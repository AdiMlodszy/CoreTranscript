# File: src/core/services/alignment_service.py

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AlignmentService:
    """
    Serwis odpowiedzialny za logikę łączenia transkrypcji (słowa) z diaryzacją (segmenty czasowe).
    Nie zależy od konkretnej implementacji AI, operuje na czystych danych.
    """

    def align(self, transcription: Dict[str, Any], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Główna metoda łącząca.
        :param transcription: Wynik z Whispera (musi zawierać word_timestamps).
        :param segments: Wynik z Pyannote (lista segmentów z 'speaker').
        :return: Lista obiektów {'speaker': str, 'text': str, 'start': float, 'end': float}.
        """
        if not transcription or not segments:
            logger.warning("Puste dane wejściowe do alignowania.")
            return []

        # 1. Ekstrakcja wszystkich słów
        words = self._extract_words(transcription)
        if not words:
            logger.warning("Transkrypcja nie zawiera słów (sprawdź czy word_timestamps=True).")
            return []

        # 2. Przypisanie mówcy do każdego słowa
        aligned_words = self._assign_speakers_to_words(words, segments)

        # 3. Grupowanie słów z powrotem w pełne wypowiedzi
        return self._group_words_by_speaker(aligned_words)

    def _extract_words(self, transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Spłaszcza strukturę Whispera do prostej listy słów."""
        words = []
        # Obsługa struktury MLX Whisper / Standard Whisper
        for segment in transcription.get('segments', []):
            words.extend(segment.get('words', []))
        return words

    def _assign_speakers_to_words(self, words: List[Dict[str, Any]], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przypisuje etykietę mówcy do każdego słowa na podstawie czasu."""
        aligned_output = []
        current_speaker_idx = 0
        
        # Sortowanie segmentów jest kluczowe dla optymalizacji, zakładamy że przychodzą posortowane
        # ale dla pewności:
        segments = sorted(segments, key=lambda x: x['start'])

        for word in words:
            word_start, word_end = word['start'], word['end']
            word_text = word['word']
            assigned_speaker = "UNKNOWN"
            
            # Przeszukujemy segmenty diaryzacji (z optymalizacją indeksu startowego)
            for i in range(current_speaker_idx, len(segments)):
                seg = segments[i]
                
                # Margines błędu 0.5s (ludzie często zaczynają mówić minimalnie przed/po wykryciu)
                if (word_start >= seg['start'] - 0.5) and (word_start <= seg['end'] + 0.5):
                    assigned_speaker = seg['speaker']
                    current_speaker_idx = i # Nie cofamy się w liście segmentów
                    break
            
            aligned_output.append({
                "word": word_text.strip(),
                "start": word_start,
                "end": word_end,
                "speaker": assigned_speaker
            })
        return aligned_output

    def _group_words_by_speaker(self, aligned_words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Grupuje ciąg słów tego samego mówcy w jedną wypowiedź."""
        if not aligned_words: return []
        
        grouped = []
        current_entry = {
            "speaker": aligned_words[0]['speaker'],
            "text": aligned_words[0]['word'],
            "start": aligned_words[0]['start'],
            "end": aligned_words[0]['end']
        }

        for word in aligned_words[1:]:
            if word['speaker'] == current_entry['speaker']:
                # Kontynuacja wypowiedzi tego samego mówcy
                current_entry['text'] += " " + word['word']
                current_entry['end'] = word['end']
            else:
                # Zmiana mówcy - zapisujemy obecną i zaczynamy nową
                grouped.append(current_entry)
                current_entry = {
                    "speaker": word['speaker'],
                    "text": word['word'],
                    "start": word['start'],
                    "end": word['end']
                }
        
        # Dodajemy ostatni wpis
        grouped.append(current_entry)
        return grouped