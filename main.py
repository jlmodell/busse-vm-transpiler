from glob import glob
import os
import speech_recognition as sr
from pydub import AudioSegment
from fastapi import FastAPI, BackgroundTasks
from uvicorn import run

def get_audio_from_file(file_path):
    return AudioSegment.from_file(file_path)

def export_audio_as_wav(audio, file_path):
    audio.export(file_path, format="wav")

def transcribe_wav_to_text(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    return r.recognize_google(audio)

def transcribe_voicemails():
    voicemails_glob = glob("/mnt/busse3/fs1/voicemails/*.mp3")
    voicemails_transcribed_glob = glob("/mnt/busse3/fs1/voicemails/*.txt")

    for voicemail_file in voicemails_glob:
        if voicemail_file.replace(".mp3",".txt") not in voicemails_transcribed_glob:
            audio = get_audio_from_file(voicemail_file)
            export_audio_as_wav(audio, voicemail_file.replace(".mp3", ".wav"))
            with open(voicemail_file.replace(".mp3", ".txt"), "w") as f:
                f.write(transcribe_wav_to_text(voicemail_file.replace(".mp3", ".wav")))
            os.remove(voicemail_file.replace(".mp3", ".wav"))

app = FastAPI()

@app.get("/")
def read_root():
    return {"version": "0.0.1"}

@app.get("/voicemails")
def read_voicemails(background_tasks: BackgroundTasks):
    background_tasks.add_task(transcribe_voicemails)
    return {"message": "messages are being transcribed in the background"}


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=3638, reload=True)

