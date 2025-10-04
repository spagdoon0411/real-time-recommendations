# Testing Instructor Integration

This directory contains test scripts to verify the Instructor integration with Vertex AI and Pydantic.

## Prerequisites

1. **Set up environment variables:**
   
   **Option A: Using .env file (Recommended)**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your actual values
   nano .env
   ```
   
   **Option B: Using environment variables**
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1  # optional, defaults to us-central1
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

## Environment Configuration

The project uses `python-dotenv` to load environment variables from a `.env` file. 

### .env File Format

Create a `.env` file in the project root with the following content:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Override default settings
# CLEAN_INTERVAL_SECONDS=5
# GEMINI_MODEL=gemini-2.5-flash
```

### Available Environment Variables

- `GOOGLE_CLOUD_PROJECT` (required): Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` (optional): Google Cloud region (default: us-central1)
- `CLEAN_INTERVAL_SECONDS` (optional): Transcript cleaning interval (default: 5)
- `GEMINI_MODEL` (optional): Gemini model to use (default: gemini-2.5-flash)

## Test Scripts

### 1. `test_instructor_integration.py` - Comprehensive Test Suite

This script runs multiple tests to verify the Instructor integration:

- **Test 1**: Basic Instructor call with a simple transcript
- **Test 2**: Ongoing conversation (topic not finished)
- **Test 3**: Finished conversation (topic finished)
- **Test 4**: Full TranscriptBuffer integration
- **Test 5**: Error handling

**Run the test suite:**
```bash
python test_instructor_integration.py
```

**Expected output:**
```
🧪 Testing Instructor Integration with Vertex AI
================================================================================
✅ Using project: your-project-id
✅ Location: us-central1

================================================================================
TEST 1: Basic Instructor Call
================================================================================
...
🏁 TEST RESULTS: 5/5 tests passed
================================================================================
🎉 All tests passed! Instructor integration is working correctly.
```

### 2. `example_usage.py` - Usage Example

This script demonstrates how to use the TranscriptBuffer in a real scenario:

**Run the example:**
```bash
python example_usage.py
```

**Expected output:**
```
🎤 TranscriptBuffer with Instructor Integration Example
============================================================
Adding conversation parts...
  Speaker1: So, um, I think we should discuss the budget for this project.
  Speaker2: Yeah, that's a good point. What do you think the budget should be?
  ...
📊 Results:
============================================================
Full raw transcript:
Speaker1So, um, I think we should discuss the budget for this project.
Speaker2Yeah, that's a good point. What do you think the budget should be?
...

Cleaned transcript:
Speaker1: So, I think we should discuss the budget for this project.
Speaker2: That's a good point. What do you think the budget should be?
...

Topic finished: True
Is topic finished: True
============================================================
✅ Example completed!
```

## What the Tests Verify

1. **Structured Output**: Ensures Instructor returns properly structured `TranscriptCleaningResponse` objects
2. **Type Safety**: Verifies Pydantic validation works correctly
3. **Topic Detection**: Tests the AI's ability to determine if conversations have concluded
4. **Error Handling**: Ensures graceful fallback when errors occur
5. **Integration**: Verifies the full TranscriptBuffer workflow works with Instructor

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure you're authenticated with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

2. **Project Not Set**: Ensure `GOOGLE_CLOUD_PROJECT` is set:
   ```bash
   echo $GOOGLE_CLOUD_PROJECT
   ```

3. **Import Errors**: Make sure the virtual environment is activated and dependencies are installed:
   ```bash
   source venv/bin/activate
   pip list | grep instructor
   ```

### Debug Mode

To see more detailed output, you can modify the test scripts to include debug information or run them with Python's verbose mode:

```bash
python -v test_instructor_integration.py
```

## Expected Behavior

- **Cleaned Transcript**: Should remove filler words, fix grammar, and improve readability
- **Topic Finished**: Should be `True` when conversations reach natural conclusions
- **Type Safety**: All responses should be `TranscriptCleaningResponse` instances
- **Error Handling**: Should gracefully handle errors and provide fallback responses
