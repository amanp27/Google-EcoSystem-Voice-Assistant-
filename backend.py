import io
import json
import base64
from datetime import datetime
from pathlib import Path
import assemblyai as aai
from openai import OpenAI
import config
import prompts
from models import Message, ConversationSession

class SpeechToText:
    def __init__(self):
        aai.settings.api_key = config.ASSEMBLYAI_API_KEY
        self.transcriber = aai.Transcriber()
        
    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio bytes to text using AssemblyAI"""
        try:
            import time
            
            timestamp = str(int(time.time() * 1000))
            temp_wav = f"temp_audio_{timestamp}.wav"
            
            # Save WAV file
            with open(temp_wav, "wb") as f:
                f.write(audio_data)
            
            # Check file size
            file_size = Path(temp_wav).stat().st_size
            if file_size < 1000:
                print(f"Audio file too small: {file_size} bytes")
                Path(temp_wav).unlink(missing_ok=True)
                return ""
            
            print(f"Transcribing audio file: {file_size} bytes")
            
            # Transcribe
            transcript = self.transcriber.transcribe(temp_wav)
            
            # Clean up
            Path(temp_wav).unlink(missing_ok=True)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Transcription error: {transcript.error}")
                return ""
            
            print(f"Transcription result: {transcript.text}")
            return transcript.text or ""
            
        except Exception as e:
            print(f"STT Error: {e}")
            import traceback
            traceback.print_exc()
            return ""

class LLMProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.conversation_history = []
        
    def start_conversation(self):
        """Initialize a new conversation"""
        self.conversation_history = [
            {"role": "system", "content": prompts.SYSTEM_PROMPT}
        ]
        
    def get_response(self, user_input: str, conversation_history: list = None) -> str:
        """Get response from OpenAI GPT-4o-mini"""
        try:
            self.conversation_history.append({"role": "user", "content": user_input})
            
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=self.conversation_history,
                max_tokens=150,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having trouble processing that. Could you try again?"

class TextToSpeech:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
    def synthesize(self, text: str) -> bytes:
        """Convert text to speech using OpenAI TTS"""
        response = self.client.audio.speech.create(
            model=config.TTS_MODEL,
            voice=config.TTS_VOICE,
            input=text
        )
        return response.content

class ConversationManager:
    def __init__(self):
        self.sessions = {}
        Path(config.CONVERSATION_DIR).mkdir(exist_ok=True)
        Path(config.AUDIO_DIR).mkdir(exist_ok=True)
        
    def create_session(self) -> str:
        """Create new conversation session"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now(),
            messages=[Message(
                role="assistant",
                content=prompts.WELCOME_MESSAGE,
                type="welcome"
            )]
        )
        self.sessions[session_id] = session
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session"""
        if session_id in self.sessions:
            self.sessions[session_id].messages.append(
                Message(role=role, content=content)
            )
    
    def end_session(self, session_id: str):
        """End session and save conversation"""
        if session_id in self.sessions:
            self.sessions[session_id].end_time = datetime.now()
            self._save_conversation(session_id)
    
    def _save_conversation(self, session_id: str):
        """Save conversation to JSON file"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        file_path = Path(config.CONVERSATION_DIR) / f"{session_id}.json"
        
        data = {
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "type": msg.type
                }
                for msg in session.messages
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_conversation(self, session_id: str) -> dict:
        """Get conversation data"""
        file_path = Path(config.CONVERSATION_DIR) / f"{session_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_audio(self, session_id: str, audio_data: bytes, speaker: str):
        """Save audio chunk to file"""
        audio_path = Path(config.AUDIO_DIR) / session_id
        audio_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = audio_path / f"{speaker}_{timestamp}.mp3"
        
        with open(file_path, 'wb') as f:
            f.write(audio_data)