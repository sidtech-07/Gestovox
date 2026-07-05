import cv2
import mediapipe as mp
import pyautogui
import threading
import time
import sys
import queue
import json
import re
import string
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from flask import Flask, jsonify
from flask_cors import CORS
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

# ---------------- Flask Setup ----------------
app = Flask(__name__)
CORS(app)

# ---------------- Global System State ----------------
system_active = False  # Whether gesture & voice system is running

# ---------------- Gesture/Mode Variables ----------------
pointer_pos = (0, 0)

# Slide & click cooldown
last_slide_time = 0           # Timestamp for slide/click cooldown
SLIDE_COOLDOWN = 1            # Minimum cooldown in seconds
SLIDE_DELAY = 1.5             # Time break after changing slides

# Mouse vs. Command mode toggle
mouse_control_mode = False
MODE_TOGGLE_COOLDOWN = 4      # Wait 4s between toggles
last_mode_toggle_time = 0

# Start Presentation (Middle Finger + Thumb)
START_PPT_COOLDOWN = 2
last_start_ppt_time = 0

# Model switching (Ring Finger + Thumb)
MODEL_SWITCH_COOLDOWN = 2
last_model_switch_time = 0

# Escape Gesture (Index + Pinky)
INDEX_PINKY_HOLD_DURATION = 2
index_pinky_start_time = 0

# Global variable for voice transcription caption
voice_caption = ""

# ---------------- Vosk Voice Recognition Setup ----------------
# Provide paths to two different Vosk models: English & Hindi.
model_path_en = "C:/Users/HP/Desktop/codes/python/model"  # Adjust to your English model
model_path_hi = "C:/Users/HP/Desktop/codes/python/vosk-model-small-hi-0.22" # Adjust to your Hindi model

try:
    model_en = Model(model_path_en)
    rec_en = KaldiRecognizer(model_en, 16000)
    print("English model loaded successfully!")
except Exception as e:
    print(f"Failed to load English model: {e}")
    sys.exit(1)

try:
    model_hi = Model(model_path_hi)
    rec_hi = KaldiRecognizer(model_hi, 16000)
    print("Hindi model loaded successfully!")
except Exception as e:
    print(f"Failed to load Hindi model: {e}")
    sys.exit(1)

# The current recognizer in use
current_rec = rec_en
using_model_index = 1  # 1 => English, 2 => Hindi

def switch_vosk_model(model_index):
    """
    Switch the current_rec to English (1) or Hindi (2).
    Also used by gesture (ring finger + thumb) or by voice commands.
    """
    global current_rec, using_model_index
    if model_index == 1:
        current_rec = rec_en
        using_model_index = 1
        print("Switched to English model")
    else:
        current_rec = rec_hi
        using_model_index = 2
        print("Switched to Hindi model")

audio_queue = queue.Queue()
processing_audio = False  # Flag to control audio processing

def audio_callback(indata, frames, time_info, status):
    """Callback for capturing audio input."""
    if status:
        print("Audio callback status:", status)
    audio_queue.put(bytes(indata))

# ---------------- Alphabetic Slides Setup ----------------
# 'a' -> '1', 'b' -> '2', ... 'z' -> '26'
alphabet_slides = {letter: str(i + 1) for i, letter in enumerate(string.ascii_lowercase)}

def parse_slide_number(command):
    """
    1) Check for 'go to slide a' => 'a' => '1'
    2) Check for numeric slides 'go to slide 12'
    Returns the slide number as a string, or None if not found.
    """
    # 1) Single letter
    letter_match = re.search(r'go to slide ([a-z])', command)
    if letter_match:
        letter = letter_match.group(1)
        if letter in alphabet_slides:
            return alphabet_slides[letter]

    # 2) Numeric slides
    match = re.search(r'go to slide (\d+)', command)
    if match:
        return match.group(1)

    return None

def process_audio():
    """Continuously processes incoming audio data and executes voice commands."""
    global processing_audio, voice_caption, current_rec
    with sd.RawInputStream(samplerate=16000, blocksize=16000, dtype="int16",
                           channels=1, callback=audio_callback):
        print("Listening for voice commands...")
        while processing_audio:
            data = audio_queue.get()
            if current_rec.AcceptWaveform(data):
                result = json.loads(current_rec.Result())
                command = result.get("text", "").lower().strip()
                print("Final recognized text:", command)
                voice_caption = command  # Update caption with final result
                execute_voice_command(command)
            else:
                partial_result = json.loads(current_rec.PartialResult())
                voice_caption = partial_result.get("partial", "").lower().strip()

def start_voice_recognition():
    """Starts the background thread for audio processing."""
    global processing_audio
    processing_audio = True
    threading.Thread(target=process_audio, daemon=True).start()

def stop_voice_recognition():
    """Stops the audio processing thread."""
    global processing_audio
    processing_audio = False

