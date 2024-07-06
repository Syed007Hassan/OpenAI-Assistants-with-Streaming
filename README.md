# Language Translation Assistant

This project is a Language Translation Assistant using OpenAI's API and PyAudio. It captures audio from a microphone, transcribes it, sends the transcription to an assistant, receives a response, and converts the response to speech.

## Features

- **Audio Capture**: Records audio using PyAudio.
- **Silence Detection**: Ensures only significant audio is processed.
- **Speech-to-Text**: Uses OpenAI's Whisper model to transcribe audio.
- **Language Translation**: Sends transcriptions to an assistant for translation.
- **Text-to-Speech**: Converts assistant's responses to audio and plays them back.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/language-translation-assistant.git
   cd language-translation-assistant
   ```

2. **Create a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root and add your OpenAI Assistant ID:
   ```sh
   ASSISTANT_ID=your_assistant_id
   OPENAI_API_KEY=sk-xxxx
   ```

## Usage

1. **Run the main script**:
   ```sh
   python main.py
   ```

2. **Interact with the assistant**:
   - Speak into the microphone.
   - The assistant will transcribe, translate, and respond in audio.

## Customization

- **Adjust recording settings**:
  Modify the `CHUNK`, `FORMAT`, `CHANNELS`, `RATE`, and `RECORD_SECONDS` constants to change the audio recording parameters.
  
- **Silence threshold**:
  Adjust the `SILENCE_THRESHOLD` to change the sensitivity of silence detection.

## Dependencies

- `pyaudio`
- `wave`
- `numpy`
- `pydub`
- `python-dotenv`
- `openai`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
