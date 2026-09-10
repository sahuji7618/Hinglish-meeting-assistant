from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from pydub import AudioSegment
import os
import requests

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25

GROQ_MAX_BYTES = 20 * 1024 * 1024  # 20 MB safety threshold (Groq limit is 25 MB)
WHISPER_SUBCHUNK_MS = 10 * 60 * 1000  # 10 minutes per piece in milliseconds

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

def _send_to_whisper(piece_path: str) -> str:
    """Send a single file (<20MB) to Groq Whisper API."""
    with open(piece_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
        )
    return transcript.text 

def transcribe_chunk_whisper(chunk_path: str) -> str:
    """Transcribe chunk using Groq Whisper.

    If file > 20MB, slice into smaller pieces before sending.
    """
    # 1. If file is within safe limits, send directly
    if os.path.getsize(chunk_path) <= GROQ_MAX_BYTES:
        return _send_to_whisper(chunk_path)

    print(
        f"  ⚡ Chunk {os.path.basename(chunk_path)} exceeds 20MB limit. Splitting for Groq..."
    )

    # 2. Slice large audio into 10-minute MP3 pieces
    audio = AudioSegment.from_file(chunk_path)
    full_text = ""
    total_pieces = (len(audio) + WHISPER_SUBCHUNK_MS - 1) // WHISPER_SUBCHUNK_MS

    for i, start in enumerate(range(0, len(audio), WHISPER_SUBCHUNK_MS)):
        piece = audio[start : start + WHISPER_SUBCHUNK_MS]
        piece_path = f"{chunk_path}_groq_{i}.mp3"
        piece.export(piece_path, format="mp3", bitrate="64k")

        try:
            print(f"  → Groq Whisper piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_whisper(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")

def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   



def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → groq Whisper 
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  