import os
import json
import whisper
import requests
import sounddevice as sd
import numpy as np
import tempfile
import wave
import torch
import Jetson.GPIO as GPIO
import time
import serial
import threading
import subprocess
import logging
from typing import Optional, Tuple

# ======================================
# LOGGING CONFIGURATION
# ======================================

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(threadName)s - %(message)s",
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("assistant")


# ======================================
# HIGH-LEVEL FEATURE TOGGLES
# ======================================

# Optional image-based emotion (Arduino + camera)
USE_IMAGE_EMOTION = False  # True to enable image emotion input, False to disable

# Whisper mode:
# True  -> GUI / light mode: tiny on CPU
# False -> headless / performance mode: small on CUDA (if available) or CPU
USE_GUI_MODE = False

# Language selection:
# "es" -> Spanish interaction (prompts in Spanish, Piper Spanish model, Whisper language "es")
# "en" -> English interaction (prompts in English, Piper English model, Whisper language "en")
LANGUAGE = "es"  # change to "en" for English


# ======================================
# WHISPER & PIPER CONFIG (BASED ON MODE & LANGUAGE)
# ======================================

# Whisper model / device based on GUI/headless mode
if USE_GUI_MODE:
    WHISPER_MODEL_NAME = "tiny"
    WHISPER_DEVICE = "cpu"
    logger.info("[CONFIG] GUI mode enabled: using Whisper 'tiny' on CPU.")
else:
    WHISPER_MODEL_NAME = "small"
    WHISPER_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"[CONFIG] Headless mode enabled: using Whisper '{WHISPER_MODEL_NAME}' on {WHISPER_DEVICE}.")

# Whisper language based on interaction language
if LANGUAGE == "es":
    WHISPER_LANGUAGE = "es"
    logger.info("[CONFIG] Interaction language: Spanish (Whisper language 'es').")
else:
    WHISPER_LANGUAGE = "en"
    logger.info("[CONFIG] Interaction language: English (Whisper language 'en').")

# Piper model path based on interaction language
if LANGUAGE == "es":
    # You can switch to es_MX-claude-medium.onnx if you prefer that voice
    PIPER_MODEL_PATH = "/usr/local/share/piper/models/es_MX-ald-medium.onnx"
    logger.info(f"[CONFIG] Piper Spanish model: {PIPER_MODEL_PATH}")
else:
    PIPER_MODEL_PATH = "/usr/local/share/piper/models/en_US-lessac-medium.onnx"
    logger.info(f"[CONFIG] Piper English model: {PIPER_MODEL_PATH}")


# ======================================
# CONSTANTS & CONFIG
# ======================================

EMOTION_NEUTRAL = "NEUTRAL"
EMOTION_FRUSTRATED = "FRUSTRATED"

LLM_URL = "http://127.0.0.1:8080/completion"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BEEP_SOUND = os.path.join(BASE_DIR, "assets/bip.wav")
BEEP2_SOUND = os.path.join(BASE_DIR, "assets/bip2.wav")

BUTTON_PIN = 15

AUDIO_SERIAL_PORT = "/dev/ttyACM0"
IMAGE_SERIAL_PORT = "/dev/ttyACM1"
SERIAL_BAUDRATE = 115200

PIPER_BIN = "/home/orin/piper/build/piper"
PIPER_OUTPUT_FILE = "response.wav"


# ======================================
# EMOTION MANAGER (THREAD-SAFE)
# ======================================

