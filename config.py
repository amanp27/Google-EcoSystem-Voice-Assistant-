import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio Settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1

# AssemblyAI STT Settings
STT_LANGUAGE = "en"
STT_MODEL = "best"  # or "nano" for faster processing

# OpenAI Settings
LLM_MODEL = "gpt-4o-mini"

# OpenAI TTS Settings
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer

# Session Settings
CONVERSATION_DIR = "conversations"
AUDIO_DIR = "audio_files"

# WebSocket Settings
WS_HEARTBEAT_INTERVAL = 30