#!/usr/bin/env python3
"""
Test script for Instructor integration with Vertex AI and TranscriptBuffer
"""

import os
import sys
from dotenv import load_dotenv
from transcript_buffer import TranscriptBuffer, TranscriptCleaningResponse

# Load environment variables from .env file
load_dotenv()



def test_basic_instructor_call():
    """Test basic Instructor call with a simple transcript"""
    print("=" * 80)
    print("TEST 1: Basic Instructor Call")
    print("=" * 80)
    
    try:
        # Create a transcript buffer
        buffer = TranscriptBuffer()
        
        # Simple test transcript
        test_transcript = """
        Speaker1: Um, so I think we should, like, you know, maybe consider the budget for this project.
        Speaker2: Yeah, that's a good point. What do you think the budget should be?
        Speaker1: Well, I was thinking maybe around fifty thousand dollars?
        Speaker2: That sounds reasonable. Let's go with that then.
        Speaker1: Great! So we're all set on the budget.
        """
        
        print("Input transcript:")
        print(test_transcript.strip())
        print("\n" + "-" * 60)
        
        # Test the cleaning function
        result = buffer.clean_transcript(test_transcript)
        
        print("✅ Instructor call successful!")
        print(f"✅ Response type: {type(result)}")
        print(f"✅ Is TranscriptCleaningResponse: {isinstance(result, TranscriptCleaningResponse)}")
        
        print("\nCleaned transcript:")
        print(result.cleaned_transcript)
        print(f"\nTopic finished: {result.topic_finished}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ongoing_conversation():
    """Test with an ongoing conversation (topic not finished)"""
    print("\n" + "=" * 80)
    print("TEST 2: Ongoing Conversation (Topic Not Finished)")
    print("=" * 80)
    
    try:
        buffer = TranscriptBuffer()
        
        ongoing_transcript = """
        Speaker1: I'm not sure about this approach. What do you think?
        Speaker2: Well, there are pros and cons to consider.
        Speaker1: Like what?
        Speaker2: On one hand, it's faster, but on the other hand...
        """
        
        print("Input transcript:")
        print(ongoing_transcript.strip())
        print("\n" + "-" * 60)
        
        result = buffer.clean_transcript(ongoing_transcript)
        
        print("✅ Instructor call successful!")
        print("\nCleaned transcript:")
        print(result.cleaned_transcript)
        print(f"\nTopic finished: {result.topic_finished}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_finished_conversation():
    """Test with a finished conversation"""
    print("\n" + "=" * 80)
    print("TEST 3: Finished Conversation (Topic Finished)")
    print("=" * 80)
    
    try:
        buffer = TranscriptBuffer()
        
        finished_transcript = """
        Speaker1: So we've decided to go with the cloud solution.
        Speaker2: Yes, that's the best option for our needs.
        Speaker1: Perfect. I'll start working on the implementation next week.
        Speaker2: Great! Let me know if you need any help.
        Speaker1: Will do. Thanks for the discussion.
        """
        
        print("Input transcript:")
        print(finished_transcript.strip())
        print("\n" + "-" * 60)
        
        result = buffer.clean_transcript(finished_transcript)
        
        print("✅ Instructor call successful!")
        print("\nCleaned transcript:")
        print(result.cleaned_transcript)
        print(f"\nTopic finished: {result.topic_finished}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transcript_buffer_integration():
    """Test the full TranscriptBuffer integration"""
    print("\n" + "=" * 80)
    print("TEST 4: Full TranscriptBuffer Integration")
    print("=" * 80)
    
    try:
        buffer = TranscriptBuffer(clean_interval_seconds=1)  # Short interval for testing
        
        # Simulate adding transcript pieces
        print("Adding transcript pieces...")
        buffer.add_transcript("So, um, I think we should discuss the budget.", "Speaker1")
        buffer.add_transcript("Yeah, that's a good idea. What's your estimate?", "Speaker2")
        buffer.add_transcript("I was thinking around fifty thousand dollars.", "Speaker1")
        buffer.add_transcript("That sounds reasonable to me.", "Speaker2")
        buffer.add_transcript("Great! Let's finalize that then.", "Speaker1")
        
        print("✅ Transcript pieces added successfully!")
        
        # Check if we have a cleaning result
        if buffer.last_cleaning_result:
            result = buffer.last_cleaning_result
            print(f"✅ Cleaning result available: {type(result)}")
            print("\nCleaned transcript:")
            print(result.cleaned_transcript)
            print(f"\nTopic finished: {result.topic_finished}")
            
            # Test convenience methods
            print(f"\nIs topic finished (method): {buffer.is_topic_finished()}")
            print(f"Last cleaning result (method): {type(buffer.get_last_cleaning_result())}")
        else:
            print("⚠️  No cleaning result yet (may need to wait for interval)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling with invalid input"""
    print("\n" + "=" * 80)
    print("TEST 5: Error Handling")
    print("=" * 80)
    
    try:
        buffer = TranscriptBuffer()
        
        # Test with empty transcript
        result = buffer.clean_transcript("")
        
        print("✅ Empty transcript handled successfully!")
        print(f"✅ Response type: {type(result)}")
        print(f"✅ Cleaned transcript: '{result.cleaned_transcript}'")
        print(f"✅ Topic finished: {result.topic_finished}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Instructor Integration with Vertex AI")
    print("=" * 80)
    
    # Check environment
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set!")
        print("Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
        sys.exit(1)
    
    print(f"✅ Using project: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"✅ Location: {os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')}")
    
    # Run tests
    tests = [
        test_basic_instructor_call,
        test_ongoing_conversation,
        test_finished_conversation,
        test_transcript_buffer_integration,
        test_error_handling,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 80)
    print(f"🏁 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("🎉 All tests passed! Instructor integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
