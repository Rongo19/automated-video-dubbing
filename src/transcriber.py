from faster_whisper import WhisperModel


def transcribe_audio(audio_path: str):
    """
    Transcribe audio using Faster-Whisper Base.
    """

    print("→ Loading Whisper Base model...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

    print("✓ Whisper model loaded")
    print("→ Analyzing speech...")
    print("→ Detecting language...")
    print("→ Transcribing speech...\n")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True
    )

    detected_language = info.language
    language_probability = info.language_probability

    print(
        f"✓ Language: {detected_language}"
    )

    print(
        f"✓ Confidence: "
        f"{language_probability * 100:.1f}%"
    )

    results = []

    for segment in segments:

        text = segment.text.strip()

        if not text:
            continue

        results.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })

        print(
            f"[{segment.start:.2f}s → "
            f"{segment.end:.2f}s] {text}"
        )

    print(
        f"\n✓ Transcription completed"
    )

    print(
        f"✓ Segments detected: "
        f"{len(results)}"
    )

    return (
        detected_language,
        results
    )