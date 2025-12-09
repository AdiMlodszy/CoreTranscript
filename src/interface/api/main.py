from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import tempfile
import logging
from src.core.meeting_service import MeetingService
from src.domain.models.models import MeetingTranscript

load_dotenv()

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(
    title="CoreTranscript API",
    description="API do transkrypcji i diaryzacji spotkań (Whisper + Pyannote)",
    version="0.1.0"
)

# Inicjalizacja serwisu (Globalna instancja)
# W wersji PRO użylibyśmy Dependency Injection (Depends), ale na teraz to wystarczy.
# Serwis załaduje modele przy pierwszym użyciu (Lazy Loading z AIEngine).
meeting_service = MeetingService()

@app.get("/")
def health_check():
    """Szybki test czy API żyje."""
    return {"status": "ok", "message": "CoreTranscript is ready to listen."}

@app.post("/transcribe", response_model=MeetingTranscript)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint przyjmujący plik audio (WAV/MP3).
    Zwraca pełny transkrypt z podziałem na mówców.
    """
    logger.info(f"Otrzymano żądanie transkrypcji pliku: {file.filename}")
    
    # Tworzymy plik tymczasowy, bo nasze modele wymagają ścieżki do pliku na dysku
    # Używamy delete=False, żeby plik nie zniknął zanim AIEngine go przeczyta.
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
    
    try:
        logger.info(f"Plik zapisany tymczasowo jako: {temp_path}")
        
        # Delegacja do Core (MeetingService)
        # To jest operacja blokująca (synchroniczna), więc w FastAPI domyślnie
        # uruchomi się w osobnym wątku (threadpool), nie blokując całego serwera.
        result = meeting_service.process_meeting(temp_path)
        
        return result

    except Exception as e:
        logger.error(f"Błąd przetwarzania: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Sprzątanie: zawsze usuwamy plik tymczasowy, nawet jak wystąpi błąd
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Usunięto plik tymczasowy: {temp_path}")