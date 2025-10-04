#!/usr/bin/env python3

import sys
import queue
import time
from google.cloud import speech
import pyaudio

RATE = 16000
CHUNK = int(RATE / 10)


class TranscriptBuffer:
    def __init__(self, clean_interval_seconds=5):
        self.buffer = []
        self.clean_interval = clean_interval_seconds
        self.last_clean_time = time.time()

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
        cleaned = self.clean_transcript(raw_transcript)

        print(f"\n{'=' * 60}")
        print(f"CLEANED TRANSCRIPT (every {self.clean_interval}s):")
        print(f"{'-' * 60}")
        print(cleaned)
        print(f"{'=' * 60}\n")

        self.last_clean_time = time.time()

    def clean_transcript(self, transcript):
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
    language_code = "en-US"
    clean_interval_seconds = 5

    client = speech.SpeechClient()

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=6,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        diarization_config=diarization_config,
        enable_word_time_offsets=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    transcript_buffer = TranscriptBuffer(clean_interval_seconds=clean_interval_seconds)

    print("Listening with Speaker Diarization... Press Ctrl+C to stop.")
    print("Detecting 2-6 speakers")
    print(f"Cleaning transcript every {clean_interval_seconds} seconds")
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
