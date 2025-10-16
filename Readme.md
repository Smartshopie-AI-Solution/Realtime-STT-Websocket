
# Real-time Speech-to-Text (STT) via WebSocket 

A real-time **Speech-to-Text** (STT) system designed for converting spoken language into written text instantly using WebSocket communication. This project supports both Vosk and Hugging Face Whisper models for flexible speech recognition.

## ✨ Features

- **Real-time transcription** via WebSocket streaming
- **Dual model support**: Vosk and Hugging Face Whisper models
- **Web-based interface** for easy microphone access
- **Configurable processing** with adjustable intervals
- **Cross-platform compatibility** (Windows, Linux, macOS)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Microphone access
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd STT
   ```

2. **Create and activate virtual environment**
   
   **Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   
   **Linux/macOS:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the web interface**
   - Open your browser and navigate to `http://localhost:8000`
   - Allow microphone permissions when prompted
   - Start speaking to see real-time transcription

## 🔧 Configuration

### Model Selection

Switch between Vosk and Hugging Face models by editing `scripts/config.py`:

```python
# For Vosk model
MODEL_TYPE = "vosk"
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# For Hugging Face Whisper model
MODEL_TYPE = "huggingface"
HUGGINGFACE_MODEL_NAME = "openai/whisper-base"
```

### Model Downloads

**Vosk Models:**
- Download models from [Vosk Models](https://alphacephei.com/vosk/models)
- Place downloaded models in the `models/` directory
- Update `VOSK_MODEL_PATH` in `config.py`

**Hugging Face Models:**
- Available models: `openai/whisper-tiny`, `openai/whisper-base`, `openai/whisper-small`, etc.
- Larger models provide better accuracy but require more processing time
- Models are automatically downloaded on first use

## 📁 Project Structure

```
STT/
├── main.py                 # Main FastAPI application
├── app.py                  # Setup and installation script
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── scripts/
│   ├── config.py          # Configuration settings
│   ├── process.py         # Audio processing logic
│   ├── utils.py           # Utility functions
│   └── exception_handling.py  # Error handling
├── templates/
│   └── index.html         # Web interface
├── models/                # Vosk model storage
└── venv/                  # Virtual environment
```

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /` - Web interface
- `WebSocket /audio-stream` - Real-time audio streaming endpoint

## 🐛 Troubleshooting

### Common Issues

1. **Microphone not working**
   - Ensure browser has microphone permissions
   - Check system audio settings

2. **Model loading errors**
   - Verify model paths in `config.py`
   - Ensure sufficient disk space for model downloads

3. **Performance issues**
   - Try smaller models for faster processing
   - Adjust `PROCESS_INTERVAL` in `config.py`

## 📝 License

This project is open source. Please check the license file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
