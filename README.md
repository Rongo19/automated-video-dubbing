# Automated Video Dubbing System

An end-to-end Python pipeline that downloads a YouTube video, detects and transcribes the spoken language, translates the transcript into English, generates natural English speech, synchronizes the generated speech with the original timestamps, and replaces the original audio while preserving the original video stream.

## Project Overview

### Goal

The system converts a video spoken in another language into an English-dubbed video while keeping the original video content intact.

**Input:**
- YouTube video URL

**Output:**
- English-dubbed MP4 video

### Current Pipeline

```text
YouTube URL
    |
    v
+------------------+
|      yt-dlp      |
| Download Video   |
+--------+---------+
         |
         v
+------------------+
|      FFmpeg      |
| Extract Audio    |
+--------+---------+
         |
         v
+---------------------------+
| Faster-Whisper Base      |
| Language Detection + ASR |
+-------------+-------------+
              |
              v
       Original Transcript
              |
              v
+---------------------------+
| NLLB-200 distilled 600M  |
| Multilingual Translation |
+-------------+-------------+
              |
              v
         English Text
              |
              v
+---------------------------+
|        Edge-TTS           |
|     English Speech        |
+-------------+-------------+
              |
              v
        TTS Segments
              |
              v
+---------------------------+
|      Audio Sync /         |
| Timestamp Alignment       |
+-------------+-------------+
              |
              v
       dubbed_audio.wav
              |
              v
+---------------------------+
|          FFmpeg           |
| Replace Original Audio   |
| Copy Original Video      |
+-------------+-------------+
              |
              v
       final_dubbed_video.mp4
```

## Architecture

The project is divided into independent modules so each stage can be tested and improved separately.

### 1. Video Downloader

**File:** `src/downloader.py`

**Technology:** `yt-dlp`

Responsibilities:
- Accept a YouTube URL.
- Download the video.
- Prefer the best available video and audio streams.
- Merge them into MP4.
- Store downloaded files inside `temp/`.

Main flow:

```text
YouTube URL
    |
    v
yt-dlp
    |
    v
temp/<video>.mp4
```

### 2. Audio Extraction

**File:** `src/audio.py`

**Technology:** FFmpeg

The downloaded video's audio is extracted and converted to:

- WAV
- Mono
- 16 kHz
- PCM 16-bit

This format is convenient for speech-recognition models.

```text
Video MP4
   |
   | FFmpeg
   v
audio.wav
16 kHz / mono / PCM
```

### 3. Speech Recognition

**File:** `src/transcriber.py`

**Technology:** Faster-Whisper

**Current model:** Whisper `base`

Responsibilities:
- Detect the spoken language.
- Convert speech into text.
- Produce timestamped segments.

Example:

```text
[16.00s -> 19.00s]
Tu as fait quoi ce week-end ?

[19.00s -> 27.00s]
Je suis allé à Bordeaux pour voir mes parents et ma sœur.
```

The timestamps are critical because they are later used for dubbing synchronization.

### Why Whisper Base?

The project initially tested Whisper `tiny`.

Whisper Tiny was lightweight and fast but produced several transcription errors.

Whisper Base produced significantly cleaner segmentation and transcription for the French test video while remaining practical for local execution.

The model can later be changed to another Whisper size depending on available hardware and required accuracy.

### 4. Multilingual Translation

**File:** `src/translator.py`

**Technology:** NLLB-200

**Current model:** `facebook/nllb-200-distilled-600M`

Responsibilities:
- Accept the original-language transcript.
- Map the detected language code to the corresponding NLLB language code.
- Translate each segment into English.
- Preserve the original segment timestamps.

Example:

```text
French:
Tu as fait quoi ce week-end ?

English:
What did you do this weekend?
```

The system uses language mappings such as:

```text
fr -> fra_Latn
de -> deu_Latn
es -> spa_Latn
hi -> hin_Deva
mr -> mar_Deva
ta -> tam_Taml
te -> tel_Telu
ja -> jpn_Jpan
ko -> kor_Hang
zh -> zho_Hans
```

The mapping can be extended as required.

### 5. English Text-to-Speech

**File:** `src/tts.py`

**Technology:** Edge-TTS

**Current voice:** `en-US-AriaNeural`

Responsibilities:
- Generate English speech for each translated segment.
- Save each segment as an individual MP3 file.

Example:

```text
Translated segment
       |
       v
Edge-TTS
       |
       v
segment_1.mp3
segment_2.mp3
segment_3.mp3
...
```

The modular design allows the TTS provider or voice to be changed later.

### 6. Timestamp Synchronization

**File:** `src/audio_sync.py`

**Technology:** FFmpeg

The generated TTS files are not simply concatenated.

Each segment is placed at its original speech timestamp.

For example:

```text
Original:
0.00 -> 16.00
16.00 -> 19.00
19.00 -> 27.00
27.00 -> 30.00
30.00 -> 36.00
36.00 -> 38.00
38.00 -> 45.72
```

The synchronization stage creates a single English audio track:

