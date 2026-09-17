from src.seamless import translate_audio_to_english


audio_path = "temp/audio.wav"

english_text = translate_audio_to_english(audio_path)

print("\n================================")
print("FINAL RESULT")
print("================================")
print(english_text)