from src.transcriber import transcribe_audio
from src.translator import translate_segments
from src.tts import generate_segment_audio
from src.audio_sync import create_synchronized_audio


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


# STEP 6
dubbed_audio = create_synchronized_audio(
    tts_segments
)


print("\n================================")
print("SYNCHRONIZED AUDIO RESULT")
print("================================")
print(f"Audio: {dubbed_audio}")