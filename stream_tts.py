import ollama
import subprocess
import sys

# Configuration
MODEL = "phi4-mini"  # Or gemma3:1b for max speed
PIPER_PATH = "/home/pi/piper/piper"  # Update path if different
VOICE_MODEL = "/home/pi/piper/voices/en_US-lessac-medium.onnx"

def speak_text(text):
    """Send text to Piper and play audio immediately."""
    if not text.strip():
        return
    try:
        # Run piper process
        piper = subprocess.Popen(
            [PIPER_PATH, "-m", VOICE_MODEL, "-f", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        # Play audio output directly via aplay
        play = subprocess.Popen(
            ["aplay", "-q", "-f", "cd", "-t", "raw", "-r", "22050", "-c", "1", "-"],
            stdin=piper.stdout,
            stderr=subprocess.DEVNULL
        )
        
        piper.stdin.write(text.encode())
        piper.stdin.close()
        piper.wait()
        play.wait()
    except Exception as e:
        print(f"TTS Error: {e}", file=sys.stderr)

def stream_chat(prompt):
    print(f"🤖 AI: ", end="", flush=True)
    
    # Stream tokens from Ollama
    stream = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}], stream=True)
    
    buffer = ""
    for chunk in stream:
        token = chunk['message']['content']
        print(token, end="", flush=True)
        buffer += token
        
        # Speak immediately when a sentence ends (. ! ?)
        if any(token.endswith(p) for p in [".", "!", "?", "\n"]):
            speak_text(buffer)
            buffer = ""
    
    # Speak any remaining text
    if buffer:
        speak_text(buffer)
    print("\n")

if __name__ == "__main__":
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        stream_chat(user_input)   