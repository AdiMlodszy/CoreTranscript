# File: tests/test_full_pipeline.py

import sys
import os
import logging

# Dodajemy katalog główny do ścieżki, żeby importy działały
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.ai_engine import AIEngine
from src.core.alignment_service import AlignmentService
from dotenv import load_dotenv

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("TestPipeline")

def run_pipeline_test():
    load_dotenv()
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file = os.path.join(test_dir, "test_mic_selection.wav")
    
    if not os.path.exists(audio_file):
        logger.error(f"Brak pliku testowego: {audio_file}")
        return

    print("\n--- [START] Test Pełnego Procesu Transkrypcji ---\n")

    # 1. Inicjalizacja Silnika
    # Model small jest szybszy do testów, do produkcji użyjesz medium/large
    engine = AIEngine(asr_model="mlx-community/whisper-large-v3-turbo") 
    #   engine = AIEngine(asr_model="mlx-community/whisper-medium") 
    #   engine = AIEngine(asr_model="mlx-community/base") 

    aligner = AlignmentService()

    try:
        # 2. Transkrypcja (ASR)
        print("1. 🗣️  Rozpoczynam transkrypcję (Whisper)...")
        transcription_result = engine.transcribe(audio_file)
        print(f"   -> Sukces. Pobrano {len(transcription_result.get('segments', []))} surowych segmentów.")

        # 3. Diaryzacja (Pyannote)
        print("2. 👥 Rozpoczynam diaryzację (Pyannote)...")
        diarization_result = engine.diarize(audio_file)
        print(f"   -> Sukces. Wykryto {len(diarization_result)} zmian mówcy.")

        # 4. Łączenie (Alignment)
        print("3. 🔗 Łączenie wyników (Alignment Service)...")
        final_transcript = aligner.align(transcription_result, diarization_result)

        # 5. Wyświetlenie wyników
        print("\n" + "="*50)
        print("   REZULTAT KOŃCOWY (Speaker + Text)")
        print("="*50)
        
        for entry in final_transcript:
            start_fmt = f"{entry['start']:.1f}s"
            # Formatowanie dla czytelności
            print(f"[{start_fmt.rjust(6)}] {entry['speaker']}: {entry['text']}")

        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Błąd krytyczny pipeline'u: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_pipeline_test()