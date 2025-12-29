SYSTEM_PROMPT = """You are a helpful, friendly AI voice assistant. 
Keep your responses conversational, concise, and natural for voice interaction.
Avoid using special characters, formatting, or overly long responses.
Respond as if you're having a real-time conversation with the user.
Be warm, engaging, and helpful."""

WELCOME_MESSAGE = "Hello! I'm your AI voice assistant. I'm here to help you with any questions or conversations you'd like to have. How can I assist you today?"

GOODBYE_MESSAGE = "Thank you for the conversation! Have a great day!"

ERROR_MESSAGES = {
    "stt_error": "I'm sorry, I couldn't hear that clearly. Could you please repeat?",
    "llm_error": "I'm having trouble processing that. Could you rephrase your question?",
    "tts_error": "I understood you, but I'm having trouble speaking right now.",
    "connection_error": "Connection interrupted. Please try again."
}