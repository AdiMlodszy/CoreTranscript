# 🎙️ CoreTranscript

**Lokalny system transkrypcji i diaryzacji (rozpoznawania mówców) zoptymalizowany dla Apple Silicon.**

CoreTranscript to narzędzie łączące siłę modelu **Whisper** (w wersji MLX dla macOS) oraz **Pyannote** (do diaryzacji), opakowane w nowoczesną architekturę (Clean Architecture). Pozwala na nagrywanie, transkrypcję i analizę spotkań w pełni lokalnie, bez przesyłania danych do chmury.

## 🚀 Możliwości

* **Transkrypcja (ASR):** Błyskawiczna zamiana mowy na tekst dzięki `mlx-whisper`.
* **Diaryzacja:** Rozpoznawanie "kto mówi i kiedy" dzięki `pyannote.audio 3.1`.
* **Interfejs UI:** Prosty panel w przeglądarce (Streamlit) do nagrywania, wgrywania plików i podglądu czatu.
* **API:** Wystawione endpointy (FastAPI) gotowe do integracji z automatyzacjami (n8n, Make).
* **Prywatność:** Wszystko działa na Twoim sprzęcie (Local First).

---

## 🛠️ Wymagania

* **System:** macOS (Zalecany procesor Apple Silicon M1/M2/M3 dla akceleracji sprzętowej).
* **Python:** Wersja 3.10 lub 3.11.
* **Konto Hugging Face:** Niezbędne do pobrania modelu Pyannote (wymaga akceptacji licencji).

### 🔑 Krok 0: Przygotowanie Tokena HF
Model `pyannote/speaker-diarization-3.1` jest modelem zamkniętym. Aby go użyć:

1.  Zaloguj się na [Hugging Face](https://huggingface.co/).
2.  Zaakceptuj warunki licencji na stronach obu modeli:
    * [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
    * [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3.  Wygeneruj token dostępu (Settings -> Access Tokens) z uprawnieniami **Read**.
4.  Zachowaj token – będzie potrzebny w pliku `.env`.

---

## 📦 Instalacja

### 1. Klonowanie repozytorium
```bash
git clone [https://github.com/AdiMlodszy/CoreTranscript.git](https://github.com/AdiMlodszy/CoreTranscript.git)
cd CoreTranscript