# File: src/infrastructure/audio_io.py

import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
from typing import Optional, List, Tuple

class AudioIOManager:
    """
    Wrapper dla operacji Audio I/O (Nagrywanie, Zapis do pliku WAV).
    Używa sounddevice do nagrywania i scipy do zapisu.
    """
    
    # Stała: 16kHz jest standardem dla modeli Whisper i Pyannote
    SAMPLE_RATE = 16000 

    def __init__(self, channels: int = 1, dtype: str = 'int16'):
        """
        :param channels: 1 dla mono (wymagane przez większość modeli ASR).
        :param dtype: int16 to standardowa głębia bitowa dla WAV.
        """
        self.channels = channels
        self.dtype = dtype

    def record_audio(self, duration_seconds: int, device_index: Optional[int] = None) -> np.ndarray:
        """
        Blokujące nagrywanie dźwięku z mikrofonu.
        """
        print(f"-> [AudioIO] Start nagrywania: {duration_seconds}s (SR: {self.SAMPLE_RATE} Hz)")
        
        # sd.rec nagrywa w tle, zwraca tablicę numpy
        recording = sd.rec(
            int(duration_seconds * self.SAMPLE_RATE), 
            samplerate=self.SAMPLE_RATE, 
            channels=self.channels, 
            dtype=self.dtype,
            device=device_index
        )
        
        sd.wait()  # Czekamy aż skończy nagrywać
        print("-> [AudioIO] Koniec nagrywania.")
        
        # Spłaszczamy tablicę (N, 1) -> (N,) bo scipy/whisper wolą płaskie wektory mono
        return recording.flatten()

    def save_to_wav(self, audio_data: np.ndarray, file_path: str) -> str:
        """
        Zrzuca surowe dane numpy do pliku .wav
        """
        try:
            # Upewnij się, że katalog istnieje
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            write(file_path, self.SAMPLE_RATE, audio_data)
            print(f"-> [AudioIO] Zapisano plik: {file_path}")
            return os.path.abspath(file_path)
        except Exception as e:
            print(f"!!! [AudioIO] Błąd zapisu pliku WAV: {e}")
            raise

    def get_available_devices(self) -> List[Tuple[int, str]]:
        """
        Zwraca listę mikrofonów (indeks, nazwa).
        """
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append((i, dev['name']))
        return input_devices