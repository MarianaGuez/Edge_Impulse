# MADI PROJECT: Local Education with Emotion Recognition
## A learning assistant device designed so that the student can ask questions with their voices and receive simple explanations in real time. 
Among its main features are:
* It works without an internet connection.
* It only listens when a physical button is pressed.
* It recognizes when a student is speaking normally or with signs of frustration, adapting its tone to explain more patiently.
* It does not record personal data.
* It does not store or transmit information outside the device.
* The prototype was specifically designed to support teaching and learning processes with complete safety for students.



# Emotion-Aware Local Educational Assistant  
TinyML (Edge Impulse) · Jetson Orin Nano Super · Gemma-2 LLM · Whisper STT · Piper TTS · Hardware Push-to-Talk

This project implements a multimodal, emotion-aware educational assistant in which emotion detection is the foundation of the interaction.  
Using Edge Impulse–trained TinyML models, an Arduino Nano 33 BLE Sense classifies the learner’s emotional state (neutral or frustrated) and sends this information to a local LLM (Gemma-2) running on a Jetson Orin Nano Super.  
The assistant adapts its tone and explanations in real time based on the detected emotion.

The entire system operates offline, enabling privacy-focused, low-latency deployment for classrooms and embedded environments.

---

## Emotion Awareness (Core Feature)

### Why emotions first?

A key challenge in education is adapting explanations to the learner's emotional state.  
This assistant modifies its communication style depending on whether the user appears calm or frustrated.

### 1. Emotion Detection with TinyML (Edge Impulse)

Edge Impulse is used to train lightweight neural networks for:

- Audio-based emotion recognition (negative vs neutral)

The models run directly on the Arduino Nano 33 BLE Sense, ensuring minimal latency and full privacy.

### 2. Real-Time Emotional JSON Stream

The Arduino sends emotion probabilities through USB serial:

### 3. Emotion Fusion Engine
The Jetson converts the probabilities into one of two emotional states:

- #### NEUTRAL

- #### FRUSTRATED

This emotional state directly modifies the system prompt provided to the LLM.

### 4. Adaptive System Prompt (LLM Personality)
Neutral learner:

- Clear and direct explanations

- Focused on middle-school level clarity

Frustrated learner:

- Slow and patient instruction

- Step-by-step reasoning

- Encouraging tone

Simple examples and mini-activities

Emotion is not decoration.
Emotion determines how the assistant communicates and teaches.

## Local AI Pipeline Overview
The assistant runs entirely on the Jetson Orin Nano Super and includes:

- Whisper (local speech-to-text)

- Gemma-2 2B (GGUF) via llama.cpp (local LLM inference)

- Piper (local text-to-speech)

- TinyML emotion detection via Edge Impulse + Arduino Nano 33 BLE Sense

- Hardware push-to-talk button (GPIO)

- No cloud services are required.

## Quick Start 
These steps assume installation is complete.
Full setup is documented in docs/installation_guide.md.

### 1. Start the Local LLM Server (Gemma-2)

cd ~/llama.cpp/build
./bin/llama-server \
    -m ../models/gemma-2-2b-it-Q4_K_S.gguf \
    -p 8090 -t 4 -c 2048 -ngl 999
### 2. Activate the Python Environment

cd ~/orin_nano_assistant
source venv/bin/activate
### 3. Run the Assistant


python3 assistant.py
### 4. Usage
Hold the physical button to record audio

Whisper transcribes the speech

Jetson receives emotional signals from Arduino

The LLM generates an emotion-aware educational response

Piper converts the response to speech