```text
dubbed_audio.wav
```

This is important because translated speech can have a different duration from the source speech.

### 7. Final Video Merging

**File:** `src/video_merger.py`

**Technology:** FFmpeg

The original video stream is copied without re-encoding:

```text
-c:v copy
```

The original audio is replaced with the generated English audio.

```text
Original Video Stream
        |
        | copy without re-encoding
        v
English Dubbed Audio
        |
        v
final_dubbed_video.mp4
```

This preserves the original video quality and avoids unnecessary video encoding time.

---

# Current Project Structure

The recommended GitHub structure is:

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
│   └── video_merger.py
│
├── output/
│   └── .gitkeep
│
├── temp/
│   └── .gitkeep
│
├── tests/
│   ├── test_transcription.py
│   ├── test_translation.py
│   ├── test_tts.py
│   ├── test_audio_sync.py
│   └── test_merge.py
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```

## Important note about test files

During development, the project used files such as:

```text
test_transcription.py
test_translation.py
test_real_tts.py
test_audio_sync.py
test_merge.py
```

For GitHub, it is cleaner to put these inside a `tests/` directory.

The final application should be run through `main.py`, while the test files remain for development and verification.

---

# Dependencies

Create a `requirements.txt` file.

A reasonable starting version is:

```text
yt-dlp
faster-whisper
torch
torchaudio
transformers
sentencepiece
edge-tts
```

FFmpeg is also required, but it is a system dependency rather than a normal Python package.

## Installing Python dependencies

Create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## FFmpeg

FFmpeg must be installed separately and available on the system PATH.

Verify:

```powershell
ffmpeg -version
```

Also verify FFprobe:

```powershell
ffprobe -version
```

---

# `.gitignore`

Do NOT upload the virtual environment, downloaded videos, generated audio, model caches, or final generated videos to GitHub.

Create `.gitignore`:

```gitignore
# Virtual environment
venv/
.venv/
env/

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Local environment variables
.env
.env.*
!.env.example

