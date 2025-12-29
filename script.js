// WebSocket and recording state
let ws = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let isConnected = false;

// DOM elements
const statusDiv = document.getElementById('status');
const transcriptDiv = document.getElementById('transcript');
const connectBtn = document.getElementById('connectBtn');
const talkBtn = document.getElementById('talkBtn');
const saveBtn = document.getElementById('saveBtn');
const micIcon = document.getElementById('micIcon');
const audioPlayer = document.getElementById('audioPlayer');

// Update status display
function updateStatus(status, className) {
    statusDiv.textContent = status;
    statusDiv.className = 'status ' + className;
}

// Add message to transcript
function addMessage(type, text) {
    const timestamp = new Date().toLocaleTimeString();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + type + '-message';
    messageDiv.innerHTML = `
        <div class="timestamp">${timestamp}</div>
        <div>${text}</div>
    `;
    transcriptDiv.appendChild(messageDiv);
    transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
}

// Toggle connection
function toggleConnection() {
    if (isConnected) {
        disconnect();
    } else {
        connect();
    }
}

// Connect to WebSocket
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onopen = () => {
        isConnected = true;
        updateStatus('Connected - Ready to talk!', 'connected');
        connectBtn.textContent = 'Disconnect';
        talkBtn.disabled = false;
        saveBtn.disabled = false;
        transcriptDiv.innerHTML = '';
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'welcome') {
            addMessage('assistant', data.text);
            if (data.audio) {
                playAudio(data.audio);
            }
        } else if (data.type === 'transcription') {
            addMessage('user', data.text);
        } else if (data.type === 'response') {
            addMessage('assistant', data.text);
            if (data.audio) {
                playAudio(data.audio);
            }
        } else if (data.type === 'error') {
            addMessage('assistant', '⚠️ ' + data.message);
        } else if (data.type === 'info') {
            addMessage('assistant', '✅ ' + data.message);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('Connection error', 'disconnected');
    };
    
    ws.onclose = () => {
        isConnected = false;
        updateStatus('Disconnected', 'disconnected');
        connectBtn.textContent = 'Connect';
        talkBtn.disabled = true;
        saveBtn.disabled = true;
    };
}

// Disconnect from WebSocket
function disconnect() {
    if (ws) {
        ws.close();
    }
}

// Toggle recording
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

// Start recording audio
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            } 
        });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64Audio = reader.result.split(',')[1];
                ws.send(JSON.stringify({
                    type: 'audio',
                    data: base64Audio
                }));
            };
            reader.readAsDataURL(audioBlob);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        updateStatus('🎤 Listening...', 'listening');
        micIcon.textContent = '🔴';
        talkBtn.textContent = 'Stop Talking';
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please check permissions.');
    }
}

// Stop recording audio
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        updateStatus('Processing...', 'connected');
        micIcon.textContent = '🎤';
        talkBtn.textContent = 'Hold to Talk';
    }
}

// Play audio response
function playAudio(base64Audio) {
    const audio = new Audio('data:audio/mp3;base64,' + base64Audio);
    audio.play().catch(err => {
        console.error('Error playing audio:', err);
    });
}

// Save conversation
function saveConversation() {
    if (ws && isConnected) {
        ws.send(JSON.stringify({ type: 'save' }));
    }
}

// Handle button press and hold for talk button
talkBtn.addEventListener('mousedown', (e) => {
    if (!isRecording && isConnected) {
        e.preventDefault();
        startRecording();
    }
});

talkBtn.addEventListener('mouseup', (e) => {
    if (isRecording) {
        e.preventDefault();
        stopRecording();
    }
});

talkBtn.addEventListener('mouseleave', () => {
    if (isRecording) {
        stopRecording();
    }
});

// Touch events for mobile
talkBtn.addEventListener('touchstart', (e) => {
    if (!isRecording && isConnected) {
        e.preventDefault();
        startRecording();
    }
});

talkBtn.addEventListener('touchend', (e) => {
    if (isRecording) {
        e.preventDefault();
        stopRecording();
    }
});

// Prevent default click behavior on talk button
talkBtn.addEventListener('click', (e) => {
    e.preventDefault();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (ws && isConnected) {
        ws.close();
    }
});