# File: tests/test_ai_diarization.py
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# --- Path Patching ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from src.infrastructure.ai_engine import AIEngine

def run_test():
    print("--- [TEST] Weryfikacja Diaryzacji (Pyannote 3.1) ---")
    
    # Używamy tego samego pliku co wcześniej
    test_file = os.path.join(current_dir, "test_mic_selection.wav")
    if not os.path.exists(test_file):
        print("!!! Brak pliku testowego. Nagraj coś przez test_audio_hardware.py")
        return

    # Inicjalizacja
    engine = AIEngine()
    
    if engine.diarization_pipeline is None:
        print("!!! TEST PRZERWANY: Pipeline nie wstał. Sprawdź logi powyżej.")
        return

    print("\n1. Rozpoczynam diaryzację...")
    start_time = time.time()
    
    try:
        # Wywołujemy nową metodę
        segments = engine.diarize(test_file)
        duration = time.time() - start_time
        
        print("-" * 40)
        print(f"WYNIK ({duration:.2f}s):")
        
        if not segments:
            print("⚠️ Brak wykrytych mówców (może nagranie jest za krótkie lub ciche?)")
        
        # Wypisujemy segmenty
        for seg in segments:
            print(f"[{seg['start']:05.2f}s - {seg['end']:05.2f}s] {seg['speaker']}")
            
        print("-" * 40)
        print("✅ SUKCES: Pyannote działa.")
            
    except Exception as e:
        print(f"!!! BŁĄD KRYTYCZNY DIARYZACJI: {e}")

if __name__ == "__main__":
    run_test()