from pydub import AudioSegment
import speech_recognition as sr
import uuid

def transcribe_audio(audio_bytes):
    recognizer = sr.Recognizer()

    raw_file = f"temp_{uuid.uuid4().hex}.webm"
    wav_file = raw_file.replace(".webm", ".wav")

    with open(raw_file, "wb") as f:
        f.write(audio_bytes)

    audio = AudioSegment.from_file(raw_file)
    audio.export(wav_file, format="wav")

    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)

    return recognizer.recognize_google(audio_data)