class EmotionManager:
    """
    Thread-safe manager to track multimodal emotion state
    (audio + image) and expose a high-level state for the LLM.
    """

    def __init__(self) -> None:
        self._state = EMOTION_NEUTRAL
        self._audio_probs = {"negative": None, "neutral": None}
        self._image_probs = {"negative": None, "neutral": None}
        self._lock = threading.Lock()

    def get_state(self) -> str:
        """Return current high-level emotion state."""
        with self._lock:
            return self._state

    def update_source_probs(self, source_id: str, negative: float, neutral: float) -> None:
        """
        Update probabilities for a given source ('audio' or 'imagen')
        and recompute the combined emotion state.
        """
        with self._lock:
            if source_id == "audio":
                self._audio_probs["negative"] = negative
                self._audio_probs["neutral"] = neutral
                logger.debug(f"[EMOTION-AUDIO] neg={negative:.4f}, neu={neutral:.4f}")
            elif source_id == "imagen":
                self._image_probs["negative"] = negative
                self._image_probs["neutral"] = neutral
                logger.debug(f"[EMOTION-IMAGE] neg={negative:.4f}, neu={neutral:.4f}")
            else:
                logger.warning(f"[EMOTION] Unknown source id received: {source_id}")
                return

            self._recalculate_state_locked()

    def _recalculate_state_locked(self) -> None:
        """
        Combine audio and image probabilities, normalize,
        and update the high-level emotion state.
        Must be called under self._lock.
        """
        neg_sum = 0.0
        neu_sum = 0.0
        count = 0

        if (
            self._audio_probs["negative"] is not None
            and self._audio_probs["neutral"] is not None
        ):
            neg_sum += self._audio_probs["negative"]
            neu_sum += self._audio_probs["neutral"]
            count += 1

        if (
            self._image_probs["negative"] is not None
            and self._image_probs["neutral"] is not None
        ):
            neg_sum += self._image_probs["negative"]
            neu_sum += self._image_probs["neutral"]
            count += 1

        if count == 0:
            logger.debug("[EMOTION] Not enough data to update emotion state yet.")
            return

        total = neg_sum + neu_sum
        if total <= 0:
            logger.warning("[EMOTION] Invalid probability total (<= 0). Skipping update.")
            return

        neg_norm = neg_sum / total
        neu_norm = neu_sum / total

        if neg_norm > neu_norm:
            self._state = EMOTION_FRUSTRATED
        else:
            self._state = EMOTION_NEUTRAL

        logger.info(
            f"[EMOTION] Combined -> neg={neg_norm:.3f}, neu={neu_norm:.3f} => {self._state}"
        )


# ======================================
# WHISPER MODEL INITIALIZATION
# ======================================

logger.info(f"[INIT] Loading Whisper '{WHISPER_MODEL_NAME}' on {WHISPER_DEVICE}...")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)
logger.info("[INIT] Whisper model loaded.")


# ======================================
# TEXT CLEANING
# ======================================

