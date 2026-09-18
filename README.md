# 🎙️ Automated Video Dubbing System

> An end-to-end Python pipeline that automatically converts spoken content from a YouTube video into English while preserving the original video.

The system downloads a YouTube video, extracts its audio, detects and transcribes the spoken language, translates the transcript into English, generates natural English speech, synchronizes the generated speech with the original timestamps, and finally replaces the original audio while preserving the original video stream.

---

## 🚀 Project Status

**Status: Working MVP — End-to-End Pipeline Tested Successfully**

The complete pipeline has been tested on an approximately 30-minute French video.

### Test Result

| | |
|---|---|
| Source language | **French** |
| Target language | **English** |
| Speech segments | **393** |
| Translation model | **NLLB-200** |
| TTS voice | **Edge-TTS — en-US-AriaNeural** |
| Processing device | **CPU** |
| Total processing time | **~14 minutes** |
| Output | Final MP4 generated successfully |

---

## 🎯 Project Objective

Build an automated video dubbing system that takes a video in a foreign language and generates an English-dubbed version automatically.

**Input:** YouTube Video URL
**Output:** English Dubbed MP4 Video

The original video stream is preserved while the original audio is replaced with synchronized English speech.

---

## 🧠 System Architecture

```text
                YouTube URL
                     │
                     ▼
                  yt-dlp
              (Video Download)
                     │
                     ▼
                  FFmpeg
             (Audio Extraction)
                     │
                     ▼
              Faster-Whisper
    (Speech Recognition + Language Detection)
                     │
                     ▼
                 NLLB-200
          (Translation to English)
                     │
                     ▼
                 Edge-TTS
          (English Speech Generation)
                     │
                     ▼
            Audio Synchronizer
           (Timestamp Alignment)
                     │
                     ▼
                  FFmpeg
             (Video + Audio Merge)
                     │
                     ▼
             English Dubbed MP4
```

---

## 🔄 Complete Pipeline

The system consists of seven major stages.

### Step 1 — Video Download

Accepts a YouTube URL and downloads the video using `yt-dlp`, stored inside `temp/`. The system avoids re-downloading a video when a valid checkpoint already exists.

### Step 2 — Audio Extraction

FFmpeg extracts the audio from the downloaded video and converts it to mono, 16 kHz, PCM WAV — the format required for speech recognition.

**Output:** `temp/audio.wav`

### Step 3 — Speech Recognition

**Faster-Whisper Base** performs speech recognition, language detection, timestamp generation, and speech segmentation.

```json
{
    "start": 3.42,
    "end": 8.91,
    "text": "Alors aujourd'hui..."
}
```

These timestamps are later used to synchronize the generated English audio.

### Step 4 — Translation

Recognized speech is translated into English using `facebook/nllb-200-distilled-600M` (**N**o **L**anguage **L**eft **B**ehind). The source language is automatically detected by Whisper and passed to the translation stage.

The current implementation supports a configured set of languages, including French, German, Spanish, Italian, Portuguese, Dutch, Russian, Ukrainian, Polish, Turkish, Arabic, Persian, Hindi, Marathi, Bengali, Gujarati, Tamil, Telugu, Kannada, Malayalam, Punjabi, Urdu, Nepali, Sinhala, Thai, Vietnamese, Indonesian, Malay, Japanese, Korean, and Chinese.

**Example**

```text
French:  "Est-ce que tu penses que le français est une langue facile ?"
English: "Do you think French is an easy language?"
```

### Step 5 — Text-to-Speech

Translated English text is converted into speech using **Edge-TTS**, currently the `en-US-AriaNeural` voice. Each translated segment becomes a separate audio file with its original timestamp metadata retained.

```text
temp/
└── tts_segments/
    ├── segment_1.mp3
    ├── segment_2.mp3
    └── ... segment_393.mp3
```

### Step 6 — Audio Synchronization

Generated English speech is positioned according to the original segment timestamps using FFmpeg filters (`adelay`, `apad`, `atrim`, `amix`). Audio is processed in chunks (default: 30 segments per chunk) rather than as one large FFmpeg command, which significantly reduces the number of inputs handled at once. The final duration is verified against the target timeline.

