"""Orchestrates the FastAPI application for the voice assistant service using WebSockets."""


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
#FastAPI → server
#WebSocket → real-time channel
#WebSocketDisconnect → clean disconnect handling
#HTTPException → REST error handling

from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import base64
import asyncio
from datetime import datetime
import backend
import prompts
import config

app = FastAPI(title="Voice Assistant API")

# Initialize services
# Server Creation
stt = backend.SpeechToText()
llm = backend.LLMProcessor()
tts = backend.TextToSpeech()
conv_manager = backend.ConversationManager()

# Active WebSocket connections
active_connections = {}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the frontend"""
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    session_id = conv_manager.create_session()
    active_connections[session_id] = websocket
    
    # Initialize LLM conversation
    llm.start_conversation()
    
    # Send welcome message
    try:
        welcome_audio = tts.synthesize(prompts.WELCOME_MESSAGE)
        conv_manager.save_audio(session_id, welcome_audio, "assistant")
        
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id
        })
        
        await websocket.send_json({
            "type": "audio",
            "data": base64.b64encode(welcome_audio).decode('utf-8'),
            "text": prompts.WELCOME_MESSAGE
        })
        
    except Exception as e:
        print(f"Error sending welcome message: {e}")
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_json()
            
            if data["type"] == "audio":
                try:
                    # Decode audio
                    audio_bytes = base64.b64decode(data["data"])
                    
                    # Speech to Text
                    user_text = stt.transcribe(audio_bytes)
                    
                    if user_text:
                        print(f"User: {user_text}")
                        conv_manager.add_message(session_id, "user", user_text)
                        conv_manager.save_audio(session_id, audio_bytes, "user")
                        
                        # Send transcription to client
                        await websocket.send_json({
                            "type": "transcription",
                            "role": "user",
                            "text": user_text
                        })
                        
                        # Get LLM response
                        assistant_text = llm.get_response(user_text)
                        print(f"Assistant: {assistant_text}")
                        conv_manager.add_message(session_id, "assistant", assistant_text)
                        
                        # Text to Speech
                        assistant_audio = tts.synthesize(assistant_text)
                        conv_manager.save_audio(session_id, assistant_audio, "assistant")
                        
                        # Send response back
                        await websocket.send_json({
                            "type": "audio",
                            "data": base64.b64encode(assistant_audio).decode('utf-8'),
                            "text": assistant_text
                        })
                        
                except Exception as e:
                    print(f"Processing error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": prompts.ERROR_MESSAGES["llm_error"]
                    })
            
            elif data["type"] == "end_session":
                break
                
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        conv_manager.end_session(session_id)
        if session_id in active_connections:
            del active_connections[session_id]

@app.get("/api/conversations")
async def list_conversations():
    """List all conversation sessions"""
    conv_dir = Path(config.CONVERSATION_DIR)
    conversations = []
    
    for file in conv_dir.glob("*.json"):
        with open(file, 'r') as f:
            data = json.load(f)
            conversations.append({
                "session_id": data["session_id"],
                "start_time": data["start_time"],
                "end_time": data.get("end_time"),
                "message_count": len(data["messages"])
            })
    
    return conversations

@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get specific conversation"""
    conversation = conv_manager.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.get("/api/download/{session_id}")
async def download_conversation(session_id: str):
    """Download conversation as JSON"""
    file_path = Path(config.CONVERSATION_DIR) / f"{session_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Conversation not found")
    return FileResponse(
        file_path,
        media_type="application/json",
        filename=f"conversation_{session_id}.json"
    )

@app.get("/api/download-audio/{session_id}")
async def download_conversation_audio(session_id: str):
    """Download merged audio of entire conversation"""
    audio_path = Path(config.AUDIO_DIR) / session_id
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="No audio files found")
    
    # Get conversation to determine order
    conversation = conv_manager.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Import pydub for audio merging
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create combined audio
        combined = AudioSegment.empty()
        
        # Add a small pause between messages (500ms silence)
        pause = AudioSegment.silent(duration=500)
        
        # Get all audio files sorted by timestamp
        audio_files = sorted(audio_path.glob("*.mp3"))
        
        for audio_file in audio_files:
            try:
                audio = AudioSegment.from_mp3(str(audio_file))
                combined += audio + pause
            except Exception as e:
                print(f"Error loading {audio_file}: {e}")
                continue
        
        if len(combined) == 0:
            raise HTTPException(status_code=404, detail="No valid audio files found")
        
        # Export to temporary file
        output_path = Path(config.AUDIO_DIR) / f"merged_{session_id}.mp3"
        combined.export(str(output_path), format="mp3")
        
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"conversation_{session_id}.mp3"
        )
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="Audio merging not available. Install pydub: pip install pydub"
        )

@app.get("/api/audio/{session_id}")
async def list_audio_files(session_id: str):
    """List all audio files for a session"""
    audio_path = Path(config.AUDIO_DIR) / session_id
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="No audio files found")
    
    files = []
    for file in audio_path.glob("*.mp3"):
        files.append({
            "filename": file.name,
            "size": file.stat().st_size,
            "url": f"/api/audio/{session_id}/{file.name}"
        })
    
    return files

@app.get("/api/audio/{session_id}/{filename}")
async def get_audio_file(session_id: str, filename: str):
    """Get specific audio file"""
    file_path = Path(config.AUDIO_DIR) / session_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)