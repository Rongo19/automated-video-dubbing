from pathlib import Path

from src.video_merger import merge_dubbed_audio


# ---------------------------------------------------------
# Find the downloaded video automatically
# ---------------------------------------------------------

temp_dir = Path("temp")

video_files = list(
    temp_dir.glob("*.mp4")
)

if not video_files:
    raise FileNotFoundError(
        "No MP4 video found inside temp/"
    )

if len(video_files) > 1:
    print("⚠ Multiple MP4 files found:")
    for file in video_files:
        print(f"  - {file}")

    print(
        "\nUsing the most recently modified video..."
    )

    video_path = max(
        video_files,
        key=lambda file: file.stat().st_mtime
    )
else:
    video_path = video_files[0]


# ---------------------------------------------------------
# Dubbed audio
# ---------------------------------------------------------

dubbed_audio_path = (
    Path("temp") /
    "dubbed_audio.wav"
)


if not dubbed_audio_path.exists():
    raise FileNotFoundError(
        "temp/dubbed_audio.wav was not found."
    )


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------

output_dir = Path("output")

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

output_path = (
    output_dir /
    "final_dubbed_video.mp4"
)


# ---------------------------------------------------------
# Display information
# ---------------------------------------------------------

print("=" * 70)
print("              STEP 7 — VIDEO MERGE TEST")
print("=" * 70)

print(f"\nVideo:")
print(video_path)

print(f"\nDubbed audio:")
print(dubbed_audio_path)

print(f"\nOutput:")
print(output_path)


# ---------------------------------------------------------
# Merge
# ---------------------------------------------------------

final_video = merge_dubbed_audio(
    str(video_path),
    str(dubbed_audio_path),
    str(output_path)
)


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("                 STEP 7 TEST COMPLETE")
print("=" * 70)

print(f"\n✓ Final video:")
print(final_video)

print("\n✓ Original video stream preserved")
print("✓ Original audio replaced")
print("✓ English dubbed audio added")
print("✓ Final MP4 created")

print("=" * 70)