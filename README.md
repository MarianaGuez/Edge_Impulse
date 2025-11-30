# Emotion-Aware Local Educational Assistant  
TinyML (Edge Impulse) · Jetson Orin Nano Super · Gemma-2 LLM · Whisper STT · Piper TTS

This project showcases how **Edge Impulse TinyML models** can power real-time **emotion recognition** on microcontrollers and how this emotional signal can be used to adapt the behavior of a **local LLM** running on embedded hardware.  
Emotion detection is the core innovation of this project and the main driver of the assistant’s teaching style.

Everything runs fully offline on:
- Arduino Nano 33 BLE Sense (TinyML inference)
- Jetson Orin Nano Super (STT, LLM, TTS)

Enabling privacy-focused, low-latency deployment for classrooms and embedded environments.

## High-Level System Architecture

```
+---------------------------------------------------------------+
|                       Input Question                          |
+---------------------------------------------------------------+

+---------------------------+        +---------------------------+
| Arduino Nano BLE Sense   |        | Jetson Orin Nano Super     |
| (Edge Impulse TinyML)    |        | (Local AI Pipeline)        |
+------------+--------------+        +-------------+-------------+
             |                                        |
             v                                        v
     +----------------------+         +---------------------------+
     | Emotion Recognition  |         |  Whisper STT              |
     |(NEUTRAL / FRUSTRATED |         +------------+--------------+
     +----------+-----------+                      |
           JSON (serial)                           |
                |                                  v
                |                      +-----------------------+
                |--------------------->|Adaptive System Prompt |
                                       +-----------+-----------+
                                                   |
                                                   v
                                       +------------------------+
                                       | Gemma-2 LLM (LLM server)|
                                       +-----------+------------+
                                                   |
                                                   v
                                       +------------------------+
                                       | Piper TTS              |
                                       +-----------+------------+
                                                   |
                                                   v
                                            Speaker Output
```

## TinyML in the Project
**The emotional intelligence layer of this assistant depends entirely on Edge Impulse, and it is the foundation of how the system behaves.**

A central component of this assistant is its ability to recognize the user’s emotional state directly on a low-power microcontroller.  
For this, a lightweight audio-based classifier was designed using a TinyML workflow and deployed on the Arduino Nano 33 BLE Sense.  
The model runs entirely on-device and distinguishes between two states:

- Neutral  
- Negative / Frustrated  

The Jetson receives these probabilities over serial and uses them to adjust the behavior of the language model, enabling responses that feel more supportive when signs of frustration appear.

Benefits provided by TinyML Model:

- TinyML neural networks that run fully on-device
- MFE audio features processing
- Real-time emotion recognition without cloud processing  
- Perfect integration with embedded workflows
- Extremely low latency  
- Privacy-preserving inference  

## Project Overview

This assistant performs:

- Speech-to-text using Whisper  
- Emotion recognition using Edge Impulse TinyML 
- Emotion-adaptive prompting for LLM  
- Local educational reasoning using Gemma-2 (llama.cpp)  
- Local text-to-speech using Piper  
- Push-to-talk hardware control  

All inference is offline, private, and fast.

## Emotion-Adaptive LLM Behavior

**Neutral learner:**
- Clear and direct explanations  
- Secondary school–level reasoning  

**Frustrated learner:**
- Slow, patient response style  
- Step-by-step reasoning  
- Encouraging tone  
- Simple examples and micro-activities  

**Emotion determines how the assistant teaches.**

## Installation

Refer to the documentation:
- [Jetson setup](docs/installation_guide_jetson.md)

- [Arduino/Edge Impulse setup](docs/installation_guide_arduino.md)
  

## Repository Structure

```
/
├── assistant.py               Main assistant script
├── README.md                  Project documentation
├── docs/
│   ├── installation_guide_jetson.md
│   ├── installation_guide_arduino.md
│   └── conection_guide.md
└── SpeechEmotionRecognition/
    └── SpeechEmotionRecognition.ino

```

## Quick Start 

### 1. Start LLM server:
```bash
cd ~/llama.cpp/build
./bin/llama-server \
  -m ../models/gemma-2-2b-it-Q4_K_S.gguf \
  -p 8090 -t 4 -c 2048 -ngl 999
```

### 2. Activate Python environment:
```bash
cd ~/orin_nano_assistant
source venv/bin/activate
```

### 3. Run assistant:
```bash
python3 assistant.py
```

### 4. Usage:
- Press and hold button → speak  
- Release → Whisper transcribes  
- Edge Impulse model provides emotion  
- Jetson receives the emotion  
- LLM responds adapting the tone  
- Piper speaks the output  


## Configuration (./assistant.py)

```
USE_IMAGE_EMOTION = False
USE_GUI_MODE = True
LANGUAGE = "es"
BUTTON_PIN = 15
AUDIO_SERIAL_PORT = "/dev/ttyACM0"
LLM_URL = "http://127.0.0.1:8090/completion"
PIPER_MODEL_PATH = "/usr/local/share/piper/models/es_MX-ald-medium.onnx"
```



## Authors

Didier & Mariana – 2025  
Embedded AI • TinyML • Edge LLM Engineering

## License

This project is provided for educational and research use as part of the Edge Impulse Hackathon.
