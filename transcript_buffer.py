import time
import hashlib
import vertexai
from pydantic import BaseModel
import instructor
import google.generativeai as genai

from config import (
    CLEAN_INTERVAL_SECONDS,
    GEMINI_MODEL,
    GEMINI_SYSTEM_PROMPT,
    PROJECT_ID,
    LOCATION,
)


class TranscriptCleaningResponse(BaseModel):
    cleaned_transcript: str
    topic_finished: bool


class TranscriptBuffer:
    def __init__(self, clean_interval_seconds=CLEAN_INTERVAL_SECONDS):
        self.buffer = []
        self.clean_interval = clean_interval_seconds
        self.last_clean_time = time.time()
        self.last_hash = None
        self.last_cleaning_result = None
        
        # Initialize Vertex AI and Instructor client
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = genai.GenerativeModel(GEMINI_MODEL)
        self.client = instructor.from_gemini(model, mode=instructor.Mode.GEMINI_JSON)


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

            cleaning_result = self.clean_transcript(raw_transcript)
            self.last_cleaning_result = cleaning_result

            print(cleaning_result.cleaned_transcript)
            print(f"\nTopic finished: {cleaning_result.topic_finished}")
            print("=" * 60 + "\n")

            self.last_hash = current_hash
        else:
            print("\n[Skipping Gemini call - buffer unchanged]\n")

        self.last_clean_time = time.time()

    def clean_transcript(self, transcript):
        try:
            # Use Instructor to get structured output
            response = self.client.create(
                response_model=TranscriptCleaningResponse,
                messages=[
                    {"role": "system", "content": GEMINI_SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
            )
            return response
            
        except Exception as e:
            print(f"Error calling Gemini with Instructor: {e}")
            # Fallback to original transcript with topic_finished=False
            return TranscriptCleaningResponse(
                cleaned_transcript=transcript,
                topic_finished=False
            )

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

    def is_topic_finished(self):
        """Check if the current topic has finished based on the last cleaning result."""
        return self.last_cleaning_result.topic_finished if self.last_cleaning_result else False

    def get_last_cleaning_result(self):
        """Get the last cleaning result, which includes both cleaned transcript and topic_finished status."""
        return self.last_cleaning_result
