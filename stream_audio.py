#!/usr/bin/env python3

import sys
import queue
import time
import hashlib
from google.cloud import speech
import pyaudio
import vertexai
from vertexai.generative_models import GenerativeModel

from config import (
    RATE,
    CHUNK,
    LANGUAGE_CODE,
    MIN_SPEAKER_COUNT,
    MAX_SPEAKER_COUNT,
    CLEAN_INTERVAL_SECONDS,
    PROJECT_ID,
    LOCATION,
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


class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses, transcript_buffer):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        speaker_tag = ""
        if (
            result.is_final
            and hasattr(result.alternatives[0], "words")
            and result.alternatives[0].words
        ):
            words_info = result.alternatives[0].words
            if words_info and hasattr(words_info[0], "speaker_tag"):
                speaker_tag = f"[Speaker {words_info[0].speaker_tag}] "

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print(speaker_tag + transcript + overwrite_chars)
            transcript_buffer.add_transcript(transcript, speaker_tag)
            num_chars_printed = 0


def main():
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set.")
        print("Please set it with: export GOOGLE_CLOUD_PROJECT='your-project-id'")
        sys.exit(1)

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    client = speech.SpeechClient()

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=MIN_SPEAKER_COUNT,
        max_speaker_count=MAX_SPEAKER_COUNT,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=LANGUAGE_CODE,
        diarization_config=diarization_config,
        enable_word_time_offsets=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    transcript_buffer = TranscriptBuffer(clean_interval_seconds=CLEAN_INTERVAL_SECONDS)

    print("Listening with Speaker Diarization... Press Ctrl+C to stop.")
    print(f"Detecting {MIN_SPEAKER_COUNT}-{MAX_SPEAKER_COUNT} speakers")
    print(f"Cleaning transcript with Gemini every {CLEAN_INTERVAL_SECONDS} seconds")
    print(f"Using model: {GEMINI_MODEL}")
    print("=" * 60)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses, transcript_buffer)


if __name__ == "__main__":
    main()
