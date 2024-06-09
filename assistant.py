from openai import OpenAI
from utils import record_audio, play_audio
import warnings
import os
import time
import pygame
import uuid

# Ignore DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)
client = OpenAI()

def play_audio_with_pygame(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.quit()

while True:
    record_audio('test.wav')
    audio_file = open('test.wav', "rb")
    transcription = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file
    )
    print(transcription.text)

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": "You are my assistant. Please answer in short sentences."},
            {"role": "user", "content": f"Please answer: {transcription.text}"},
        ]
    )

    print(response.choices[0].message.content)
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=response.choices[0].message.content
    )

    # Use a unique filename for each speech output to avoid conflicts
    speech_filename = f"speech_{uuid.uuid4()}.mp3"
    speech_response.stream_to_file(speech_filename)
    
    # Use pygame to play the audio to ensure proper file release
    play_audio_with_pygame(speech_filename)
    
    # Ensure file is properly closed
    audio_file.close()
    
    # Optionally delete the file after playing to avoid accumulating files
    os.remove(speech_filename)
