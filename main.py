import json
import time
from pathlib import Path

from src.downloader import download_video
from src.audio import extract_audio
from src.transcriber import transcribe_audio
from src.translator import translate_segments
from src.tts import generate_segment_audio
from src.audio_sync import create_synchronized_audio
from src.video_merger import merge_dubbed_audio

from src.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)


TOTAL_STEPS = 7

TEMP_DIR = Path("temp")
OUTPUT_DIR = Path("output")

TRANSCRIPT_FILE = TEMP_DIR / "transcript.json"
TRANSLATION_FILE = TEMP_DIR / "translation.json"


def format_time(seconds):
    """Convert seconds into a readable time format."""

    if seconds < 60:
        return f"{seconds:.2f} sec"

    minutes = int(seconds // 60)
    remaining = seconds % 60

    return f"{minutes} min {remaining:.2f} sec"


def print_header():

    print("\n")
    print("=" * 70)
    print("              AUTOMATED VIDEO DUBBING SYSTEM")
    print("=" * 70)
    print(
        " YouTube → Whisper → NLLB → Edge-TTS → "
        "Sync → Final Video"
    )
    print("=" * 70)


def print_step(number, title, description):

    print("\n")
    print("=" * 70)
    print(f"[{number}/{TOTAL_STEPS}] {title}")
    print("-" * 70)
    print(f"→ {description}")
    print("=" * 70)


def print_step_complete(duration):

    print("-" * 70)
    print("✓ Step completed successfully")
    print(f"⏱ Time taken: {format_time(duration)}")


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print_header()

    TEMP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    checkpoint = load_checkpoint()

    # ---------------------------------------------------------
    # CHECK FOR PREVIOUS RUN
    # ---------------------------------------------------------

    if checkpoint:

        print("\n⚡ Previous pipeline progress found.")

        print(
            f"→ Saved checkpoint: "
            f"{checkpoint.get('last_completed_step', 0)}/7"
        )

        print(
            "→ Completed work can be reused."
        )

    # ---------------------------------------------------------
    # GET URL
    # ---------------------------------------------------------

    url = input(
        "\nEnter YouTube URL:\n> "
    ).strip()

    if not url:

        print("\n❌ No YouTube URL provided.")

        return

    pipeline_start = time.perf_counter()

    timings = {}

    try:

        # =====================================================
        # STEP 1 — VIDEO DOWNLOAD
        # =====================================================

        video_path = checkpoint.get(
            "video_path"
        )

        if (
            checkpoint.get("step_1_completed")
            and video_path
            and Path(video_path).exists()
        ):

            print_step(
                1,
                "📥 VIDEO DOWNLOAD",
                "Reusing previously downloaded video..."
            )

            print(
                f"✓ Existing video found:\n"
                f"  {video_path}"
            )

            timings["Video Download"] = 0

        else:

            print_step(
                1,
                "📥 VIDEO DOWNLOAD",
                "Downloading the YouTube video using yt-dlp..."
            )

            start = time.perf_counter()

            video_path = download_video(url)

            timings["Video Download"] = (
                time.perf_counter() - start
            )

            checkpoint.update({
                "url": url,
                "video_path": video_path,
                "step_1_completed": True,
                "last_completed_step": 1,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Video Download"]
            )

        print(
            f"📁 Video: {video_path}"
        )


        # =====================================================
        # STEP 2 — AUDIO EXTRACTION
        # =====================================================

        audio_path = checkpoint.get(
            "audio_path"
        )

        if (
            checkpoint.get("step_2_completed")
            and audio_path
            and Path(audio_path).exists()
        ):

            print_step(
                2,
                "🔊 AUDIO EXTRACTION",
                "Reusing previously extracted audio..."
            )

            print(
                f"✓ Existing audio found:\n"
                f"  {audio_path}"
            )

            timings["Audio Extraction"] = 0

        else:

            print_step(
                2,
                "🔊 AUDIO EXTRACTION",
                "Extracting audio and converting it to 16 kHz mono WAV..."
            )

            start = time.perf_counter()

            audio_path = extract_audio(
                video_path
            )

            timings["Audio Extraction"] = (
                time.perf_counter() - start
            )

            checkpoint.update({
                "audio_path": audio_path,
                "step_2_completed": True,
                "last_completed_step": 2,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Audio Extraction"]
            )

        print(
            f"📁 Audio: {audio_path}"
        )


        # =====================================================
        # STEP 3 — SPEECH RECOGNITION
        # =====================================================

        if (
            checkpoint.get("step_3_completed")
            and TRANSCRIPT_FILE.exists()
        ):

            print_step(
                3,
                "🗣️ SPEECH RECOGNITION",
                "Reusing previously generated transcript..."
            )

            transcript_data = load_json(
                TRANSCRIPT_FILE
            )

            language = transcript_data[
                "language"
            ]

            segments = transcript_data[
                "segments"
            ]

            print(
                f"✓ Transcript loaded"
            )

            print(
                f"🌍 Language: {language}"
            )

            print(
                f"📝 Segments: {len(segments)}"
            )

            timings["Speech Recognition"] = 0

        else:

            print_step(
                3,
                "🗣️ SPEECH RECOGNITION",
                "Detecting language and transcribing speech using Whisper..."
            )

            start = time.perf_counter()

            language, segments = transcribe_audio(
                audio_path
            )

            timings["Speech Recognition"] = (
                time.perf_counter() - start
            )

            save_json(
                TRANSCRIPT_FILE,
                {
                    "language": language,
                    "segments": segments
                }
            )

            checkpoint.update({
                "language": language,
                "step_3_completed": True,
                "last_completed_step": 3,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Speech Recognition"]
            )

        print(
            f"🌍 Detected language: {language}"
        )

        print(
            f"📝 Speech segments: {len(segments)}"
        )


        # =====================================================
        # STEP 4 — TRANSLATION
        # =====================================================

        if (
            checkpoint.get("step_4_completed")
            and TRANSLATION_FILE.exists()
        ):

            print_step(
                4,
                "🌍 TRANSLATION",
                "Reusing previously generated English translation..."
            )

            translated_segments = load_json(
                TRANSLATION_FILE
            )

            print(
                f"✓ Translation loaded"
            )

            print(
                f"✓ Segments: "
                f"{len(translated_segments)}"
            )

            timings["Translation"] = 0

        else:

            print_step(
                4,
                "🌍 TRANSLATION",
                "Translating the transcript into English using NLLB-200..."
            )

            start = time.perf_counter()

            translated_segments = translate_segments(
                segments,
                language
            )

            timings["Translation"] = (
                time.perf_counter() - start
            )

            save_json(
                TRANSLATION_FILE,
                translated_segments
            )

            checkpoint.update({
                "step_4_completed": True,
                "last_completed_step": 4,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Translation"]
            )

        print(
            f"✓ Translated segments: "
            f"{len(translated_segments)}"
        )


        # =====================================================
        # STEP 5 — TEXT TO SPEECH
        # =====================================================

        tts_directory = Path(
            "temp/tts_segments"
        )

        existing_tts_files = list(
            tts_directory.glob("segment_*.mp3")
        )

        if (
            checkpoint.get("step_5_completed")
            and len(existing_tts_files)
            >= len(translated_segments)
        ):

            print_step(
                5,
                "🎙️ ENGLISH VOICE GENERATION",
                "Reusing previously generated English TTS..."
            )

            tts_segments = []

            for index, segment in enumerate(
                translated_segments,
                start=1
            ):

                audio_file = (
                    tts_directory /
                    f"segment_{index}.mp3"
                )

                if not audio_file.exists():

                    raise FileNotFoundError(
                        f"Missing TTS file: "
                        f"{audio_file}"
                    )

                tts_segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment[
                        "translated_text"
                    ],
                    "audio": str(audio_file)
                })

            print(
                f"✓ Existing TTS files found: "
                f"{len(tts_segments)}"
            )

            timings["Text-to-Speech"] = 0

        else:

            print_step(
                5,
                "🎙️ ENGLISH VOICE GENERATION",
                "Generating English speech using Edge-TTS..."
            )

            start = time.perf_counter()

            tts_segments = generate_segment_audio(
                translated_segments
            )

            timings["Text-to-Speech"] = (
                time.perf_counter() - start
            )

            checkpoint.update({
                "step_5_completed": True,
                "last_completed_step": 5,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Text-to-Speech"]
            )

        print(
            f"✓ Generated TTS segments: "
            f"{len(tts_segments)}"
        )


        # =====================================================
        # STEP 6 — AUDIO SYNCHRONIZATION
        # =====================================================

        dubbed_audio = Path(
            "temp/dubbed_audio.wav"
        )

        if (
            checkpoint.get("step_6_completed")
            and dubbed_audio.exists()
        ):

            print_step(
                6,
                "⏱️ AUDIO SYNCHRONIZATION",
                "Reusing previously synchronized audio..."
            )

            print(
                f"✓ Existing dubbed audio found:\n"
                f"  {dubbed_audio}"
            )

            timings["Audio Synchronization"] = 0

        else:

            print_step(
                6,
                "⏱️ AUDIO SYNCHRONIZATION",
                "Synchronizing English speech with original timestamps..."
            )

            start = time.perf_counter()

            dubbed_audio = create_synchronized_audio(
                tts_segments,
                output_path=str(dubbed_audio)
            )

            timings["Audio Synchronization"] = (
                time.perf_counter() - start
            )

            checkpoint.update({
                "dubbed_audio": str(dubbed_audio),
                "step_6_completed": True,
                "last_completed_step": 6,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Audio Synchronization"]
            )

        print(
            f"📁 Dubbed audio: "
            f"{dubbed_audio}"
        )


        # =====================================================
        # STEP 7 — VIDEO MERGE
        # =====================================================

        output_path = (
            OUTPUT_DIR /
            "final_dubbed_video.mp4"
        )

        if (
            checkpoint.get("step_7_completed")
            and output_path.exists()
        ):

            print_step(
                7,
                "🎬 FINAL VIDEO MERGE",
                "Reusing previously generated final video..."
            )

            final_video = str(
                output_path
            )

            print(
                f"✓ Existing final video found:\n"
                f"  {final_video}"
            )

            timings["Video Merge"] = 0

        else:

            print_step(
                7,
                "🎬 FINAL VIDEO MERGE",
                "Replacing the original audio while preserving the video..."
            )

            start = time.perf_counter()

            final_video = merge_dubbed_audio(
                video_path,
                str(dubbed_audio),
                str(output_path)
            )

            timings["Video Merge"] = (
                time.perf_counter() - start
            )

            checkpoint.update({
                "final_video": final_video,
                "step_7_completed": True,
                "last_completed_step": 7,
            })

            save_checkpoint(checkpoint)

            print_step_complete(
                timings["Video Merge"]
            )

        print(
            f"📁 Final video: "
            f"{final_video}"
        )


        # =====================================================
        # COMPLETE
        # =====================================================

        total_time = (
            time.perf_counter()
            - pipeline_start
        )

        print("\n\n")

        print("=" * 70)
        print("                  🎉 DUBBING COMPLETED")
        print("=" * 70)

        print("\n📊 PIPELINE PERFORMANCE")

        print("-" * 70)

        for step, duration in timings.items():

            if duration == 0:

                print(
                    f"{step:<30}"
                    f"{'REUSED':>20}"
                )

            else:

                print(
                    f"{step:<30}"
                    f"{format_time(duration):>20}"
                )

        print("-" * 70)

        print(
            f"{'TOTAL PROCESSING TIME':<30}"
            f"{format_time(total_time):>20}"
        )

        print("\n📁 FINAL OUTPUT")

        print("-" * 70)

        print(final_video)

        print("\n")

        print("✓ Video downloaded")
        print("✓ Speech transcribed")
        print("✓ Speech translated to English")
        print("✓ English voice generated")
        print("✓ Audio synchronized")
        print("✓ Original video preserved")
        print("✓ Original audio replaced")
        print("✓ Final MP4 created")

        # -----------------------------------------------------
        # CLEAR CHECKPOINT
        # -----------------------------------------------------

        clear_checkpoint()

        print(
            "\n✓ Pipeline completed successfully."
        )

        print(
            "✓ Checkpoint cleared."
        )

        print("\n")

        print("=" * 70)
        print("             AUTOMATED VIDEO DUBBING COMPLETE")
        print("=" * 70)


    except Exception as e:

        total_time = (
            time.perf_counter()
            - pipeline_start
        )

        print("\n")

        print("=" * 70)
        print("                    ❌ PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        print(
            f"\nTime before failure: "
            f"{format_time(total_time)}"
        )

        print(
            "\n✓ Completed work has been saved."
        )

        print(
            "✓ You can run the pipeline again "
            "to resume."
        )

        raise


if __name__ == "__main__":
    main()