#!/usr/bin/env python3
"""
Example usage of TranscriptBuffer with Instructor integration
"""

import os
import time
from dotenv import load_dotenv
from transcript_buffer import TranscriptBuffer

# Load environment variables from .env file
load_dotenv()

def example_usage():
    """Demonstrate how to use TranscriptBuffer with Instructor"""
    
    # Check environment
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("Please set GOOGLE_CLOUD_PROJECT environment variable")
        return
    
    print("🎤 TranscriptBuffer with Instructor Integration Example")
    print("=" * 60)
    
    # Create a transcript buffer
    buffer = TranscriptBuffer(clean_interval_seconds=3)  # Clean every 3 seconds
    
    # Simulate a conversation
    conversation_parts = [
        ("Speaker1", "So, um, I think we should discuss the budget for this project."),
        ("Speaker2", "Yeah, that's a good point. What do you think the budget should be?"),
        ("Speaker1", "Well, I was thinking maybe around fifty thousand dollars?"),
        ("Speaker2", "That sounds reasonable. Let's go with that then."),
        ("Speaker1", "Great! So we're all set on the budget."),
        ("Speaker2", "Perfect. Is there anything else we need to discuss?"),
        ("Speaker1", "I think that covers everything for now."),
        ("Speaker2", "Alright, thanks for the meeting everyone."),
    ]
    
    print("Adding conversation parts...")
    for speaker, text in conversation_parts:
        print(f"  {speaker}: {text}")
        buffer.add_transcript(text, speaker)
        time.sleep(0.5)  # Small delay to simulate real conversation
    
    print("\n" + "=" * 60)
    print("📊 Results:")
    print("=" * 60)
    
    # Get the full transcript
    full_transcript = buffer.get_full_transcript()
    print("Full raw transcript:")
    print(full_transcript)
    
    print("\n" + "-" * 40)
    
    # Check if we have cleaning results
    if buffer.last_cleaning_result:
        result = buffer.last_cleaning_result
        print("Cleaned transcript:")
        print(result.cleaned_transcript)
        print(f"\nTopic finished: {result.topic_finished}")
        
        # Use convenience methods
        print(f"\nIs topic finished: {buffer.is_topic_finished()}")
    else:
        print("No cleaning result yet (waiting for interval)")
    
    print("\n" + "=" * 60)
    print("✅ Example completed!")

if __name__ == "__main__":
    example_usage()