def clean_text_for_llm(text: str) -> str:
    """Remove NULL chars and keep printable / control newline/tab."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    cleaned_chars = []
    for ch in text:
        if ch in ("\n", "\t"):
            cleaned_chars.append(ch)
        elif ch >= " ":
            cleaned_chars.append(ch)
    return "".join(cleaned_chars)


def clean_llm_response(text: str) -> str:
    """
    Remove asterisks and other unwanted formatting characters
    from the LLM response before sending to TTS.
    """
    if not text:
        return ""
    text = text.replace("**", "")
    text = text.replace("*", "")
    return text.strip()


# ======================================
# EMOTION JSON PARSING & SERIAL READERS
# ======================================

def parse_emotion_json(line: str) -> Optional[Tuple[str, float, float]]:
    """
    Expect lines like:
      {"id":"audio","negative":0.13452,"neutral":0.86548}
      {"id":"imagen","negative":0.13452,"neutral":0.86548}

    Returns (source_id, negative, neutral) or None if parsing fails.
    """
    try:
        data = json.loads(line)
    except Exception:
        logger.debug(f"[EMOTION] Failed to parse JSON line: {line!r}")
        return None

    if not isinstance(data, dict):
        logger.debug(f"[EMOTION] Parsed JSON is not a dict: {data!r}")
        return None

    source_id = data.get("id")
    if source_id not in ("audio", "imagen"):
        logger.debug(f"[EMOTION] Ignoring JSON with unexpected id: {source_id!r}")
        return None

    try:
        negative = float(data.get("negative", 0.0))
        neutral = float(data.get("neutral", 0.0))
    except Exception:
        logger.warning(f"[EMOTION] Failed to convert probabilities to float: {data!r}")
        return None

    return source_id, negative, neutral


def emotion_serial_worker(
    emotion_manager: EmotionManager,
    port: str,
    expected_id: str,
    baudrate: int = SERIAL_BAUDRATE,
) -> None:
    """
    Generic worker that reads JSON lines from a serial port and updates
    the emotion manager only when the 'id' field matches expected_id.
    """
    try:
        serial_port = serial.Serial(port, baudrate, timeout=1)
        logger.info(f"[EMOTION-{expected_id.upper()}] Connected to {port}")
    except Exception as exc:
        logger.error(f"[EMOTION-{expected_id.upper()}] Error opening {port}: {exc}")
        return

    while True:
        try:
            line = serial_port.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                time.sleep(0.01)
                continue

            parsed = parse_emotion_json(line)
            if not parsed:
                continue

            source_id, negative, neutral = parsed
            if source_id != expected_id:
                logger.debug(
                    f"[EMOTION-{expected_id.upper()}] Ignoring line with id={source_id!r}: {line}"
                )
                continue

            emotion_manager.update_source_probs(source_id, negative, neutral)

        except Exception as exc:
            logger.error(f"[EMOTION-{expected_id.upper()}] Serial read error: {exc}")
            time.sleep(0.1)


# ======================================
# PROMPT BUILDING (EMOTION-AWARE, MULTI-LANGUAGE)
# ======================================

def build_system_prompt(emotion_state: str) -> str:
    """
    Build the system prompt depending on the current emotion state
    and selected LANGUAGE ("es" or "en").
    """
    if LANGUAGE == "es":
        base = (
            "Eres un asistente educativo en español. Responde con un máximo de 150 tokens. "
            "No uses listas ni símbolos como *, •, >>. "
            "Responde siempre de forma clara y sencilla.\n"
        )

        if emotion_state == EMOTION_FRUSTRATED:
            extra = (
                "El alumno está frustrado, así que responde con mucha paciencia y empatía, "
                "explicando paso a paso con ejemplos sencillos. "
                "Si algo puede ser difícil, sugiere una pequeña dinámica como hacer una pausa, "
                "un mini juego mental relacionado a la pregunta o un ejercicio simple antes de continuar.\n"
                "Nunca repitas literalmente esta descripción en tu respuesta.\n"
            )
        else:  # NEUTRAL
            extra = (
                "El alumno está tranquilo, así que responde de forma directa y amable, "
                "adaptando la explicación a nivel secundaria. "
                "Nunca repitas literalmente esta descripción en tu respuesta.\n"
            )

        return base + extra

    else:  # LANGUAGE == "en"
        base = (
            "You are an educational assistant. Answer in English with a maximum of 150 tokens. "
            "Do not use lists or symbols like *, •, >>. "
            "Always respond clearly and simply.\n"
        )

        if emotion_state == EMOTION_FRUSTRATED:
            extra = (
                "The student is frustrated, so answer with a lot of patience and empathy, "
                "explaining step by step with simple examples. "
                "If something may be difficult, suggest a short activity such as taking a break, "
                "a small mental game related to the question, or a simple exercise before continuing.\n"
                "Never repeat this description literally in your answer.\n"
            )
        else:  # NEUTRAL
            extra = (
                "The student is calm, so answer in a direct and friendly way, "
                "adapting the explanation to a middle-school level. "
                "Never repeat this description literally in your answer.\n"
            )

        return base + extra


# ======================================
# AUDIO CAPTURE
# ======================================

def play_sound(sound_file: str) -> None:
    """Play a WAV sound using aplay, ignoring errors."""
    try:
        subprocess.run(["aplay", sound_file], check=False)
    except Exception as exc:
        logger.error(f"[AUDIO] Error playing sound {sound_file}: {exc}")


def record_audio_while_pressed(filename: str, fs: int = 16000) -> None:
    """
    Record audio in small chunks while the button is pressed (GPIO HIGH)
    and save it as a WAV file.
    """
    play_sound(BEEP_SOUND)
    logger.info("Recording started... (release the button to stop)")

    audio_chunks = []

    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        chunk = sd.rec(int(0.1 * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
        audio_chunks.append(chunk.copy())

    play_sound(BEEP2_SOUND)
    logger.info("Recording stopped.")

    if not audio_chunks:
        logger.warning("No audio captured (empty buffer).")
        return

    audio_data = np.concatenate(audio_chunks, axis=0)

    try:
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(fs)
            wav_file.writeframes(audio_data.tobytes())
        logger.debug(f"Audio saved to {filename}")
    except Exception as exc:
        logger.error(f"Error saving audio to {filename}: {exc}")


def transcribe_audio(filename: str) -> str:
    """
    Run Whisper transcription on the recorded audio file.
    """
    logger.info(f"Starting transcription for file: {filename}")
    try:
        result = whisper_model.transcribe(
            filename,
            language=WHISPER_LANGUAGE,
            task="transcribe",
            fp16=False,
            temperature=0.0,
            beam_size=3,
            best_of=3,
        )
        text = result.get("text", "")
        logger.info(f"Transcription result: {text!r}")
        return text
    except Exception as exc:
        logger.error(f"Error during transcription: {exc}")
        return ""


# ======================================
# LLM REQUEST & DEBUG
# ======================================

def call_llm_with_prompt(prompt: str) -> Optional[str]:
    """
    Perform a single call to the local LLM server and return raw text
    extracted from the JSON response, or None on error.
    """
    logger.debug("================= PROMPT SENT TO LLM =================")
    logger.debug(prompt)
    logger.debug("======================================================")
    logger.debug(f"[DEBUG] Prompt length: {len(prompt)} characters")

    payload = {
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.8,
        "ignore_eos": True,
        "samplers": ["top_k", "top_p", "temperature"],
    }

    try:
        response = requests.post(
            LLM_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        logger.debug("=========== RAW RESPONSE (response.text) ===========")
        logger.debug(response.text)
        logger.debug("====================================================")

        if response.status_code != 200:
            logger.error(f"LLM error status: {response.status_code}")
            logger.error(f"LLM server message: {response.text}")
            return None

        try:
            response_json = response.json()
            logger.debug("=========== PARSED JSON (response.json()) =========")
            logger.debug(response_json)
            logger.debug("===================================================")
        except Exception as exc:
            logger.error(f"Error parsing LLM JSON response: {exc}")
            logger.error(f"Raw text: {response.text}")
            return None

        text = ""

        if isinstance(response_json, dict):
            if "content" in response_json and isinstance(response_json["content"], str):
                text = response_json["content"].strip()
            elif "text" in response_json and isinstance(response_json["text"], str):
                text = response_json["text"].strip()
            elif "choices" in response_json and response_json["choices"]:
                text = response_json["choices"][0].get("text", "").strip()

        logger.debug("=========== TEXT EXTRACTED FROM JSON ===========")
        logger.debug(repr(text))
        logger.debug("================================================")

        return text or ""

    except Exception as exc:
        logger.error(f"Exception while calling LLM: {exc}")
        return None


def ask_llm_with_emotion(
    user_query: str,
    emotion_state: str,
    allow_fallback: bool = True,
) -> str:
    """
    High-level function to ask the LLM with:
    - cleaned user text
    - emotion-aware system prompt
    - optional fallback on empty response
    - cleaned output for TTS
    """
    cleaned_query = clean_text_for_llm(user_query)
    system_prompt = build_system_prompt(emotion_state)

    if LANGUAGE == "es":
        full_prompt = (
            f"{system_prompt}\n"
            f"Pregunta del alumno:\n{cleaned_query}\n\n"
            "Empieza de inmediato con el contenido que el alumno pidió.\n"
            "Responde según las instrucciones."
        )
    else:
        full_prompt = (
            f"{system_prompt}\n"
            f"Student question:\n{cleaned_query}\n\n"
            "Start immediately with the content the student asked for.\n"
            "Answer following these instructions."
        )

    text = call_llm_with_prompt(full_prompt)

    if text is None:
        logger.error("LLM returned None (connection or internal error).")
        if LANGUAGE == "es":
            return "Hubo un error al conectar con el modelo local."
        else:
            return "There was an error connecting to the local model."

    if not text.strip():
        logger.warning("LLM returned an empty response (whitespace only).")

        if allow_fallback:
            logger.info("Trying fallback with minimal prompt...")
            if LANGUAGE == "es":
                fallback_prompt = (
                    "Responde en español de forma breve y clara a la siguiente pregunta de un alumno. "
                    f"{cleaned_query}\n"
                )
            else:
                fallback_prompt = (
                    "Answer briefly and clearly in English to the following student question: "
                    f"{cleaned_query}\n"
                )

            fallback_text = call_llm_with_prompt(fallback_prompt)

            if fallback_text and fallback_text.strip():
                return clean_llm_response(fallback_text)

        if LANGUAGE == "es":
            return "Lo siento, no pude generar una respuesta."
        else:
            return "Sorry, I was not able to generate a response."

    return clean_llm_response(text)


# ======================================
# TEXT-TO-SPEECH
# ======================================

def text_to_speech(text: str) -> None:
    """
    Convert text to speech using Piper.
    """
    safe_text = text.replace('"', '\\"')
    echo_cmd = f'echo "{safe_text}"'

    piper_cmd = [
        PIPER_BIN,
        "--model",
        PIPER_MODEL_PATH,
        "--length_scale",
        "0.9",
        "--output_file",
        PIPER_OUTPUT_FILE,
    ]

    try:
        subprocess.run(f"{echo_cmd} | " + " ".join(piper_cmd), shell=True, check=False)
        subprocess.run(["aplay", PIPER_OUTPUT_FILE], check=False)
        logger.info("TTS playback completed.")
    except Exception as exc:
        logger.error(f"[TTS] Error running Piper: {exc}")


# ======================================
# MAIN LOOP (PUSH-TO-TALK)
# ======================================

def main() -> None:
    emotion_manager = EmotionManager()

    # Audio emotion thread (always used)
    threading.Thread(
        target=emotion_serial_worker,
        kwargs={
            "emotion_manager": emotion_manager,
            "port": AUDIO_SERIAL_PORT,
            "expected_id": "audio",
        },
        daemon=True,
        name="EmotionAudioThread",
    ).start()

    # Image emotion thread (optional)
    if USE_IMAGE_EMOTION:
        logger.info("Image-based emotion is ENABLED. Starting image emotion thread.")
        threading.Thread(
            target=emotion_serial_worker,
            kwargs={
                "emotion_manager": emotion_manager,
                "port": IMAGE_SERIAL_PORT,
                "expected_id": "imagen",
            },
            daemon=True,
            name="EmotionImageThread",
        ).start()
    else:
        logger.info("Image-based emotion is DISABLED by configuration.")

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    logger.info("Educational assistant ready with PUSH-TO-TALK.")
    logger.info(f"Button on physical pin {BUTTON_PIN} (HIGH when pressed).")
    logger.info("Hold the button to talk.")
    logger.info("Release the button to let the assistant respond.")

    try:
        while True:
            logger.info("Waiting for button press...")

            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)

            logger.info("Button pressed -> starting recording...")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                record_audio_while_pressed(tmp_file.name)

                user_text = transcribe_audio(tmp_file.name)
                logger.info(f"User said: {user_text!r}")

                if not user_text.strip():
                    logger.warning("No text detected from transcription.")
                    continue

                current_emotion = emotion_manager.get_state()
                logger.info(f"Current emotion state: {current_emotion}")

                answer = ask_llm_with_emotion(user_text, current_emotion)
                logger.info(f"Assistant answer: {answer!r}")

                text_to_speech(answer)
                logger.info("Ready. You can speak again whenever you want.\n")

    finally:
        GPIO.cleanup()
        logger.info("GPIO cleaned up. Exiting.")


if __name__ == "__main__":
    main()