**Output:** `temp/dubbed_audio.wav`

### Step 7 — Video Merge

Combines the original video with the synchronized English audio. The original video stream is copied without re-encoding (`-c:v copy`), and the audio is encoded as AAC (`-c:a aac -b:a 192k`).

**Output:** `output/final_dubbed_video.mp4`

> **Note:** Only the audio track is replaced — the original video stream is fully preserved.

---

## 🔁 Checkpoint & Resume System

### Pipeline Checkpointing

Progress across all seven stages is stored in `temp/checkpoint.json`, so an interrupted run can reuse already-completed stages instead of starting over.

### Translation Resume

Translation progress is saved incrementally to `temp/translation_progress.json` — each segment is saved as soon as it's translated. If the process stops at, say, segment 100, the next run resumes from there instead of re-translating everything. This matters most on long videos, where translation can take several minutes.

---

## 📊 Performance

Tested on an approximately 30-minute French video.

**Test configuration:** French → English, 393 segments, CPU, Faster-Whisper Base, NLLB-200 Distilled 600M, Edge-TTS.

| Pipeline Stage | Time |
|---|---:|
| Video Download | Reused |
| Audio Extraction | Reused |
| Speech Recognition | Reused |
| Translation | 4 min 49 sec |
| Text-to-Speech | 7 min 21 sec |
| Audio Synchronization | 1 min 42 sec |
| Video Merge | 13 sec |
| **Total Processing Time** | **~14 min 6 sec** |

The complete pipeline successfully produced the final dubbed MP4.

---

## 🛠️ Technology Stack

| Category | Tools |
|---|---|
| Language | Python 3.13 |
| Video Processing | FFmpeg, yt-dlp |
| Speech Recognition | Faster-Whisper (Whisper Base) |
| Machine Translation | Hugging Face Transformers, NLLB-200 (`facebook/nllb-200-distilled-600M`) |
| Text-to-Speech | Edge-TTS (`en-US-AriaNeural`) |
| Deep Learning | PyTorch |
| Data Processing | JSON, pathlib, subprocess, asyncio |

---

## 📁 Project Structure

```text
automated-video-dubbing/
│
├── src/
│   ├── __init__.py
│   ├── downloader.py
│   ├── audio.py
│   ├── transcriber.py
│   ├── translator.py
│   ├── tts.py
│   ├── audio_sync.py
│   ├── video_merger.py
│   └── checkpoint.py
│
├── temp/
│   ├── audio.wav
│   ├── transcript.json
│   ├── translation.json
│   ├── translation_progress.json
│   ├── dubbed_audio.wav
│   ├── checkpoint.json
│   └── tts_segments/
│
├── output/
│   └── final_dubbed_video.mp4
│
├── tests/
│   ├── test_transcription.py
│   ├── test_translation.py
│   ├── test_tts.py
│   ├── test_audio_sync.py
│   ├── test_merge.py
│   └── test_checkpoint.py
│
├── main.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd automated-video-dubbing
```

### 2. Create a Virtual Environment (Windows)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

Main dependencies: `yt-dlp`, `faster-whisper`, `torch`, `torchaudio`, `transformers`, `sentencepiece`, `edge-tts`.

### 4. Install FFmpeg

Required for audio extraction, synchronization, silence generation, and video/audio merging.

Verify:

```powershell
ffmpeg -version
ffprobe -version
```

Both commands must work from the terminal.

---

## ▶️ Usage

```powershell
python main.py
```

You'll be prompted for a YouTube URL:

```text
Enter YouTube URL:
> https://youtu.be/VIDEO_ID
```

The pipeline then runs automatically:

```text
[1/7] Video Download
[2/7] Audio Extraction
[3/7] Speech Recognition
[4/7] Translation
[5/7] Text-to-Speech
[6/7] Audio Synchronization
[7/7] Video Merge
```

**Output:** `output/final_dubbed_video.mp4`

