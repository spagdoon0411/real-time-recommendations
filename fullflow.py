from topic_manager import TopicManager

from transcript_buffer import TranscriptBuffer
from transcript_buffer_chunker import TranscriptBufferChunker


def main():

    transcript_buffer = TranscriptBuffer()
    topic_manager = TopicManager()


    transcript = [
        {"text": "Um, so I think we should, like, you know, maybe consider the budget for this project.", "speaker": "Speaker1"},
        {"text": "Yeah, that's a good point. What do you think the budget should be?", "speaker": "Speaker2"},
        {"text": "Well, I was thinking maybe around fifty thousand dollars?", "speaker": "Speaker1"},
        {"text": "That sounds reasonable. Let's go with that then.", "speaker": "Speaker2"},
        {"text": "Great! So we're all set on the budget.", "speaker": "Speaker1"},
        {"text": "I'm thinking about getting a new pet. Maybe a cat?", "speaker": "Speaker1"},
        {"text": "Cats are great! They're independent and low maintenance.", "speaker": "Speaker2"},
        {"text": "What breed would you recommend?", "speaker": "Speaker1"},
        {"text": "I'd suggest a Maine Coon or a British Shorthair. Both are friendly.", "speaker": "Speaker2"},
        {"text": "Thanks for the advice! I'll look into those breeds.", "speaker": "Speaker1"},
        {"text": "No problem! Let me know if you need help with anything else.", "speaker": "Speaker2"},
    ]


    transcript_chunker = TranscriptBufferChunker()
    for line in transcript:
        transcript_chunker.add_transcript_line(line["text"], )

    chunks = transcript_chunker.chunk_buffer(topic_manager.list_topics())

    print(chunks)

    return
    



    for line in transcript:
        transcript_buffer.add_transcript(line["text"], line["speaker"])

    cleaned_transcript = transcript_buffer.clean_transcript(transcript_buffer.get_full_transcript())
    print(cleaned_transcript.cleaned_transcript)
    print(f"Topic finished: {cleaned_transcript.topic_finished}")

    res = topic_manager.classify_chunk(cleaned_transcript.cleaned_transcript)

    print("first time", res.topic_key, res.updated_description)

    # none and summary

    if not res.topic_key:
        topic_manager.add_new_topic(res.updated_description)
    else:
        topic_manager.update_topic(res.topic_key, res.updated_description)




    second_transcript = [
        {"text": "I'm thinking about getting a new pet. Maybe a cat?", "speaker": "Speaker1"},
        {"text": "Cats are great! They're independent and low maintenance.", "speaker": "Speaker2"},
        {"text": "What breed would you recommend?", "speaker": "Speaker1"},
        {"text": "I'd suggest a Maine Coon or a British Shorthair. Both are friendly.", "speaker": "Speaker2"},
        {"text": "Thanks for the advice! I'll look into those breeds.", "speaker": "Speaker1"},
        {"text": "No problem! Let me know if you need help with anything else.", "speaker": "Speaker2"},
    ]

    transcript_buffer2 = TranscriptBuffer()
    for line in second_transcript:
        transcript_buffer2.add_transcript(line["text"], line["speaker"])

    cleaned_transcript2 = transcript_buffer2.clean_transcript(transcript_buffer2.get_full_transcript())
    print(cleaned_transcript2.cleaned_transcript)
    print(f"Topic finished: {cleaned_transcript2.topic_finished}")

    res2 = topic_manager.classify_chunk(cleaned_transcript2.cleaned_transcript)

    if not res2.topic_key:
        topic_manager.add_new_topic(res2.updated_description)
    else:
        topic_manager.update_topic(res2.topic_key, res2.updated_description)

    print(topic_manager.list_topics())





if __name__ == "__main__":
    main()