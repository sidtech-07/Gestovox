# GestoVox
### AI-Powered Voice & Gesture Controlled Smart Presentation System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![Vosk](https://img.shields.io/badge/Vosk-Offline%20Speech%20Recognition-red)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)

</p>

---

## Overview

**GestoVox** is an AI-powered smart presentation assistant that enables users to control presentations using **hand gestures** and **offline voice commands**.

Unlike conventional presentation tools that rely on remotes or internet-based services, GestoVox performs all processing locally, ensuring low latency, enhanced privacy, and uninterrupted operation.

The project integrates **Computer Vision**, **Human-Computer Interaction**, and **Offline Speech Recognition** into a unified presentation system.

---

## Features

- 🎤 Offline voice control (English & Hindi)
- ✋ Hand gesture-based slide navigation
- 🖱️ Virtual mouse control
- 📝 Real-time speech captions
- 📽️ Start and exit presentation using gestures
- 🎯 Laser pointer control through voice
- 🔄 Switch between English and Hindi speech models
- ⚡ Fully offline operation
- 💻 No cloud dependency

---

## Demo

> **Coming Soon**

Add:

- GIF demonstrating gesture control
- Video of voice commands
- Screenshot of caption overlay

---

## System Architecture

```text
                Webcam
                   │
                   ▼
              OpenCV Camera
                   │
                   ▼
        MediaPipe Hand Tracking
                   │
                   ▼
          Gesture Recognition
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Slide Control  Virtual Mouse  Presentation Commands

                Microphone
                   │
                   ▼
         Vosk Offline Recognition
                   │
                   ▼
          English / Hindi Models
                   │
                   ▼
          Voice Command Engine
                   │
                   ▼
          Live Caption Overlay

                   │
                   ▼
        Microsoft PowerPoint
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core Application |
| OpenCV | Computer Vision |
| MediaPipe | Hand Tracking |
| Vosk | Offline Speech Recognition |
| PyAutoGUI | Mouse & Keyboard Automation |
| Flask | Backend API |
| PyQt5 | Caption Overlay |
| HTML | User Interface |
| CSS | Styling |
| JavaScript | Frontend Interaction |

---

## Supported Voice Commands

| Command | Action |
|---------|--------|
| Start Presentation | Start slideshow |
| Next Slide | Move forward |
| Previous Slide | Move backward |
| Go to Slide 5 | Jump to slide |
| Click | Mouse click |
| Exit Presentation | Exit slideshow |
| Switch to English | English recognition |
| Switch to Hindi | Hindi recognition |
| Laser On | Enable laser |
| Laser Off | Disable laser |

---

## Installation

### Clone Repository

```bash
git clone https://github.com/sidtech-07/GestoVox.git
```

### Enter Project

```bash
cd GestoVox
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Download Vosk Models

Download:

- English Model
- Hindi Model

Place them inside the project directory and update their paths in the Python configuration.

---

## Run

```bash
python download.py
```

---

## Folder Structure

```
GestoVox/
│
├── src/
├── models/
├── images/
├── docs/
├── videos/
├── requirements.txt
├── download.py
├── README.md
└── LICENSE
```

---

## Screenshots

### Main Interface

> Add Screenshot

---

### Gesture Detection

> Add Screenshot

---

### Caption Overlay

> Add Screenshot

---

### Virtual Mouse

> Add Screenshot

---

## Future Enhancements

- AI Presentation Assistant
- Custom Gesture Training
- Support for Google Slides
- Support for LibreOffice Impress
- Multi-user Gesture Recognition
- Speaker Notes Overlay
- Gesture Customization
- Presenter Analytics
- Linux Support

---

## Project Status

This project is currently under active development.

Upcoming releases will focus on improving gesture accuracy, modular architecture, and cross-platform compatibility.

---

## Contributing

Contributions, suggestions, bug reports, and feature requests are welcome.

Please open an Issue before submitting major changes.

---

## License

This project is licensed under the MIT License.

---

## Author

**Siddharth Thakare**

M.Sc. Electronics Student

Embedded Systems • Computer Vision • AI • FPGA • Human–Computer Interaction

---

## Acknowledgements

- OpenCV
- MediaPipe
- Vosk Speech Recognition
- Flask
- PyQt5
- Python Community
