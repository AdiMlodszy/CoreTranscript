import mlx_whisper
import torch
from pyannote.audio import Pipeline
import os
import logging
from typing import Dict, Any, List, Optional

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEngine:
    """
    Fasada infrastrukturalna dla silników AI (ASR + Diaryzacja).
    Odpowiedzialność: Tylko i wyłącznie interakcja z modelami ML.
    """

    def __init__(self, asr_model: str = "mlx-community/whisper-large-v3-turbo"):
        self.asr_model_path = asr_model
        self.hf_token = os.getenv("HF_TOKEN")
        self._diarization_pipeline: Optional[Pipeline] = None
        
        logger.info(f"Zainicjowano AIEngine. Model ASR: {self.asr_model_path}")

    @property
    def diarization_pipeline(self) -> Pipeline:
        if self._diarization_pipeline is None:
            logger.info("Ładowanie modelu Pyannote (Lazy Load)...")
            if not self.hf_token:
                logger.warning("Brak HF_TOKEN! Diaryzacja modelu zamkniętego się nie uda.")

            try:
                # Wymaga: pip install "huggingface_hub<0.25.0"
                pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.hf_token
                )
                
                if torch.backends.mps.is_available():
                    device = torch.device("mps")
                    pipeline.to(device)
                    logger.info("Pyannote załadowano na: MPS (Apple GPU) 🚀")
                else:
                    pipeline.to(torch.device("cpu"))
                    logger.info("Pyannote załadowano na: CPU 🐢")
                
                self._diarization_pipeline = pipeline
            except Exception as e:
                logger.error(f"Krytyczny błąd ładowania Pyannote: {e}")
                raise RuntimeError("Błąd ładowania modelu diaryzacji.") from e
        
        return self._diarization_pipeline

    def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """Zwraca surowy wynik z Whispera."""
        self._validate_file(audio_file_path)
        logger.info(f"Start ASR: {os.path.basename(audio_file_path)}")
        try:
            return mlx_whisper.transcribe(
                audio_file_path, 
                path_or_hf_repo=self.asr_model_path,
                word_timestamps=True
            )
        except Exception as e:
            logger.error(f"Błąd transkrypcji: {e}")
            raise

    def diarize(self, audio_file_path: str) -> List[Dict[str, Any]]:
        """Zwraca surowe segmenty czasowe mówców."""
        self._validate_file(audio_file_path)
        logger.info(f"Start Diaryzacji: {os.path.basename(audio_file_path)}")
        
        pipeline = self.diarization_pipeline
        try:
            diarization = pipeline(audio_file_path)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            logger.info(f"Znaleziono {len(segments)} segmentów mówców.")
            return segments
        except Exception as e:
            logger.error(f"Błąd diaryzacji: {e}")
            raise

    def _validate_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Nie znaleziono pliku: {path}")