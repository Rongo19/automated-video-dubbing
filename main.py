import time
from pathlib import Path

from src.downloader import download_video
from src.audio import extract_audio
from src.transcriber import transcribe_audio
from src.translator import translate_segments
from src.tts import generate_segment_audio
from src.audio_sync import create_synchronized_audio
from src.video_merger import merge_dubbed_audio


TOTAL_STEPS = 7


def format_time(seconds):
    """Convert seconds into a readable format."""

    if seconds < 60:
        return f"{seconds:.2f} sec"

    minutes = int(seconds // 60)
    remaining = seconds % 60

    return f"{minutes} min {remaining:.2f} sec"


def print_header():
    print("\n")
    print("=" * 70)
    print("                 AUTOMATED VIDEO DUBBING SYSTEM")
    print("=" * 70)
    print("   YouTube → Speech Recognition → Translation → TTS → Final Video")
    print("=" * 70)


def print_step(number, title, description):
    """Print a clean pipeline step header."""

    print("\n")
    print("=" * 70)
    print(f"[{number}/{TOTAL_STEPS}] {title}")
    print("-" * 70)
    print(f"→ {description}")
    print("=" * 70)


def print_step_complete(duration):
    print("-" * 70)
    print(f"✓ Step completed successfully")
    print(f"⏱ Time taken: {format_time(duration)}")


def main():

    print_header()

    url = input("\nEnter YouTube URL:\n> ").strip()

    if not url:
        print("\n❌ No YouTube URL provided.")
        return

    pipeline_start = time.perf_counter()

    timings = {}

    try:

        # ============================================================
        # STEP 1 — DOWNLOAD
        # ============================================================

        print_step(
            1,
            "📥 VIDEO DOWNLOAD",
            "Downloading the YouTube video using yt-dlp..."
        )

        start = time.perf_counter()

        video_path = download_video(url)

        timings["Video Download"] = time.perf_counter() - start

        print_step_complete(
            timings["Video Download"]
        )

        print(f"📁 Video: {video_path}")

        # ============================================================
        # STEP 2 — AUDIO EXTRACTION
        # ============================================================

        print_step(
            2,
            "🔊 AUDIO EXTRACTION",
            "Extracting and converting audio to 16 kHz mono WAV..."
        )

        start = time.perf_counter()

        audio_path = extract_audio(video_path)

        timings["Audio Extraction"] = time.perf_counter() - start

        print_step_complete(
            timings["Audio Extraction"]
        )

        print(f"📁 Audio: {audio_path}")

        # ============================================================
        # STEP 3 — TRANSCRIPTION
        # ============================================================

        print_step(
            3,
            "🗣️ SPEECH RECOGNITION",
            "Detecting language and transcribing speech using Whisper..."
        )

        start = time.perf_counter()

        language, segments = transcribe_audio(
            audio_path
        )

        timings["Speech Recognition"] = time.perf_counter() - start

        print_step_complete(
            timings["Speech Recognition"]
        )

        print(f"🌍 Detected language: {language}")
        print(f"📝 Speech segments: {len(segments)}")

        # ============================================================
        # STEP 4 — TRANSLATION
        # ============================================================

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

        timings["Translation"] = time.perf_counter() - start

        print_step_complete(
            timings["Translation"]
        )

        print(
            f"✓ Translated segments: "
            f"{len(translated_segments)}"
        )

        # ============================================================
        # STEP 5 — TEXT TO SPEECH
        # ============================================================

        print_step(
            5,
            "🎙️ ENGLISH VOICE GENERATION",
            "Generating English speech using Edge-TTS..."
        )

        start = time.perf_counter()

        tts_segments = generate_segment_audio(
            translated_segments
        )

        timings["Text-to-Speech"] = time.perf_counter() - start

        print_step_complete(
            timings["Text-to-Speech"]
        )

        print(
            f"✓ Generated audio segments: "
            f"{len(tts_segments)}"
        )

        # ============================================================
        # STEP 6 — AUDIO SYNCHRONIZATION
        # ============================================================

        print_step(
            6,
            "⏱️ AUDIO SYNCHRONIZATION",
            "Aligning English speech with the original timestamps..."
        )

        start = time.perf_counter()

        dubbed_audio = create_synchronized_audio(
            tts_segments
        )

        timings["Audio Synchronization"] = (
            time.perf_counter() - start
        )

        print_step_complete(
            timings["Audio Synchronization"]
        )

        print(f"📁 Dubbed audio: {dubbed_audio}")

        # ============================================================
        # STEP 7 — VIDEO MERGE
        # ============================================================

        print_step(
            7,
            "🎬 FINAL VIDEO MERGE",
            "Replacing the original audio while preserving the video..."
        )

        start = time.perf_counter()

        video_name = Path(video_path).stem

        output_path = (
            Path("output")
            / f"{video_name}_dubbed.mp4"
        )

        final_video = merge_dubbed_audio(
            video_path,
            dubbed_audio,
            str(output_path)
        )

        timings["Video Merge"] = time.perf_counter() - start

        print_step_complete(
            timings["Video Merge"]
        )

        print(f"📁 Final video: {final_video}")

        # ============================================================
        # TOTAL TIME
        # ============================================================

        total_time = (
            time.perf_counter()
            - pipeline_start
        )

        # ============================================================
        # FINAL REPORT
        # ============================================================

        print("\n\n")
        print("=" * 70)
        print("                    🎉 DUBBING COMPLETED")
        print("=" * 70)

        print("\n📊 PIPELINE PERFORMANCE")
        print("-" * 70)

        for step, duration in timings.items():

            print(
                f"{step:<30}"
                f"{format_time(duration):>20}"
            )

        print("-" * 70)

        print(
            f"{'TOTAL PROCESSING TIME':<30}"
            f"{format_time(total_time):>20}"
        )

        print("\n")
        print("📁 FINAL OUTPUT")
        print("-" * 70)
        print(final_video)

        print("\n")
        print("✓ Original video preserved")
        print("✓ Original audio replaced")
        print("✓ English dubbing generated")
        print("✓ Audio synchronized")
        print("✓ Final MP4 ready")

        print("\n" + "=" * 70)
        print("              THANK YOU FOR USING THE SYSTEM")
        print("=" * 70)

    except Exception as e:

        total_time = (
            time.perf_counter()
            - pipeline_start
        )

        print("\n")
        print("=" * 70)
        print("                     ❌ PIPELINE FAILED")
        print("=" * 70)

        print(f"\nError: {e}")

        print(
            f"\nTime before failure: "
            f"{format_time(total_time)}"
        )

        print("\nPlease check the error above.")

        raise


if __name__ == "__main__":
    main()