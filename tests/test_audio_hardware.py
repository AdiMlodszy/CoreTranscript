import sys
import os
import numpy as np

# --- PATH PATCHING ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from src.infrastructure.audio_io import AudioIOManager

def run_test():
    print(f"--- [TEST] Interaktywny test Audio I/O ---")
    
    try:
        manager = AudioIOManager()
        
        # 1. Wybór urządzenia
        print("\n=== KROK 1: Wybór Mikrofonu ===")
        devices = manager.get_available_devices()
        
        if not devices:
            print("!!! BŁĄD: Brak urządzeń wejściowych.")
            return

        print(f"{'ID':<5} | {'Nazwa Urządzenia'}")
        print("-" * 40)
        for idx, name in devices:
            print(f"{idx:<5} | {name}")
        
        print("-" * 40)
        user_input = input("Podaj ID urządzenia (lub wciśnij ENTER dla domyślnego): ").strip()
        
        selected_device_index = int(user_input) if user_input.isdigit() else None
        
        if selected_device_index is not None:
             # Walidacja czy ID jest na liście
            valid_ids = [d[0] for d in devices]
            if selected_device_index not in valid_ids:
                print(f"!!! Błąd: ID {selected_device_index} nie istnieje.")
                return
            print(f"-> Wybrano urządzenie ID: {selected_device_index}")
        else:
            print("-> Wybrano urządzenie domyślne systemowe.")

        # 2. Nagrywanie
        print("\n=== KROK 2: Nagrywanie (30s) ===")
        print("Proszę, powiedz coś do wybranego mikrofonu...")
        # Przekazujemy wybrane ID do managera
        audio_data = manager.record_audio(duration_seconds=30, device_index=selected_device_index)
        
        print(f"   Nagrano próbek: {len(audio_data)}")
        
        # 3. Weryfikacja sygnału
        if np.all(audio_data == 0):
            print("!!! OSTRZEŻENIE: Wykryto absolutną ciszę (same zera).")
            print("    Sprawdź czy wybrałeś właściwy mikrofon i czy Terminal ma uprawnienia!")
        else:
            peak = np.max(np.abs(audio_data))
            print(f"   Sygnał wykryty. Max amplituda: {peak:.4f}")
        # 4. Zapis
        output_file = os.path.join(current_dir, "test_mic_selection.wav")
        manager.save_to_wav(audio_data, output_file)
        print(f"\n-> Zapisano nagranie testowe: {output_file}")

    except Exception as e:
        print(f"\n!!! BŁĄD KRYTYCZNY: {e}")

if __name__ == "__main__":
    run_test()