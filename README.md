# MADI Project
### *Local AI. Emotional Education. Human-Centered Technology.*
<img width="5118" height="2878" alt="7" src="https://github.com/user-attachments/assets/243e2be6-68c6-4096-a4af-362cf7cec3a6" />


---

## What is MADI?
**MADI** is an educational assistant built with **local LLM inference** and **TinyML emotional detection**, designed to bring high-quality learning support to communities without reliable internet access.

MADI listens, understands emotions through voice (neutral vs. frustrated), and responds with empathy — all running **offline**, on a  **Arduino Nano 33 BLE Sense** + **Jetson Orin Nano Super**.

No cloud. No data leaks.  
Just human-centered AI.

This project showcases how **Edge Impulse ML models** can power real-time **emotion recognition** on microcontrollers and how this emotional signal can be used to adapt the behavior of a **local LLM** running on embedded hardware.  
Emotion detection is the core innovation of this project and the main driver of the assistant’s teaching style.


---

## 🧠 Core Features
- **TinyML-based emotion detection** on-device (audio / Edge Impulse)
- **Local Large Language Model** (Gemma 2B / Llama.cpp)  
- **Adaptive responses** depending on emotional state  
- **Push-to-talk hardware interaction**  
- **Offline, privacy-preserving operation**  
- **Designed for low-resource schools and communities**

---

## 🔧 Hardware Used
- Arduino Nano 33 BLE Sense 
- NVIDIA Jetson Orin Nano Super  
- Speaker 4-Mic Array or USB mic  
- Bluetooth speaker (optional)  
- Physical button + RGB LED  

---

## 🏗️ Architecture Overview

1. **Arduino Nano 33 BLE Sense** captures audio and runs a TinyML classifier that outputs two states:  
   - Neutral  
   - Frustrated  

2. It sends JSON via serial:
   ```json
   {"id":"audio","negative":0.23,"neutral":0.77}


3. **The Jetson Orin Nano Super** receives the emotional probabilities and integrates them into the assistant’s workflow:  

   - If the learner is **Neutral**:
      - Clear and direct explanations  
      - Normal pacing  
      - Concise responses  

   - If the learner is **Frustrated**:
      - Slower, calmer responses  
      - Step-by-step reasoning  
      - More examples, analogies, and micro-activities  
      - Supportive and empathetic tone  

    Emotion directly influences how the assistant teaches.



## **Local Whisper Transcription — Voice to Text Offline**

When the user presses the button and speaks, Whisper (running fully offline) transcribes the audio and sends clean text to the LLM.



## **Local LLM (Gemma 2B / Llama.cpp) — Context-Aware Response Generation**

The LLM uses both:  
- The **transcribed text**, and  
- The **emotional state**  

to generate a fully local, privacy-preserving, and emotionally aligned answer.



## **Audio Output — The Assistant Speaks Back**

The final response is spoken using a local TTS system through a USB or Bluetooth speaker.

---


## Installation

Refer to the documentation:

- [Arduino/Edge Impulse setup](docs/installation_guide_arduino.md)
- [Jetson setup](docs/installation_guide_jetson.md)
- [HW conection setup](docs/conection_guide.md)
  

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




