import time
import hashlib
import vertexai
from vertexai.generative_models import GenerativeModel

from config import (
    CLEAN_INTERVAL_SECONDS,
    GEMINI_MODEL,
    GEMINI_SYSTEM_PROMPT,
)


class TranscriptBuffer:
    def __init__(self, clean_interval_seconds=CLEAN_INTERVAL_SECONDS):
        self.buffer = []
        self.clean_interval = clean_interval_seconds
        self.last_clean_time = time.time()
        self.last_hash = None

    def add_transcript(self, text, speaker_tag=""):
        self.buffer.append(
            {"speaker": speaker_tag, "text": text, "timestamp": time.time()}
        )

        if time.time() - self.last_clean_time >= self.clean_interval:
            self._run_clean()

    def _run_clean(self):
        if not self.buffer:
            return

        raw_transcript = self.get_full_transcript()
        current_hash = hashlib.sha256(raw_transcript.encode()).hexdigest()

        if current_hash != self.last_hash:
            print("\n" + "=" * 60)
            print("CLEANING TRANSCRIPT with Gemini (buffer changed)...")
            print("-" * 60)

            cleaned = self.clean_transcript(raw_transcript)

            print(cleaned)
            print("=" * 60 + "\n")

            self.last_hash = current_hash
        else:
            print("\n[Skipping Gemini call - buffer unchanged]\n")

        self.last_clean_time = time.time()

    def clean_transcript(self, transcript):
        try:
            model = GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=GEMINI_SYSTEM_PROMPT,
            )
            response = model.generate_content(transcript)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return transcript

    def get_full_transcript(self):
        transcript_lines = []
        for entry in self.buffer:
            speaker = entry["speaker"].strip()
            text = entry["text"].strip()
            if speaker:
                transcript_lines.append(f"{speaker}{text}")
            else:
                transcript_lines.append(text)
        return "\n".join(transcript_lines)
