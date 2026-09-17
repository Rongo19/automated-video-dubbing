from src.transcriber import transcribe_audio


audio_path = "temp/audio.wav"

language, segments = transcribe_audio(audio_path)

print("\n================================")
print("TRANSCRIPTION RESULT")
print("================================")

print(f"Language: {language}")

for segment in segments:
    print(
        f"[{segment['start']:.2f}s - {segment['end']:.2f}s] "
        f"{segment['text']}"
    )