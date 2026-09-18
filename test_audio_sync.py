# from src.transcriber import transcribe_audio
# from src.translator import translate_segments
# from src.tts import generate_segment_audio
# from src.audio_sync import create_synchronized_audio


# audio_path = "temp/audio.wav"


# # # STEP 3
# # language, segments = transcribe_audio(
# #     audio_path
# # )


# # # STEP 4
# # translated_segments = translate_segments(
# #     segments,
# #     language
# # )


# # # STEP 5
# # tts_segments = generate_segment_audio(
# #     translated_segments
# # )


# # STEP 6
# dubbed_audio = create_synchronized_audio(
#     tts_segments
# )


# print("\n================================")
# print("SYNCHRONIZED AUDIO RESULT")
# print("================================")
# print(f"Audio: {dubbed_audio}")

import json
from pathlib import Path

from src.audio_sync import create_synchronized_audio


# ---------------------------------------------------------
# Load recovered timestamps
# ---------------------------------------------------------

timestamps_file = Path("temp/timestamps.json")

if not timestamps_file.exists():
    raise FileNotFoundError(
        "temp/timestamps.json was not found."
    )

with open(
    timestamps_file,
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)


segments = data["segments"]

print("=" * 70)
print("           STEP 6 — AUDIO SYNCHRONIZATION TEST")
print("=" * 70)

print(f"Language : {data['language']}")
print(f"Segments : {len(segments)}")


# ---------------------------------------------------------
# Connect timestamps with existing TTS files
# ---------------------------------------------------------

tts_segments = []

for i, segment in enumerate(
    segments,
    start=1
):

    audio_file = (
        Path("temp/tts_segments")
        / f"segment_{i}.mp3"
    )

    if not audio_file.exists():
        raise FileNotFoundError(
            f"Missing TTS file: {audio_file}"
        )

    tts_segments.append({
        "start": segment["start"],
        "end": segment["end"],
        "text": segment["text"],
        "audio": str(audio_file)
    })


print(
    f"✓ Connected {len(tts_segments)} "
    "timestamps with TTS files"
)


# ---------------------------------------------------------
# Run synchronization
# ---------------------------------------------------------

dubbed_audio = create_synchronized_audio(
    tts_segments,
    output_path="temp/dubbed_audio.wav"
)


# ---------------------------------------------------------
# Final result
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("                 STEP 6 TEST COMPLETE")
print("=" * 70)

print(
    f"Dubbed audio: {dubbed_audio}"
)

print("=" * 70)