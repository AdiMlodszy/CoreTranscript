import sys
import os

# Fix na ścieżki (żeby widział src, bo odpalamy z poziomu ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import streamlit as st
print(f"👀 WERSJA STREAMLIT W RUNTIME: {st.__version__}")
import tempfile
import logging
from dotenv import load_dotenv
from src.core.meeting_service import MeetingService

# Konfiguracja strony
st.set_page_config(
    page_title="CoreTranscript AI",
    page_icon="🎙️",
    layout="centered"
)

# Style CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .stAudio {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    load_dotenv()
    
    st.title("🎙️ CoreTranscript AI")
    st.caption("Whisper (ASR) + Pyannote (Diarization) on Apple Silicon")

    # --- 1. INICJALIZACJA MODELI (CACHE) ---
    @st.cache_resource
    def get_meeting_service():
        return MeetingService()

    try:
        service = get_meeting_service()
        # Wyświetlamy status tylko w expanderze, żeby nie śmiecić
        with st.expander("Status Systemu", expanded=False):
            st.success("Silnik AI (Whisper + Pyannote) załadowany i gotowy.")
    except Exception as e:
        st.error(f"Krytyczny błąd silnika AI: {e}")
        st.stop()

    # --- 2. INPUT DANYCH (ZAKŁADKI) ---
    # To jest ten moment! Wybierasz czy wgrywasz plik, czy nagrywasz.
    tab1, tab2 = st.tabs(["📁 Wgraj Plik", "🎤 Nagraj Audio"])

    audio_source = None
    source_name = "recording.wav"

    # Opcja A: Upload pliku
    with tab1:
        uploaded_file = st.file_uploader("Wybierz plik (WAV, MP3, M4A)", type=['wav', 'mp3', 'm4a'])
        if uploaded_file:
            audio_source = uploaded_file
            source_name = uploaded_file.name

    # Opcja B: Nagrywanie (To, czego Ci brakowało)
    with tab2:
        st.write("Naciśnij ikonę mikrofonu, aby rozpocząć nagrywanie.")
        # Widget dostępny od Streamlit 1.39.0
        audio_recording = st.audio_input("Rejestrator głosu")
        if audio_recording:
            audio_source = audio_recording
            source_name = "live_recording.wav"
            st.audio(audio_source) # Odsłuch od razu po nagraniu

    # --- 3. LOGIKA PRZETWARZANIA ---
    if audio_source is not None:
        # Przycisk aktywuje się dopiero jak mamy źródło dźwięku
        if st.button("🚀 Uruchom Transkrypcję", type="primary", use_container_width=True):
            
            with st.spinner("Przetwarzanie... (Whisper czyta, Pyannote słucha)"):
                tmp_path = None
                try:
                    # Zapisujemy strumień bajtów do pliku tymczasowego na dysku
                    suffix = f".{source_name.split('.')[-1]}" if "." in source_name else ".wav"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(audio_source.getvalue())
                        tmp_path = tmp_file.name

                    # --- CORE PROCESSING ---
                    # Tu dzieje się magia backendu
                    transcript = service.process_meeting(tmp_path)
                    
                    # --- WYNIKI ---
                    st.divider()
                    st.success(f"Gotowe! Przetworzono: {transcript.total_duration:.2f}s")

                    # Wyświetlanie czatu
                    chat_container = st.container()
                    with chat_container:
                        for segment in transcript.segments:
                            # Różne awatary dla czytelności
                            avatar = "🤖" if "SPEAKER_00" in segment.speaker else "👤"
                            if "SPEAKER_01" in segment.speaker: avatar = "🗣️"
                            
                            with st.chat_message(name=segment.speaker, avatar=avatar):
                                st.markdown(f"**{segment.speaker}** _({segment.start:.1f}s)_")
                                st.write(segment.text)
                    
                    # Pobieranie JSON
                    st.download_button(
                        label="📥 Pobierz wynik (JSON)",
                        data=transcript.model_dump_json(indent=2),
                        file_name=f"transcript_{source_name}.json",
                        mime="application/json"
                    )

                except Exception as e:
                    st.error(f"Błąd podczas przetwarzania: {e}")
                finally:
                    # Sprzątanie po sobie
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)

if __name__ == "__main__":
    main()