---

## 🧪 Testing Individual Components

Each pipeline stage can be tested independently — useful for isolating issues before running the full pipeline.

```powershell
python test_transcription.py    # Speech recognition
python test_tts.py              # Text-to-speech
python test_audio_sync.py       # Audio synchronization
python test_merge.py            # Video merge
python test_checkpoint.py       # Checkpoint system
```

---

## 🧩 Module Responsibilities

| Module | Responsibility |
|---|---|
| `downloader.py` | Connects to YouTube, downloads video, selects streams, produces MP4 |
| `audio.py` | Extracts audio via FFmpeg, converts to 16 kHz mono WAV |
| `transcriber.py` | Loads Faster-Whisper, detects language, transcribes, generates timestamped segments |
| `translator.py` | Loads NLLB-200, maps language codes, translates segments, saves/resumes progress |
| `tts.py` | Generates English speech via Edge-TTS, creates per-segment audio files |
| `audio_sync.py` | Positions speech using timestamps, generates silence, mixes segments in chunks, verifies duration |
| `video_merger.py` | Strips original audio, adds dubbed audio, copies video stream, produces final MP4 |
| `checkpoint.py` | Saves/loads pipeline progress, clears completed checkpoints, supports recovery |

---

## 🌍 Supported Languages

Mappings are defined in `translator.py`. Examples:

| Language | NLLB Code |
|---|---|
| French | `fra_Latn` |
| German | `deu_Latn` |
| Spanish | `spa_Latn` |
| Italian | `ita_Latn` |
| Portuguese | `por_Latn` |
| Russian | `rus_Cyrl` |
| Arabic | `arb_Arab` |
| Hindi | `hin_Deva` |
| Marathi | `mar_Deva` |
| Bengali | `ben_Beng` |
| Gujarati | `guj_Gujr` |
| Tamil | `tam_Taml` |
| Telugu | `tel_Telu` |
| Kannada | `kan_Knda` |
| Malayalam | `mal_Mlym` |
| Japanese | `jpn_Jpan` |
| Korean | `kor_Hang` |
| Chinese | `zho_Hans` |

Actual supported input languages depend on the configured mapping in `translator.py`.

---

## 🎯 Design Decisions

**Faster-Whisper** — efficient Whisper inference on CPU, with built-in language detection and timestamped segments.

**NLLB-200** — broad multilingual coverage without needing a separate translation system per language pair.

**Edge-TTS** — natural-sounding neural voices with simple Python integration.

**FFmpeg** — reliable media processing (extraction, conversion, delay, mixing, silence generation, muxing), and allows the original video stream to be copied without re-encoding.

---

## ⚠️ Current Limitations

1. **Original background audio is not preserved** — the original audio track, including music and ambient sound, is fully replaced.
2. **Single TTS voice** — all translated speech uses one voice (`en-US-AriaNeural`), regardless of how many speakers are in the source.
3. **No speaker diarization** — individual speakers are not identified or distinguished.
4. **No voice cloning** — generated speech does not resemble the original speaker's voice.
5. **Translation quality varies** — depends on source language, sentence complexity, ASR accuracy, and context; ASR errors can propagate into translation.
6. **Speech duration mismatches** — English translations may run shorter or longer than the original segment; timing follows the original timestamps rather than dynamically adjusting speech speed.
7. **Internet dependency** — YouTube downloading, Edge-TTS, and Hugging Face model downloads currently require connectivity, so a fully offline workflow isn't guaranteed.

---

## 🚀 Future Improvements

- **Multi-speaker dubbing** — add speaker diarization (e.g. `pyannote.audio`) and assign distinct TTS voices per speaker.
- **Voice cloning** — generate dubbed speech that resembles the original speaker.
- **Background audio preservation** — separate speech from music/sound effects, translate and re-synthesize only the speech, then remix with the original background.
- **GPU acceleration** — CUDA support for faster Whisper inference, NLLB translation, and audio processing.
- **Batch translation** — translate multiple segments together to improve NLLB throughput.
- **Context-aware translation** — use surrounding segments as context for more consistent translations.
- **Automatic speech speed adjustment** — dynamically adjust TTS playback speed to better fit each timestamp window.
- **Web interface** — a simple UI for submitting a URL, selecting target language, and tracking progress.

