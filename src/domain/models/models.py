from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TranscriptionSegment(BaseModel):
    """
    Pojedynczy fragment wypowiedzi przypisany do konkretnego mówcy.
    """
    start: float = Field(..., description="Czas rozpoczęcia w sekundach")
    end: float = Field(..., description="Czas zakończenia w sekundach")
    speaker: str = Field(..., description="Identyfikator mówcy (np. SPEAKER_01)")
    text: str = Field(..., description="Treść wypowiedzi")

    @property
    def duration(self) -> float:
        return self.end - self.start

class MeetingTranscript(BaseModel):
    """
    Pełny zapis spotkania zawierający metadane i listę wypowiedzi.
    """
    filename: str
    processed_at: datetime = Field(default_factory=datetime.now)
    segments: List[TranscriptionSegment]
    
    # Opcjonalnie: miejsce na podsumowanie AI, które dodamy w przyszłości
    summary: Optional[str] = None 

    @property
    def total_duration(self) -> float:
        if not self.segments:
            return 0.0
        return self.segments[-1].end