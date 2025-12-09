# File: tests/test_ai_transcription.py
import sys
import os
import time
from dotenv import load_dotenv

# 1. Ładujemy zmienne z pliku .env (musisz mieć plik .env z HF_TOKEN=...)
load_dotenv()

# --- Path Patching ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from src.infrastructure.ai_engine import AIEngine

def run_test():
    print("--- [TEST] Weryfikacja MLX Whisper (Oczekiwany model: MEDIUM) ---")
    
    # Weryfikacja tokena (dla pewności przed diaryzacją)
    token = os.getenv("HF_TOKEN")
    if token:
        print(f"-> HF_TOKEN wykryty: {token[:4]}...***")
    else:
        print("!!! OSTRZEŻENIE: Brak HF_TOKEN w .env. Diaryzacja później nie zadziała!")

    # 1. Ścieżka do pliku testowego
    test_file = os.path.join(current_dir, "test_mic_selection.wav")
    if not os.path.exists(test_file):
        print(f"!!! BŁĄD: Brak pliku {test_file}. Nagraj coś najpierw (test_audio_hardware.py).")
        return

    # 2. Inicjalizacja silnika BEZ ARGUMENTÓW
    # Dzięki temu weźmie domyślną wartość z src/infrastructure/ai_engine.py (czyli Medium)
    print("-> Inicjalizacja AIEngine...")
    engine = AIEngine() 
    
    # Safety check - upewniamy się, co Python załadował
    if "tiny" in engine.model_path:
        print("!!! BŁĄD KONFIGURACJI: Silnik nadal wskazuje na TINY. Sprawdź src/infrastructure/ai_engine.py!")
        return

    print(f"\n1. Pobieranie/Ładowanie modelu '{engine.model_path}'...")
    print("   (To wersja MEDIUM - waży ok. 1.5GB, więc teraz chwilę to potrwa)")
    
    start_time = time.time()
    
    try:
        result = engine.transcribe(test_file)
        duration = time.time() - start_time
        
        print("-" * 40)
        print(f"WYNIK ({duration:.2f}s):")
        print(f"'{result['text'].strip()}'")
        print("-" * 40)
        
        if result['text']:
            print("✅ SUKCES: Transkrypcja gotowa.")
        else:
            print("⚠️ OSTRZEŻENIE: Pusty wynik.")
            
    except Exception as e:
        print(f"!!! BŁĄD KRYTYCZNY MLX: {e}")

if __name__ == "__main__":
    run_test()