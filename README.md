Oto pełna treść pliku README.md. Skopiuj poniższy tekst od pierwszej do ostatniej linii i zapisz jako README.md.

🎙️ CoreTranscript
Lokalny system transkrypcji i diaryzacji (rozpoznawania mówców) zoptymalizowany dla Apple Silicon.

CoreTranscript to narzędzie łączące siłę modelu Whisper (w wersji MLX dla macOS) oraz Pyannote (do diaryzacji), opakowane w nowoczesną architekturę (Clean Architecture). Pozwala na nagrywanie, transkrypcję i analizę spotkań w pełni lokalnie, bez przesyłania danych do chmury.

🚀 Możliwości
Transkrypcja (ASR): Błyskawiczna zamiana mowy na tekst dzięki mlx-whisper.

Diaryzacja: Rozpoznawanie "kto mówi i kiedy" dzięki pyannote.audio 3.1.

Nagrywanie w aplikacji: Możliwość nagrywania audio bezpośrednio przez przeglądarkę.

Interfejs UI: Prosty panel (Streamlit) do obsługi procesu i podglądu czatu.

API: Wystawione endpointy (FastAPI) gotowe do integracji z automatyzacjami (n8n, Make).

Prywatność: Wszystko działa na Twoim sprzęcie (Local First).

🛠️ Wymagania
System: macOS (Zalecany procesor Apple Silicon M1/M2/M3 dla akceleracji sprzętowej).

Python: Wersja 3.10 lub 3.11.

Konto Hugging Face: Niezbędne do pobrania modelu Pyannote (wymaga akceptacji licencji).

🔑 Krok 0: Przygotowanie Tokena HF
Model pyannote/speaker-diarization-3.1 jest modelem zamkniętym. Aby go użyć:

Zaloguj się na Hugging Face.

Zaakceptuj warunki licencji na stronach obu modeli:

pyannote/speaker-diarization-3.1

pyannote/segmentation-3.0

Wygeneruj token dostępu (Settings -> Access Tokens) z uprawnieniami Read.

Zachowaj token – będzie potrzebny w pliku .env.

📦 Instalacja
1. Klonowanie repozytorium
Bash

git clone https://github.com/AdiMlodszy/CoreTranscript.git
cd CoreTranscript
2. Utworzenie środowiska wirtualnego
Bash

python3 -m venv venv
source venv/bin/activate
3. Instalacja zależności
Ważne: Projekt wymaga konkretnych wersji bibliotek, aby uniknąć konfliktów między Pyannote a HuggingFace Hub.

Bash

pip install -r requirements.txt
4. Konfiguracja środowiska (.env)
Utwórz plik .env w głównym katalogu projektu:

Bash

touch .env
Otwórz go i wklej swój token:

Ini, TOML

HF_TOKEN=twoj_token_z_hugging_face_tutaj
▶️ Uruchomienie
Projekt oferuje dwa tryby pracy: Interfejs Graficzny (dla ludzi) oraz API (dla systemów).

Opcja A: Interfejs Graficzny (Streamlit)
Najlepszy sposób na start. Pozwala nagrywać audio prosto z przeglądarki lub wgrywać gotowe pliki.

Bash

PYTHONPATH=. streamlit run src/interface/ui/main_ui.py
Aplikacja otworzy się pod adresem: http://localhost:8501

Opcja B: Backend API (FastAPI)
Uruchamia serwer REST API, który przyjmuje pliki na endpoincie /transcribe.

Bash

uvicorn src.interface.api.main:app --reload
Dokumentacja API (Swagger) dostępna pod adresem: http://127.0.0.1:8000/docs

📂 Struktura Projektu
Projekt oparty jest o zasady Clean Architecture:

src/core/ - Logika biznesowa (łączenie transkrypcji z diaryzacją, serwisy).

src/domain/ - Modele danych (Pydantic).

src/infrastructure/ - Obsługa "ciężkiego sprzętu" (ładowanie modeli MLX i Pyannote).

src/interface/ - Warstwa prezentacji (API oraz UI).

tests/ - Testy jednostkowe i integracyjne.

⚠️ Znane problemy i Rozwiązania
Błąd: huggingface_hub_download() got an unexpected keyword argument 'use_auth_token'

Jeśli zobaczysz ten błąd, oznacza to, że Twoje środowisko zaktualizowało bibliotekę huggingface_hub do wersji niekompatybilnej z Pyannote 3.1. Należy wykonać downgrade biblioteki:

Bash

pip uninstall huggingface_hub -y
pip install "huggingface_hub==0.24.7"
Błąd: AttributeError: module 'streamlit' has no attribute 'audio_input'

Oznacza to, że masz starą wersję Streamlit. Należy zaktualizować bibliotekę:

Bash

pip install "streamlit>=1.40.0"