def execute_voice_command(command):
    """Executes recognized voice commands, including English & Hindi."""
    # 1) Go to Slide (alphabetic or numeric)
    slide_num = parse_slide_number(command)
    if slide_num:
        print(f"Voice Command: Going to slide {slide_num}")
        for digit in slide_num:
            pyautogui.press(digit)
        pyautogui.press("enter")
        return

    # 2) Start Presentation (English or Hindi)
    #    "start presentation" or "presentation shuru karo"
    if "start presentation" in command or "प्रेजेंटेशन शुरू" in command:
        print("Voice Command: Start Presentation (F5)")
        pyautogui.press("f5")
        return

    # 3) Laser Pointer On/Off
    if ("on laser" in command) or ("लेजर चालू" in command):
        print("Voice Command: Laser Pointer On (Ctrl+P)")
        pyautogui.hotkey("ctrl", "p")
        return
    if ("stop laser" in command) or ("लेजर बंद" in command):
        print("Voice Command: Laser Pointer Off (Ctrl+A)")
        pyautogui.hotkey("ctrl", "a")
        return

    # 4) Next / Previous Slide (English or Hindi)
    if "next slide" in command or "अगली स्लाइड" in command:
        print("Voice Command: Next Slide")
        pyautogui.press("right")
        return
    elif "previous slide" in command or "पिछली स्लाइड" in command:
        print("Voice Command: Previous Slide")
        pyautogui.press("left")
        return

    # 5) Click
    if "click" in command:
        print("Voice Command: Click")
        pyautogui.click()
        return

    # 6) Exit Presentation
    #    "exit presentation", "escape", or "presentation band karo"
    if ("exit presentation" in command or "escape" in command or
            "प्रेजेंटेशन बंद" in command):
        print("Voice Command: Exit Presentation")
        pyautogui.press("esc")  # Press Escape to exit PowerPoint
        return

    # 7) Switch Language by Voice
    #    "switch to english" or "switch to hindi"
    if "switch to english" in command or "इंग्लिश मोड चालू" in command:
        switch_vosk_model(1)
        return
    if "switch to hindi" in command or "either more" in command:
        switch_vosk_model(2)
        return

    # 8) Stop Program (English or Hindi)
    if "stop program" in command or "प्रोग्राम बंद" in command:
        print("Voice Command: Stopping program")
        stop_system()
        sys.exit()

