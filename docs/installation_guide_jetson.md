# Installation Guide – Jetson Orin Nano Super  
Gemma-2 LLM · Whisper STT · Piper TTS · Emotion-Aware Assistant

This document describes all steps required to install, configure, and run the educational assistant on a Jetson Orin Nano Super using JetPack 6.2.  
The guide focuses exclusively on the Jetson-side components:

- llama.cpp (Gemma-2 LLM server)
- Whisper (speech-to-text)
- Piper (text-to-speech)
- Python environment
- GPIO button
- Serial communication for emotion data
- Execution of assistant.py

The Arduino/TinyML part is documented separately.

---

# 1. System Requirements

### Hardware
- Jetson Orin Nano Super Developer Kit
- USB microphone
- Speaker or headphones (USB or Bluetooth)
- Physical push-to-talk button (GPIO)
- Arduino Nano 33 BLE Sense (for emotion input)
- USB cable for Arduino

### Software
- JetPack 6.2 (Ubuntu 22.04)
- Python 3.8+
- Git, CMake, build tools

The paths in this tutorial use /home/orin/ as the directory, where orin is the device name. You must replace orin with your actual device name or username. For example:
If your device name is jetson_user, update the directory as:

- /home/jetson_user/piper/build/pi/share/espeak
---

# 2. Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

---

# 3. Install Base Dependencies

```bash
sudo apt install -y \
    git cmake build-essential \
    python3 python3-pip python3-venv \
    libasound2-dev libportaudio2 \
    alsa-utils \
    libffi-dev libssl-dev \
    curl wget
```

---

# 4. Clone the main Project Directory

```bash
git clone --branch modified https://github.com/ZGMFX20AR/orin_nano_assistant.git
cd orin_nano_assistant
chmod +x install_dependencies.sh
./install_dependencies.sh
```
---

# 5. Install Piper (Local Text-to-Speech)

## 5.1 Clone and build

```bash
cd ~
git clone https://github.com/rhasspy/piper.git
cd piper
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## 5.2 Move necessary files

```bash
sudo mv /home/orin/piper/build/pi/share/espeak-ng-data /usr/share/
sudo mkdir -p /usr/local/share/piper/models
sudo mv ~/orin_nano_assistant/assets/en_US-lessac-medium.onnx ~/orin_nano_assistant/assets/en_US-lessac-medium.onnx.json /usr/local/share/piper/models/
```

## 5.3 Install voice models

```bash
sudo mkdir -p /usr/local/share/piper/models
```

Download voices:

```bash
cd ~/piper
mkdir -p models
cd models

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium/es_MX-ald-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium/es_MX-ald-medium.onnx.json

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

Move:

```bash
sudo mv *.onnx *.json /usr/local/share/piper/models/
```

---

# 6. Install llama.cpp and Gemma-2 GGUF

## 6.1 Clone

```bash
cd ~
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
mkdir build && cd build
```

## 6.2 Build with CPU only

```bash
cmake .. -DGGML_CUDA=OFF
make -j$(nproc)
```

## 6.3 Download Gemma-2 model

```bash
cd ~/llama.cpp
mkdir models
cd models

wget -O gemma-2-2b-it-Q4_K_S.gguf \
"https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_S.gguf"
```

## 6.4 Test

```bash
cd ~/llama.cpp/build-cpu
./bin/llama-cli \
  -m ../models/gemma-2-2b-it-Q4_K_S.gguf \
  -p "Testing Gemma 2 on CPU" \
  -n 64 \
  -ngl 0
```

---

# 7. Start the LLM Server

Open a dedicated terminal:

```bash
cd ~/llama.cpp/build

./bin/llama-server \
  -m ../models/gemma-2-2b-it-Q4_K_S.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 2048 \
  -b 16 \
  -t 6 \
  -ngl 0 \
  --no-warmup
```

Keep this running.
<img width="1667" height="900" alt="image" src="https://github.com/user-attachments/assets/23c3564d-9982-4267-a4ad-b2920f2f784b" />

---

# 8. Create Python Virtual Environment

```bash
cd ~/orin_nano_assistant
python3 -m venv venv
source venv/bin/activate
```

