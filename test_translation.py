from src.transcriber import transcribe_audio
from src.translator import translate_segments


audio_path = "temp/audio.wav"


# STEP 3
language, segments = transcribe_audio(
    audio_path
)


# STEP 4
translated_segments = translate_segments(
    segments,
    language
)


print("\n================================")
print("FINAL TRANSLATION")
print("================================")

for segment in translated_segments:

    print(
        f"\n[{segment['start']:.2f}s - "
        f"{segment['end']:.2f}s]"
    )

    print(
        f"Original : "
        f"{segment['original_text']}"
    )

    print(
        f"English  : "
        f"{segment['translated_text']}"
    )