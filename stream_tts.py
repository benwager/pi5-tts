import ollama
import subprocess
import sys
import os
import tempfile


# Configuration
MODEL = "phi4-mini"  # Or gemma3:1b for max speed
PIPER_PATH = "/home/pi/piper/piper"  # Update path if different
VOICE_MODEL = "/home/pi/piper/voices/en_US-lessac-medium.onnx"

def get_bluetooth_sink():
    """Finds the currently active Bluetooth sink."""
    try:
        # List sinks and look for one that is RUNNING (like YouTube is using)
        result = subprocess.run(["pactl", "list", "short", "sinks"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "bluez" in line and "RUNNING" in line:
                # Format: Index Name ... -> We need the Name (2nd column)
                return line.split()[1]
        # Fallback: Just find any bluez sink
        for line in result.stdout.splitlines():
            if "bluez" in line:
                return line.split()[1]
    except Exception:
        pass
    return None

def speak_text(text):
    if not text.strip():
        return
    
    sink = get_bluetooth_sink()
    if not sink:
        print("No Bluetooth sink found, using default.")
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        piper = subprocess.Popen(
            ["piper", "-m", "en_US-lessac-medium.onnx", "--output-file", temp_path],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        piper.stdin.write(text.encode())
        piper.stdin.close()
        piper.wait()
        
        cmd = ["paplay", temp_path]
        if sink:
            cmd.insert(1, "-d") # Insert -d flag
            cmd.insert(2, sink) # Insert sink name
            
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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