---

# 9. Install Python Packages

```bash
pip install \
    openai-whisper \
    sounddevice \
    numpy \
    requests \
    pyserial \
    Jetson.GPIO
```

Install PyTorch for JetPack 6.2:

```bash
pip install torch-<version>.whl
```

---


## 10. Replace the default assistant.py with the customized version

The original repository cloned in the previous steps includes its own `assistant.py`, located at:

```
~/orin_nano_assistant/assistant.py
```

This file must be replaced with the customized version provided in this project, which includes:

- Whisper speech-to-text integration  
- Piper local TTS pipeline  
- Gemma-2 prompt construction  
- Emotion fusion logic  
- Serial JSON parsing  
- Hardware push-to-talk control  

Open any code editor and replace orin with your actual device name.

<img width="769" height="732" alt="image" src="https://github.com/user-attachments/assets/d0e5f3ea-001b-4fbc-a4f1-0b1bf9f01a82" />


### Steps:

1. Delete or overwrite the existing file:
```
rm ~/orin_nano_assistant/assistant.py
```

2. Copy your custom `assistant.py` into this directory:
```
cp /path/to/your/assistant.py ~/orin_nano_assistant/
```

(Replace `/path/to/your/assistant.py` with the actual location.)

3. Verify the file exists:
```
ls ~/orin_nano_assistant/assistant.py
```

If the file appears, the replacement was successful.

---

## Step 11: Run the Assistant

With all components configured, you can now launch the assistant:

```bash
python3 assistant.py
```

If the script starts without errors, the system is fully operational.  
You should see log messages indicating:

- Whisper has initialized  
- The serial connection to the Arduino is active  
- The LLM server is responding  
- The push-to-talk loop is waiting for input  

This confirms that your emotion-aware educational assistant is running correctly on the Jetson Orin Nano.

This marks the starting point for further experimentation.  
The modular design of this system allows you to extend or modify any component—TinyML model, prompts, hardware interface, or LLM behavior—depending on your goals.

---

# 10. GPIO Button Setup

Wiring:

- Pin 15 (BOARD mode): input from button
- Any GND pin: return path

`assistant.py` uses:

```
BUTTON_PIN = 15
GPIO.setmode(GPIO.BOARD)
```

<img width="528" height="1282" alt="image" src="https://github.com/user-attachments/assets/2a3b33aa-d979-4929-8b60-ef0c56fcd393" />


---

# 11. Serial Port for Emotion Data

Connect Arduino and check port:

```bash
ls /dev/ttyACM*
```

Configure in `assistant.py`:

```
AUDIO_SERIAL_PORT = "/dev/ttyACM0"
```

Arduino must output:

```json
{"id":"audio","negative":0.10,"neutral":0.90}
```

---

# 13. Audio Device Testing

Test microphone:

```bash
arecord -d 3 -f cd test.wav
aplay test.wav
```

---

# 14. Run the Assistant

```bash
cd ~/orin_nano_assistant
source venv/bin/activate
python3 assistant.py
```

Flow:

1. Press and hold button  
2. Speak  
3. Release  
4. Whisper transcribes  
5. Emotion affects LLM prompt  
6. Piper speaks response  

---

# 15. Performance Tips

- Use Whisper small on CUDA (`USE_GUI_MODE = False`)
- Set Jetson to MAXN performance mode
- Reduce context window (`-c 1024`) if memory is low
- Use quantized GGUF models (Q4_K_S recommended)

---

# 16. Troubleshooting

### LLM server fails  
Check CUDA:

```bash
nvidia-smi
```

### No audio output  
Test:

```bash
aplay <file>
```

### Serial issues  
Add user to dialout:

```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

### Piper silent  
Test standalone:

```bash
echo "test" | ~/piper/build/piper --model /usr/local/share/piper/models/es_MX-ald-medium.onnx --output_file t.wav
aplay t.wav
```

---

# Installation Complete

The Jetson Orin Nano Super is now fully set up to run:

- Whisper STT  
- Gemma-2 LLM  
- Piper TTS  
- GPIO interactions  
- Serial emotion input  

Your device is ready for the emotion-aware educational assistant.