# Downloaded/generated media
temp/*
output/*

# Keep directory structure
!temp/.gitkeep
!output/.gitkeep

# Model/cache directories
.cache/
huggingface/
models/

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
```

If you have important demo media that you intentionally want to publish, store it separately or use GitHub Releases rather than committing large video files to the repository.

---

# `.env.example`

At the moment, the pipeline does not require a secret API key for the current code.

However, if future versions use API credentials, create:

```text
.env.example
```

Example:

```env
# Add API keys here if future versions require them.
# Never commit the real .env file.
```

Then add `.env` to `.gitignore`.

---

# Running the Project

The current development process runs individual test files.

The final goal is to make `main.py` run the entire pipeline:

```text
python main.py
```

or:

```text
python main.py "https://www.youtube.com/watch?v=..."
```

The final application should perform:

```text
1. Download video
2. Extract audio
3. Detect language
4. Transcribe speech
5. Translate to English
6. Generate English speech
7. Synchronize speech
8. Replace video audio
9. Save final MP4
```

Expected output:

```text
output/
└── final_dubbed_video.mp4
```

---

# End-to-End Data Flow

The data passed between modules is approximately:

```text
YouTube URL
      |
      v
video_path
      |
      v
audio_path
      |
      v
{
    language: "fr",
    segments: [
        {
            start: 16.0,
            end: 19.0,
            text: "Tu as fait quoi ce week-end ?"
        }
    ]
}
      |
      v
{
    start: 16.0,
    end: 19.0,
    original_text: "Tu as fait quoi ce week-end ?",
    translated_text: "What did you do this weekend?"
}
      |
      v
TTS MP3
      |
      v
Timestamp-aligned WAV
      |
      v
Final MP4
```

---

# Testing Performed

The system was tested using a French YouTube video.

Whisper Base detected:

```text
Language: fr
Probability: 0.99
```

It generated 7 timestamped segments.

Example:

```text
[16.00s - 19.00s]
Tu as fait quoi ce week-end ?

[19.00s - 27.00s]
Je suis allé à Bordeaux pour voir mes parents et ma sœur.

[27.00s - 30.00s]
Ah, super ! C'était comment ?

[30.00s - 36.00s]
Il a fait très beau. On a même pu aller au bord de la mer.
```

NLLB successfully translated these segments into English.

Edge-TTS successfully generated English speech for all 7 segments.

The timestamp synchronization stage successfully generated the dubbed audio.

Finally, FFmpeg successfully merged the English audio with the original video.

The resulting MP4 played correctly.

---

# Known Limitations

## 1. Transcription quality

Whisper Base is substantially better than Tiny in the tested example, but transcription errors can still occur, especially with:
- background noise
- accents
- music
- overlapping speakers
- low-quality recordings

Because translation operates on the transcript, ASR errors can propagate into the final translation.

## 2. Translation quality

NLLB-200 is a multilingual translation model, but translation quality varies by language and sentence.

The first long French segment in testing contained ASR errors, which resulted in an awkward translation.

This is an upstream transcription problem rather than necessarily a translation-model problem.

## 3. Voice preservation

The current system generates a new English voice.

It does NOT currently preserve the original speaker's identity or vocal characteristics.

## 4. Background audio

The current implementation replaces the original audio track.

It does not yet separate:
- speech
- music
- environmental/background sounds

A future version could use source separation to preserve background audio while replacing only the speech.

## 5. Multiple speakers

The current pipeline does not perform speaker diarization.

Future versions could detect:

```text
Speaker 1
Speaker 2
Speaker 1
Speaker 3
```

and assign different English voices to each speaker.

## 6. Duration matching

English and source-language sentences can have different speaking durations.

The current timestamp synchronization handles placement, but a production system could additionally use:
- TTS speed adjustment
- time stretching
- sentence-level duration optimization

to make the dubbing more naturally aligned.

---

# Future Improvements

### Better ASR

Evaluate:
- Whisper Small
- Whisper Medium
- faster-whisper optimized models
- other multilingual ASR models

### Better Translation

Evaluate:
- NLLB-200 variants
- language-specific translation models
- improved text normalization

### Better TTS

Potential improvements:
- selectable English voices
- more natural voices
- emotion/style control
- speaker-specific voices
- voice cloning where legally and ethically appropriate

### Speaker Diarization

Add a diarization stage:

```text
Audio
  |
  v
Speaker Detection
  |
  +---- Speaker 1
  |
  +---- Speaker 2
  |
  +---- Speaker 3
```

### Speech Separation

Separate:

```text
Original Audio
      |
      +---- Speech
      |
      +---- Music
      |
      +---- Background
```

Then remove/replace only the speech layer.

### Web Interface

A future UI could allow:

```text
+-----------------------------------+
|     Automated Video Dubbing       |
|                                   |
| YouTube URL: [................]   |
|                                   |
| Target Language: [English  v]     |
| Voice:          [Aria     v]      |
|                                   |
|          [ Start Dubbing ]        |
+-----------------------------------+
```

---

# GitHub Setup

## 1. Create the repository locally

From the project directory:

```powershell
git init
```

## 2. Check the files

```powershell
git status
```

Make sure things such as:

```text
venv/
temp/*.mp4
temp/*.wav
temp/*.mp3
output/*.mp4
```

are ignored.

## 3. Add files

```powershell
git add .
```

## 4. Create the first commit

```powershell
git commit -m "Initial automated video dubbing pipeline"
```

## 5. Create a GitHub repository

On GitHub, create a repository named something like:

```text
automated-video-dubbing
```

Do not upload your `venv` or generated media files.

## 6. Connect the local repository

GitHub will give you a repository URL. Then run:

```powershell
git remote add origin YOUR_GITHUB_REPOSITORY_URL
```

Verify:

```powershell
git remote -v
```

## 7. Push

```powershell
git branch -M main
git push -u origin main
```

---

# Recommended GitHub Files

At minimum, publish:

```text
README.md
requirements.txt
.gitignore
LICENSE
main.py
src/
```

Recommended:

```text
tests/
.env.example
```

Do NOT publish:

```text
venv/
temp/*.mp4
temp/*.wav
temp/*.mp3
output/*.mp4
large model files
API keys
.env
```

---

# Suggested GitHub README Sections

The GitHub `README.md` should contain:

1. Project title
2. Project description
3. Features
4. Architecture
5. Pipeline workflow
6. Technologies used
7. Project structure
8. Installation
9. FFmpeg setup
10. Usage
11. Example
12. Output
13. Limitations
14. Future improvements
15. License

This makes the repository understandable to someone who has never seen the project before.

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Video Downloader | yt-dlp |
| Audio/Video Processing | FFmpeg |
| Speech Recognition | Faster-Whisper |
| ASR Model | Whisper Base |
| Translation | NLLB-200 |
| Translation Model | NLLB-200 distilled 600M |
| Text-to-Speech | Edge-TTS |
| Audio Format | WAV, 16 kHz, mono |
| Final Video | MP4 |
| Version Control | Git + GitHub |

---

# Final Architecture Summary

The system follows a modular pipeline:

```text
        INPUT
          |
          v
   YouTube Video URL
          |
          v
       yt-dlp
          |
          v
      Video MP4
          |
          v
       FFmpeg
          |
          v
      Audio WAV
          |
          v
   Faster-Whisper
          |
          v
  Language + Transcript
          |
          v
      NLLB-200
          |
          v
    English Text
          |
          v
      Edge-TTS
          |
          v
 English Speech Segments
          |
          v
    Audio Sync
          |
          v
  dubbed_audio.wav
          |
          v
       FFmpeg
          |
          v
 FINAL DUBBED VIDEO
```

## Project Status

**Current status: Working MVP**

The complete pipeline has been successfully tested from YouTube video input through final English-dubbed MP4 output.

The next development milestone is to consolidate the individual test scripts into a single production-oriented `main.py` command and improve transcription, translation, timing, and audio quality.
