import os
import logging
from typing import List, Dict, Any

from src.infrastructure.ai_engine import AIEngine
from src.core.alignment_service import AlignmentService
from src.domain.models.models import MeetingTranscript, TranscriptionSegment

logger = logging.getLogger(__name__)

class MeetingService:
    """
    Serwis aplikacyjny (Use Case).
    Odpowiada za przeprowadzenie pełnego procesu przetwarzania pliku audio:
    Audio -> ASR -> Diaryzacja -> Alignment -> Model Domenowy.
    """

    def __init__(self):
        # Wstrzykiwanie zależności (na razie hardcoded, później można użyć Dependency Injection)
        self.ai_engine = AIEngine()
        self.alignment_service = AlignmentService()

    def process_meeting(self, file_path: str) -> MeetingTranscript:
        """
        Przetwarza plik audio i zwraca gotowy obiekt MeetingTranscript.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Nie znaleziono pliku: {file_path}")

        logger.info(f"Rozpoczynam przetwarzanie spotkania: {file_path}")

        # 1. Pobierz surowe dane z infrastruktury
        # (Tu jest miejsce na optymalizację: można by to puścić równolegle, ale Pyannote i Whisper i tak walczą o GPU)
        raw_transcription = self.ai_engine.transcribe(file_path)
        raw_diarization = self.ai_engine.diarize(file_path)

        # 2. Wykonaj logikę biznesową (Core)
        aligned_data = self.alignment_service.align(raw_transcription, raw_diarization)

        # 3. Mapowanie na Model Domenowy (Domain)
        # Zamieniamy brudne słowniki na czyste obiekty Pydantic
        segments_models = []
        for item in aligned_data:
            segment = TranscriptionSegment(
                start=item['start'],
                end=item['end'],
                speaker=item['speaker'],
                text=item['text']
            )
            segments_models.append(segment)

        # 4. Budowa finalnego obiektu
        transcript = MeetingTranscript(
            filename=os.path.basename(file_path),
            segments=segments_models
        )

        logger.info(f"Przetwarzanie zakończone. Utworzono transkrypt z {len(segments_models)} segmentami.")
        return transcript