# ---------------- PyQt Overlay for Captions ----------------
class CaptionOverlay(QMainWindow):
    """A semi-transparent overlay window for displaying transcribed text."""
    def __init__(self):
        super().__init__()
        self.caption = ""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Position at bottom-left of the primary screen
        self.setGeometry(10, QApplication.primaryScreen().size().height() - 120, 800, 100)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(100)  # Update every 100 ms

    def update_overlay(self):
        """Update the overlay text from the global voice_caption."""
        global voice_caption
        self.caption = voice_caption
        self.repaint()

    def paintEvent(self, event):
        """Paint a semi-transparent rectangle with the caption text."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 128))  # Semi-transparent background
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(self.rect(), Qt.AlignLeft | Qt.AlignVCenter, self.caption)

# ---------------- Gesture Control ----------------
def gesture_controls():
    """
    Captures webcam frames and detects only ONE hand for gesture control.
    Features:
      - 4s cooldown to toggle Mouse vs. Command Mode (thumb + pinky)
      - Start Presentation (middle finger + thumb) => 2s cooldown
      - Switch Vosk Model (ring finger + thumb) => 2s cooldown
      - Escape => Index + Pinky for 2 seconds
      - Slide changes in Command Mode, Click in Mouse Mode
      - Slide Delay after next/previous slides
    """
    global pointer_pos, last_slide_time, mouse_control_mode, system_active
    global last_mode_toggle_time, last_start_ppt_time, last_model_switch_time
    global index_pinky_start_time

    cap = cv2.VideoCapture(0)
    sensitivity_factor = 4  # Higher => faster, more sensitive virtual mouse
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=2
    ) as hands:
        while cap.isOpened() and system_active:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Mirror effect
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                # Select only ONE hand (the closest one) based on WRIST y-value
                largest_hand = max(
                    result.multi_hand_landmarks,
                    key=lambda hand: hand.landmark[mp_hands.HandLandmark.WRIST].y
                )

                # Extract relevant landmarks
                thumb_tip = largest_hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = largest_hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = largest_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = largest_hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = largest_hand.landmark[mp_hands.HandLandmark.PINKY_TIP]
                index_mcp = largest_hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                # Convert to pixel coords
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)
                ring_x, ring_y = int(ring_tip.x * w), int(ring_tip.y * h)
                pinky_x, pinky_y = int(pinky_tip.x * w), int(pinky_tip.y * h)
                mcp_x, mcp_y = int(index_mcp.x * w), int(index_mcp.y * h)

                # Distances for gestures
                distance_thumb_index = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5
                distance_thumb_middle = ((thumb_x - middle_x) ** 2 + (thumb_y - middle_y) ** 2) ** 0.5
                distance_thumb_ring = ((thumb_x - ring_x) ** 2 + (thumb_y - ring_y) ** 2) ** 0.5
                distance_thumb_pinky = ((thumb_x - pinky_x) ** 2 + (thumb_y - pinky_y) ** 2) ** 0.5

                # For escaping: index + pinky
                distance_index_pinky = ((index_x - pinky_x) ** 2 + (index_y - pinky_y) ** 2) ** 0.5

                current_time = time.time()

                # 1) Escape by holding index + pinky for 2 seconds
                if distance_index_pinky < 20:
                    if index_pinky_start_time == 0:
                        index_pinky_start_time = current_time
                    else:
                        if current_time - index_pinky_start_time >= INDEX_PINKY_HOLD_DURATION:
                            print("Gesture Command: Exit Presentation (Index + Pinky Held)")
                            pyautogui.press("esc")
                            index_pinky_start_time = 0
                else:
                    index_pinky_start_time = 0

                # 2) Toggle mouse control mode if thumb touches pinky, with 4s cooldown
                global last_mode_toggle_time
                if distance_thumb_pinky < 20 and (current_time - last_mode_toggle_time > MODE_TOGGLE_COOLDOWN):
                    mouse_control_mode = not mouse_control_mode
                    mode = "Mouse Control Mode" if mouse_control_mode else "Command Mode"
                    print("Switched to", mode)
                    last_mode_toggle_time = current_time

                # 3) Start presentation if middle finger touches thumb (2s cooldown)
                global last_start_ppt_time
                if distance_thumb_middle < 20 and (current_time - last_start_ppt_time > START_PPT_COOLDOWN):
                    print("Gesture Command: Start Presentation (F5)")
                    pyautogui.press("f5")
                    last_start_ppt_time = current_time

                # 4) Switch Vosk model if ring finger touches thumb (2s cooldown)
                global last_model_switch_time
                if distance_thumb_ring < 20 and (current_time - last_model_switch_time > MODEL_SWITCH_COOLDOWN):
                    # Toggle English/Hindi
                    if using_model_index == 1:
                        switch_vosk_model(2)  # Switch to Hindi
                    else:
                        switch_vosk_model(1)  # Switch to English
                    last_model_switch_time = current_time

                # 5) Mouse vs. Command Mode logic
                global last_slide_time
                if mouse_control_mode:
                    # Mouse mode: move pointer and allow click gesture with cooldown
                    scaled_index_x = int(index_x * sensitivity_factor)
                    scaled_index_y = int(index_y * sensitivity_factor)
                    pyautogui.moveTo(scaled_index_x, scaled_index_y)

                    # Click if thumb touches index finger and cooldown has passed
                    if distance_thumb_index < 20 and current_time - last_slide_time > SLIDE_COOLDOWN:
                        print("Gesture Command (Click): Click")
                        pyautogui.click()
                        last_slide_time = current_time
                else:
                    # Command mode: process slide changes if cooldown has passed
                    if current_time - last_slide_time > SLIDE_COOLDOWN:
                        horizontal_diff = abs(index_x - mcp_x)
                        if horizontal_diff > 50:
                            if index_x > mcp_x:
                                print("Gesture Command: Next Slide")
                                pyautogui.press("right")
                            else:
                                print("Gesture Command: Previous Slide")
                                pyautogui.press("left")
                            last_slide_time = current_time
                            # Add a short time break after changing slides
                            time.sleep(SLIDE_DELAY)

                # Draw landmarks for the selected hand
                mp_drawing.draw_landmarks(frame, largest_hand, mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Gesture Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

# ---------------- System Control Functions ----------------
def start_system():
    """Starts the gesture control and voice recognition threads if not already active."""
    global system_active
    if not system_active:
        system_active = True
        threading.Thread(target=gesture_controls, daemon=True).start()
        start_voice_recognition()
        print("System started")

def stop_system():
    """Stops the gesture control and voice recognition."""
    global system_active
    if system_active:
        system_active = False
        stop_voice_recognition()
        print("System stopped")

# ---------------- Flask Endpoints ----------------
@app.route('/start_transcription', methods=['GET'])
def flask_start():
    """Endpoint to start the system via HTTP GET."""
    start_system()
    return jsonify({"status": "system started"})

@app.route('/stop_transcription', methods=['GET'])
def flask_stop():
    """Endpoint to stop the system via HTTP GET."""
    stop_system()
    return jsonify({"status": "system stopped"})

@app.route('/get_transcription', methods=['GET'])
def flask_get_transcription():
    """Endpoint to retrieve the current transcription text."""
    return jsonify({"transcription": voice_caption})

def run_flask():
    """Runs the Flask server in a separate thread."""
    app.run(debug=False, use_reloader=False)

# ---------------- Main Application ----------------
def main():
    """Main entry point: start Flask server, then launch the PyQt overlay in the main thread."""
    # Start the Flask server
    threading.Thread(target=run_flask, daemon=True).start()

    # Start the PyQt overlay
    app_qt = QApplication(sys.argv)
    overlay = CaptionOverlay()
    overlay.show()
    sys.exit(app_qt.exec_())

if __name__ == "__main__":
    main()
