from openai import OpenAI
from utils import record_audio, play_audio
import warnings
import os
import time
import pygame
import uuid
import platform

warnings.filterwarnings("ignore", category=DeprecationWarning)
client = OpenAI()

conversation_history = [
    {"role": "system", "content": "You are my assistant. Please answer in short sentences."}
]

def play_audio_with_pygame(file_path):
    pygame.mixer.init()
    time.sleep(0.5)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(1.0)
    time.sleep(0.5)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.quit()

def play_audio_with_alsa(file_path):
    import alsaaudio
    import wave

    wf = wave.open(file_path, 'rb')

    device = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    device.setchannels(wf.getnchannels())
    device.setrate(wf.getframerate())
    device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    device.setperiodsize(320)

    data = wf.readframes(320)
    audio_data = []
    while data:
        audio_data.append(data)
        data = wf.readframes(320)

    time.sleep(0.5)

    for chunk in audio_data:
        device.write(chunk)
    wf.close()

is_windows = platform.system() == "Windows"

while True:
    record_audio('test.wav')
    audio_file = open('test.wav', "rb")
    transcription = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file
    )
    print(transcription.text)

    conversation_history.append({"role": "user", "content": transcription.text})

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=conversation_history
    )

    assistant_message = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_message})

    print(assistant_message)
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=assistant_message
    )

    speech_filename = f"speech_{uuid.uuid4()}.mp3"
    speech_response.stream_to_file(speech_filename)

    if is_windows:
        play_audio_with_pygame(speech_filename)
    else:
        play_audio_with_alsa(speech_filename)

    audio_file.close()

    os.remove(speech_filename)