---

## 🔐 Environment Variables

If future versions require environment variables, define them in `.env`, with an example template committed as `.env.example`. Never commit secrets or API tokens to GitHub.

---

## 🗂️ Temporary Files

Intermediate files live in `temp/` (`audio.wav`, `transcript.json`, `translation.json`, `translation_progress.json`, `checkpoint.json`, `tts_segments/`, `audio_sync/`). These are generated during processing and should not normally be committed to GitHub.

## 🧹 Cleanup

After a successful run, the checkpoint system clears the completed pipeline checkpoint. Temporary media files in `temp/` can be manually removed if disk space is needed. Final results remain in `output/`.

---

## 📦 Requirements

```text
yt-dlp
faster-whisper
torch
torchaudio
transformers
sentencepiece
edge-tts
```

FFmpeg must be installed separately as a system dependency.

---

## 🔧 Troubleshooting

**FFmpeg not found**
`'ffmpeg' is not recognized` → install FFmpeg and add it to your system PATH, then verify with `ffmpeg -version`.

**Whisper model download issues**
The first run downloads the model, which takes longer; subsequent runs reuse the cached model.

**NLLB model download**
NLLB-200 is significantly larger than Whisper Base, so the first translation run takes extra time to download and load.

**Translation interrupted**
Resumes automatically from `temp/translation_progress.json` on the next run.

**Pipeline interrupted**
Resumes automatically from `temp/checkpoint.json`, reusing completed stages.

---

## 🧪 Tested Workflow

**Input:** French YouTube video, ~30 minutes

**Processing:** 393 speech segments → French transcription → French→English translation → 393 English TTS segments → timestamp synchronization → English dubbed audio → video/audio merge

**Output:** `output/final_dubbed_video.mp4` — generated successfully and playable.

---

## 📈 Current MVP Capabilities

| Feature | Status |
|---|:---:|
| YouTube video input | ✅ |
| Automatic video download | ✅ |
| Audio extraction | ✅ |
| Automatic language detection | ✅ |
| Speech transcription | ✅ |
| Timestamp generation | ✅ |
| Multilingual translation | ✅ |
| English TTS | ✅ |
| Timestamp-based synchronization | ✅ |
| Chunked audio processing | ✅ |
| Original video preservation | ✅ |
| Audio replacement | ✅ |
| Final MP4 generation | ✅ |
| Pipeline checkpointing | ✅ |
| Translation progress saving | ✅ |
| Background audio preservation | ✅ |

---

## 📚 Key Concepts Demonstrated

Automatic Speech Recognition · Natural Language Processing · Neural Machine Translation · Text-to-Speech · Audio signal processing · Timestamp alignment · Video processing · FFmpeg pipelines · Deep learning model inference · Multilingual AI · Pipeline checkpointing · Fault-tolerant processing · Python modular architecture

---

## 👨‍💻 Author

**Rohan Raju Gorde**
B.E. Artificial Intelligence & Data Science
PVG's College of Engineering and Technology, Pune

---

## 📄 License

This project is intended for educational and development purposes. Add your preferred open-source license (e.g. MIT License) if you choose to release it publicly.

---

## ⭐ Acknowledgements

This project builds on open-source technologies and models: Faster-Whisper, Whisper, Hugging Face Transformers, NLLB-200, PyTorch, Edge-TTS, FFmpeg, and yt-dlp.

---

## 🎬 Final Result

```text
🌍 Foreign-language YouTube Video → 🤖 AI Processing → 🎙️ English-Dubbed Video
```

The original video stream is preserved; the original audio is replaced by synchronized English speech.

**Status: WORKING END-TO-END MVP ✅**
The pipeline has successfully processed a ~30-minute French video and generated a complete English-dubbed MP4 in approximately **14 minutes** on a CPU-based setup.