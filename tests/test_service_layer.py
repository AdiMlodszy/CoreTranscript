# File: tests/test_service_layer.py
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.meeting_service import MeetingService
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

def run_service_test():
    load_dotenv()
    
    # Magia ze ścieżką
    test_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file = os.path.join(test_dir, "test_mic_selection.wav")
    
    service = MeetingService()
    
    try:
        # Teraz wywołujemy tylko jedną, czystą metodę!
        result = service.process_meeting(audio_file)
        
        print("\n" + "="*60)
        print(f"📄 RAPORT SPOTKANIA: {result.filename}")
        print(f"⏱️  Data: {result.processed_at}")
        print(f"⏳ Czas trwania: {result.total_duration:.2f}s")
        print("="*60)
        
        for seg in result.segments:
            print(f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.speaker}: {seg.text}")
            
    except Exception as e:
        logging.error(f"Błąd: {e}")

if __name__ == "__main__":
    run_service_test()