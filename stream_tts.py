import ollama
import subprocess
import sys
import os
import tempfile


# Configuration
MODEL = "phi4-mini"  # Or gemma3:1b for max speed
PIPER_PATH = "/home/pi/piper/piper"  # Update path if different
VOICE_MODEL = "/home/pi/piper/voices/en_US-lessac-medium.onnx"

def speak_text(text):
    if not text.strip():
        return
    try:
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        # 1. Generate WAV file (Piper adds headers automatically with --output-file)
        piper = subprocess.Popen(
            ["piper", "-m", "en_US-lessac-medium.onnx", "--output-file", temp_path],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        piper.stdin.write(text.encode())
        piper.stdin.close()
        piper.wait()
        
        # 2. Play WAV file using paplay (PipeWire compatible, handles Bluetooth)
        # paplay automatically detects format from WAV header
        subprocess.run(["paplay", temp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 3. Clean up
        os.remove(temp_path)
        
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