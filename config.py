import os

RATE = 16000
CHUNK = int(RATE / 10)

LANGUAGE_CODE = "en-US"

MIN_SPEAKER_COUNT = 2
MAX_SPEAKER_COUNT = 6

CLEAN_INTERVAL_SECONDS = 5

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_SYSTEM_PROMPT = """You are a transcript cleaning assistant. 
Your task is to clean and format the provided transcript by:
- Removing filler words (um, uh, like, you know, etc.)
- Fixing grammar and punctuation
- Maintaining speaker labels
- Keeping the original meaning intact
- Making it more readable while staying faithful to the content

Return only the cleaned transcript without any additional commentary."""
