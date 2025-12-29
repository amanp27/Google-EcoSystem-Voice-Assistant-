# Real-Time Voice Assistant

Two-way bidirectional real-time voice assistant using AssemblyAI STT, Gemini LLM, and OpenAI TTS.

## Service Overview

This service is responsible for handling real-time voice interactions,
including audio streaming, speech transcription, LLM response generation,
text-to-speech synthesis, and conversation persistence.

## Requirements

- Python 3.13.9
- AssemblyAI API key
- OpenAI API key

## Features

- **Real-time voice conversation** via WebSocket
- **AssemblyAI Speech-to-Text** for accurate transcription
- **OpenAI LLM** for intelligent responses
- **OpenAI TTS** for natural voice synthesis
- **Conversation storage** in JSON format
- **Audio file recording** for each conversation
- **Dark-themed responsive UI**
- **Download conversations** and audio files

## Project Structure

```
├── app.py              # FastAPI main application
├── backend.py          # Core services (STT, LLM, TTS, ConversationManager)
├── config.py           # Configuration and settings
├── prompts.py          # System prompts and messages
├── models.py           # Data models (Pydantic)
├── index.html          # Frontend UI
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── conversations/      # Stored conversations (auto-created)
└── audio_files/        # Recorded audio files (auto-created)
```

## Setup

### 1. Python Version

Ensure you have Python 3.13.9 installed:

```bash
python --version  # Should show 3.13.9
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

- **AssemblyAI**: Get from https://www.assemblyai.com/
- **OpenAI API**: Get from OpenAI platform (https://platform.openai.com/api-keys)

### 4. Run the Application

```bash
python app.py
```

Or with uvicorn:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the Application

Open browser: `http://localhost:8000`

## Usage

1. **Start Session**: Click "Start Session" to connect
2. **Hold to Talk**: Press and hold the microphone button while speaking
3. **Release**: Release button to send audio to assistant
4. **Listen**: Wait for AI response
5. **End Session**: Click "End Session" when done

## API Endpoints

- `GET /` - Frontend UI
- `WebSocket /ws/voice` - Real-time voice communication
- `GET /api/conversations` - List all conversations
- `GET /api/conversation/{session_id}` - Get specific conversation
- `GET /api/download/{session_id}` - Download conversation JSON
- `GET /api/audio/{session_id}` - List audio files
- `GET /api/audio/{session_id}/{filename}` - Get audio file

## Configuration Options

Edit `config.py` to customize:

- **Audio settings**: Sample rate, channels
- **STT settings**: Language, model ("best" for accuracy, "nano" for speed)
- **TTS settings**: Voice type (alloy, echo, fable, onyx, nova, shimmer)
- **Gemini model**: Model version

## Conversation Format

```json
{
  "session_id": "20251226_100900",
  "start_time": "2025-12-26T10:09:00",
  "end_time": "2025-12-26T10:21:34",
  "messages": [
    {
      "role": "assistant",
      "content": "Hello! How can I help?",
      "type": "welcome"
    },
    {
      "role": "user",
      "content": "What's the weather like?"
    }
  ]
}
```

## Notes

- **WebSocket** is used for real-time bidirectional communication
- **AssemblyAI** provides accurate speech recognition with automatic punctuation
- Audio files are stored in MP3 format
- Conversations are automatically saved when session ends
- Frontend uses vanilla JavaScript for simplicity
- All audio is base64 encoded for WebSocket transmission
- Compatible with Python 3.13.9

## Architecture Flow
```
[ User presses "Hold to Talk" ]
              |
              v
[ Browser starts audio recording ]
              |
              v
[ Audio chunks streamed via WebSocket ]
              |
              v
[ Backend receives audio stream ]
              |
              v
[ AssemblyAI Speech-to-Text ]
( Voice → Text conversion )
              |
              v
[ Transcribed text sent to Gemini LLM ]
              |
              v
[ Gemini generates response text ]
              |
              v
[ Response text sent to OpenAI TTS ]
              |
              v
[ TTS converts text to audio ]
              |
              v
[ Audio streamed back to browser ]
              |
              v
[ User hears assistant response ]
              |
              v
[ User ends session ]
        |                 |
        v                 v
[ Conversation stored ]  [ Audio files saved ]
( JSON format )          ( per interaction )
```

## Future Improvements

- Streaming TTS playback
- Multi-language support
- User authentication
- Conversation analytics dashboard