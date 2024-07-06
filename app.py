import pyaudio
import wave
import os
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from prompt import SYSTEM_PROMPT

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
SILENCE_THRESHOLD = 500  # Adjust this threshold as needed

# Load environment variables
load_dotenv()
assistant_id = os.getenv("ASSISTANT_ID")
client = OpenAI()

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create a new assistant and save the ID
# assistant = client.beta.assistants.create(
#     name="Language Translation Assistant",
#     instructions=SYSTEM_PROMPT,
#     model="gpt-4o")

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Recording...")


class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = ""

    @override
    def on_text_created(self, text) -> None:
        # No need to handle text creation separately
        pass

    @override
    def on_text_delta(self, delta, snapshot):
        delta_value = delta.value if hasattr(delta, 'value') else str(delta)
        print(delta_value, end="", flush=True)
        self.response_text += delta_value

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # Finalize the message
        print(f"\nassistant > {self.response_text}", flush=True)

# Function to capture and transcribe audio


def transcribe_audio():
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # Convert frames to numpy array for silence detection
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    # Check if audio data exceeds silence threshold
    if np.max(np.abs(audio_data)) < SILENCE_THRESHOLD:
        print("No significant audio detected.")
        return None

    # Save the captured audio to a temporary file
    audio_file_path = "temp_audio.wav"
    wf = wave.open(audio_file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribe the audio file using OpenAI API
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file)

    return transcript.text

# Function to convert text to speech and play it


def text_to_audio(text, audio_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    # Save and play the generated audio
    with open(audio_path, "wb") as f:
        for chunk in response.iter_bytes():
            f.write(chunk)

    audio_segment = AudioSegment.from_file(audio_path, format="mp3")
    play(audio_segment)


def send_message_to_assistant(client, thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=[{
            "type": "text",
            "text": content
        }]
    )
    return message


def run_assistant(client, thread_id):
    event_handler = EventHandler()
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        stream.until_done()
    response_text = event_handler.response_text
    event_handler.response_text = ""  # Clear response text for next interaction
    return response_text


def main():
    # Create a new thread
    thread = client.beta.threads.create()

    try:
        while True:
            transcription = transcribe_audio()
            if transcription:
                print(f"Transcription: {transcription}")

                # Send transcription to the assistant and get a response
                send_message_to_assistant(client, thread.id, transcription)
                assistant_response = run_assistant(client, thread.id)

                # Convert assistant's response to audio and play it
                response_audio_file = "response.mp3"
                text_to_audio(assistant_response, response_audio_file)
    except KeyboardInterrupt:
        print("Stopping...")
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
