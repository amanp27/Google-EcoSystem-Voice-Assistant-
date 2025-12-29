# Real-Time Voice Assistant

Two-way bidirectional real-time voice assistant using AssemblyAI STT, Gemini LLM, and OpenAI TTS.

This project was built to explore real-time voice AI systems,
focusing on low-latency speech pipelines, scalable WebSocket
communication, and practical integration of modern STT, LLM,
and TTS services, in Collabration with Tacktile Systems Pvt. Ltd.

## Requirements

- Python 3.13.9
- AssemblyAI API key
- Google Gemini API key  
- OpenAI API key

## Features

- **Real-time voice conversation** via WebSocket
- **AssemblyAI Speech-to-Text** for accurate transcription
- **Google Gemini** for intelligent responses
- **OpenAI TTS** for natural voice synthesis
- **Conversation storage** in JSON format
- **Audio file recording** for each conversation
- **Beautiful dark theme UI**
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
├── .env               # Environment variables (create from .env.example)
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
- **Gemini API**: Get from Google AI Studio (https://makersuite.google.com/app/apikey)
- **OpenAI API**: Get from OpenAI platform (https://platform.openai.com/api-keys)

### 4. Run the Application

```bash
python app.py
```

Or with uvicorn:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
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
      "type": "welcome",
      "timestamp": "2025-12-26T10:09:00"
    },
    {
      "role": "user",
      "content": "What's the weather like?",
      "timestamp": "2025-12-26T10:09:15"
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

## Troubleshooting

- **Microphone not working**: Check browser permissions
- **API errors**: Verify API keys in `.env`
- **AssemblyAI errors**: Ensure API key is valid and has credits
- **Audio quality**: Adjust `SAMPLE_RATE` in `config.py`
- **Python version issues**: Use Python 3.13.9 exactly

## Production Deployment

For production:
1. Use HTTPS for WebSocket security (wss://)
2. Add authentication/authorization
3. Implement rate limiting
4. Add error recovery mechanisms
5. Use production-grade ASGI server (gunicorn + uvicorn)
6. Set up proper logging and monitoring