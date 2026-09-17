from src.transcriber import transcribe_audio
from src.translator import translate_segments
from src.tts import generate_segment_audio


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


# STEP 5
tts_segments = generate_segment_audio(
    translated_segments
)


print("\n================================")
print("TTS RESULT")
print("================================")

for segment in tts_segments:

    print(
        f"\n[{segment['start']:.2f}s - "
        f"{segment['end']:.2f}s]"
    )

    print(f"Text : {segment['text']}")
    print(f"Audio: {segment['audio']}")