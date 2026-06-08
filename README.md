# Install Python libraries
pip install ollama sounddevice

# Install Piper TTS (ARM64 binary)
mkdir -p ~/piper && cd ~/piper
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_aarch64.tar.gz
tar -xzf piper_linux_aarch64.tar.gz

# Download a fast, high-quality voice (Lessac Medium)
mkdir -p voices
wget -O voices/en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -O voices/en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Install system audio tools
sudo apt update && sudo apt install -y libportaudio2