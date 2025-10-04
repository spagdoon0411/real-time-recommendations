# Real-Time Speech Recognition

A real-time speech-to-text streaming application using Google Cloud Speech-to-Text API.

## Prerequisites

1. **Google Cloud Account**: Create a project and enable the Speech-to-Text API
2. **Authentication**: Set up Application Default Credentials

## Setup

### 1. Install PortAudio (required for PyAudio)

**macOS:**

```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows:**
PyAudio wheels are available via pip, but you may need to install from [unofficial binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Google Cloud Authentication

**Option A: Use Application Default Credentials**

```bash
gcloud auth application-default login
```

**Option B: Use Service Account Key**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

## Usage

Run the streaming speech recognition:

```bash
python stream_audio.py
```

The application will:

- Start listening to your microphone
- Display interim results (partial transcriptions) in real-time
- Show final transcriptions as complete sentences
- Continue until you press Ctrl+C

## Features

- **Real-time transcription**: See your words appear as you speak
- **Interim results**: Partial transcriptions update continuously
- **High accuracy**: Uses Google Cloud's state-of-the-art speech recognition
- **Streaming mode**: Low latency with continuous audio input

## Configuration

You can modify these parameters in `stream_audio.py`:

- `RATE`: Sample rate in Hz (default: 16000)
- `CHUNK`: Audio chunk size (default: RATE/10 = 1600)
- `language_code`: Language for recognition (default: "en-US")

## Troubleshooting

**No audio input detected:**

- Check your microphone permissions
- Verify the correct audio device is selected in system settings

**Import errors:**

- Ensure PortAudio is installed before installing PyAudio
- Try reinstalling PyAudio: `pip install --upgrade --force-reinstall pyaudio`

**Authentication errors:**

- Verify your Google Cloud credentials are set up correctly
- Check that the Speech-to-Text API is enabled in your project
