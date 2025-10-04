import vertexai
from google.cloud import speech
import sys
from config import (
    PROJECT_ID,
    LOCATION,
    MIN_SPEAKER_COUNT,
    MAX_SPEAKER_COUNT,
    RATE,
)
from topic_manager import TopicManager
from transcript_buffer_chunker import TranscriptBufferChunker
from microphone_stream import MicrophoneStream
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
)

class Transcriber:

       

    def listen_print_loop(self, responses, transcript_buffer):
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
                transcript_buffer.add_transcript_line(transcript)
                num_chars_printed = 0


    def __init__(self):
        self.topics_manager = TopicManager()
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

        transcript_buffer = TranscriptBufferChunker(topics_manager=self.topics_manager)

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

            self.listen_print_loop(responses, transcript_buffer)


if __name__ == "__main__":
    transcriber = Transcriber()
    transcriber.transcribe()