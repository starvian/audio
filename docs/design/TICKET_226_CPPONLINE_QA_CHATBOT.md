# TICKET_226: C++Online 2026 Poster Q&A Chatbot

## Status: Open
## Priority: High
## Category: Conference / Presentation
## Parent: TICKET_225
## Date: 2026-02-25

---

## Background

English communication barrier during the C++Online 2026 poster session creates a risk that audience questions go unanswered or are answered poorly during the 20-minute live slot. The poster booth is active for the **entire 3-day conference**, meaning most interactions happen asynchronously without the presenter present.

### Solution

Deploy a self-service Q&A chatbot as the **Website object** in the Gather Town poster booth. The bot contains all 182 pre-written Q&A pairs from TICKET_205 (16 general + 166 technical), enabling attendees to get high-quality answers 24/7 without requiring live interaction.

### Solution - Two Deployment Modes

**Mode A: Booth Chatbot (for attendees, 24/7 self-service)**
Deploy as the Website object in the Gather Town poster booth. Attendees type questions and get instant answers from 182 pre-written Q&A pairs. Works without presenter present.

**Mode B: Presenter Assistant with Voice Recognition + TTS Response (for live 20-min slot)**
Run locally on presenter's laptop during the live session. Captures attendee voice from Gather Town proximity chat via Web Speech API + virtual audio routing, automatically matches to Q&A, and responds with pre-generated TTS audio played back directly into Gather Town. Text answers also displayed for manual copy/paste fallback. Solves the English communication barrier with zero typing required.

### Why This Works

- TICKET_205 already contains **182 curated Q&A pairs** covering every release and general project questions
- Gather Town supports **embedded HTTPS websites** via iframe - attendees interact like a normal website
- Web Speech API provides browser-native speech-to-text with zero dependencies
- Pre-generated TTS audio enables instant voice responses without typing
- Browser SpeechSynthesis API provides zero-storage TTS fallback for booth mode
- PulseAudio sink isolation prevents audio feedback loops between STT and TTS
- Pure client-side implementation: zero cost, zero backend, zero failure modes
- On-brand: deterministic, zero-dependency system mirrors NexusFix design philosophy

---

## Architecture

### Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Frontend | Static HTML + CSS + JavaScript | No build tools, no framework, embeddable in iframe |
| Search | Client-side keyword matching | No backend, instant response |
| Speech-to-Text | Web Speech API (Chrome native) | Zero dependencies, browser-built-in |
| Text-to-Speech (Booth) | Browser SpeechSynthesis API | Zero storage, zero dependencies, real-time |
| Text-to-Speech (Presenter) | Pre-generated edge-tts .mp3 files | High quality, zero latency, offline capable |
| TTS Generation | edge-tts (Microsoft Azure, free) | High quality Neural voices, Python CLI, SSML support |
| Audio Routing | PulseAudio dual-sink isolation (Linux) | Separates STT input from TTS output, prevents feedback loop |
| Data | Embedded JSON (from TICKET_205) | Single file, no API calls |
| Hosting | GitHub Pages (booth) + localhost (presenter) | Dual deployment |
| Deployment | `/docs/chatbot/` or separate `gh-pages` branch | Minimal repo impact |

### Architecture - Mode A: Booth (Attendee Self-Service)

```
Attendee -> Gather Town iframe -> GitHub Pages (static) -> Client-side JS
                                                           |-- Q&A JSON embedded
                                                           |-- Keyword search
                                                           |-- Category filter
                                                           +-- Browser SpeechSynthesis (read answer aloud)
```

### Architecture - Mode B: Presenter Assistant (Live Session + TTS Response)

```
Attendee speaks English in Gather Town proximity chat
         |
         v
Gather Town audio output -> PulseAudio "GatherIn" sink
         |                         |
         v                         v
  Presenter hears via         Monitor of GatherIn -> Chrome Speech API (STT)
  headphones/speakers                |
                                     v
                          Speech-to-text -> transcript displayed
                                     |
                                     v
                          Auto-search 182 Q&A -> matched answer displayed
                                     |
                                     v
                          ┌──────────┴──────────┐
                          v                      v
                    [Play] button          [Copy] button (fallback)
                          |                      |
                          v                      v
                    Pre-generated .mp3     Paste text into
                    plays to "TTSOut"      Gather Town chat
                    sink
                          |
                          v
                    TTSOut -> virtual mic -> Gather Town microphone input
                          |
                          v
                    Attendee hears English TTS answer directly
```

**Key**: Speech API listens on GatherIn sink. TTS plays on TTSOut sink. The two sinks are isolated - no feedback loop.

### Virtual Audio Routing Setup (Linux) - Dual-Sink Isolation

Two isolated PulseAudio sinks prevent the audio feedback loop between STT (Speech-to-Text) and TTS (Text-to-Speech). The Speech API only hears attendee voice; TTS output only goes to Gather Town.

```
Audio Flow Diagram:

  Gather Town output ──> GatherIn sink ──> Monitor of GatherIn ──> Speech API (STT)
                              |
                              +──> Presenter headphones (optional loopback)

  TTS .mp3 playback ──> TTSOut sink ──> Monitor of TTSOut ──> Virtual Mic ──> Gather Town mic input
                                                                               (attendee hears answer)

  Speech API CANNOT hear TTSOut (isolated sink)
  TTS CANNOT trigger on GatherIn (separate output)
```

```bash
# === PulseAudio Dual-Sink Setup Script ===

# 1. Create GatherIn sink (receives Gather Town audio output)
pactl load-module module-null-sink sink_name=GatherIn \
  sink_properties=device.description="GatherIn"

# 2. Create TTSOut sink (receives TTS playback)
pactl load-module module-null-sink sink_name=TTSOut \
  sink_properties=device.description="TTSOut"

# 3. Route Gather Town audio to GatherIn:
#    In pavucontrol -> Playback tab -> find Chrome (Gather Town tab)
#    -> set output to "GatherIn"

# 4. Chrome Speech API microphone:
#    Settings > Privacy > Site Settings > Microphone
#    -> select "Monitor of GatherIn"
#    (Speech API now ONLY hears attendee voice from Gather Town)

# 5. TTS audio output:
#    presenter.html plays .mp3 files to TTSOut sink
#    (configured via AudioContext.setSinkId or pactl move-sink-input)

# 6. Route TTS to Gather Town microphone input:
#    Create loopback from TTSOut monitor to virtual mic source
pactl load-module module-loopback \
  source=TTSOut.monitor \
  sink_name=GatherMicInput
#    In pavucontrol -> Recording tab -> find Chrome (Gather Town tab)
#    -> set input to "Monitor of TTSOut"

# 7. (Optional) Also hear TTS through presenter's headphones:
pactl load-module module-loopback \
  source=TTSOut.monitor \
  sink=<hardware-output-sink>

# === Verify Isolation ===
# Test: play TTS -> Speech API transcript should NOT show any text
# Test: speak into Gather Town -> TTS should NOT auto-trigger
```

**Important**: The presenter hears Gather Town audio through their normal hardware output. The GatherIn sink is only for the Speech API tap. The two sinks (GatherIn and TTSOut) are completely isolated from each other.

---

## Q&A Data Source

### From TICKET_205

| Section | Questions | Topics |
|---------|-----------|--------|
| General Project Q&A | 16 | Motivation, audience, production status, roadmap, licensing, lessons learned |
| v1.0.0 | 10 | C++23 choice, architecture, testing strategy |
| v0.1.0 | 10 | Parser foundation, zero-copy, consteval |
| v0.1.1 | 11 | PMR pools, C++11 vs C++23, cross-platform |
| v0.1.2 | 10 | CMake, FetchContent, install/export |
| v0.1.4 | 10 | CI/CD, version management, sanitizers |
| v0.1.5 | 10 | std::construct_at, object construction |
| v0.1.6 | 12 | MPSC queue, Disruptor pattern |
| v0.1.7 | 11 | SBE binary encoding |
| v0.1.8 | 10 | Scope guards, string hash, source_location |
| v0.1.9 | 10 | Compile-time MsgType dispatch |
| v0.1.10 | 10 | Compile-time optimization roadmap |
| v0.1.11 | 10 | C++23 quick wins, [[assume]] |
| v0.1.12 | 10 | Ranges, deducing this, std::print |
| v0.1.13 | 12 | Structural index, SIMD two-stage parsing |
| v0.1.14 | 10 | mimalloc, per-session heap |
| v0.1.15 | 10 | xsimd, portable SIMD |
| **Total** | **182** | |

### Data Format

```json
{
  "categories": [
    {
      "id": "general",
      "label": "General",
      "icon": "💡",
      "questions": [
        {
          "q": "What motivated you to build NexusFix?",
          "a": "QuickFIX was designed in the early 2000s...",
          "a_short": "QuickFIX was designed in the early 2000s and doesn't leverage modern C++ performance features.",
          "keywords": ["motivation", "why", "quickfix", "build", "started"],
          "audio_short": "audio/general_q01_short.mp3",
          "audio_full": "audio/general_q01_full.mp3"
        }
      ]
    },
    {
      "id": "simd",
      "label": "SIMD",
      "icon": "⚡",
      "questions": [...]
    }
  ]
}
```

**New fields**:
- `a_short` - 1-2 sentence summary of the answer (core conclusion, used for TTS short version)
- `audio_short` - Pre-generated TTS of `a_short` (~5-10 seconds, default playback)
- `audio_full` - Pre-generated TTS of full `a` (~30-90 seconds, on-demand playback)

---

## UI Design

### Layout

**Booth Mode (for attendees in Gather Town iframe):**

```
┌──────────────────────────────────────────────────┐
│  NexusFix Interactive Q&A                    🔍  │
│  ────────────────────────────────────────────     │
│                                                   │
│  Topics:                                          │
│  [General] [SIMD] [PMR] [SBE] [Queue]           │
│  [Index] [CMake] [CI/CD] [C++23] [All 182]      │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │  Welcome to NexusFix Q&A!                 │   │
│  │    I have 182 pre-answered questions      │   │
│  │    about the project.                     │   │
│  │                                           │   │
│  │    Pick a topic above, or type a          │   │
│  │    keyword below.                         │   │
│  │                                           │   │
│  │    Popular questions:                     │   │
│  │    > Why not just use QuickFIX?           │   │
│  │    > How does SIMD scanning work?         │   │
│  │    > What's the P99 latency?              │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────┐  [Ask]  │
│  │ Type keyword or question...         │         │
│  └─────────────────────────────────────┘         │
│                                                   │
│  github.com/SilverstreamsAI/NexusFix        v1.0 │
└──────────────────────────────────────────────────┘
```

**Presenter Assistant Mode (local, with voice recognition + TTS response):**

```
┌──────────────────────────────────────────────────────────────┐
│  NexusFix Presenter Assistant                          v1.0  │
│  ────────────────────────────────────────────────────────     │
│                                                               │
│  ┌─ Live Transcript ───────────────────────────────────────┐ │
│  │                                                         │ │
│  │  "so how does the structural index compare to          │ │
│  │   a hash map approach for field lookup"                 │ │
│  │                                                    ⏺ ● │ │
│  └─────────────────────────────────────────────────────────┘ │
│   [Listen]  [Stop]  [Clear]            Status: Listening...  │
│                                                               │
│  ┌─ Auto-Matched Q&A (3 results) ─────────────────────────┐ │
│  │                                                         │ │
│  │  #1 (score: 35) v0.1.13 Q9                             │ │
│  │  Q: How does this compare to a hash map approach        │ │
│  │     for field lookup?                                   │ │
│  │  A: Hash map (std::unordered_map<int, string_view>)     │ │
│  │     has ~25ns per lookup due to hashing and potential    │ │
│  │     collisions. Our index array has ~2.3ns per          │ │
│  │     lookup (direct array access)...                     │ │
│  │                         [Play Short] [Play Full] [Copy] │ │
│  │                                                         │ │
│  │  #2 (score: 20) v0.1.13 Q1                             │ │
│  │  Q: What does "simdjson-style" mean in FIX context?     │ │
│  │  A: simdjson's key insight is separating...             │ │
│  │                         [Play Short] [Play Full] [Copy] │ │
│  │                                                         │ │
│  │  #3 (score: 12) v0.1.13 Q7                             │ │
│  │  Q: How does 2.3ns per-field compare to state of art?   │ │
│  │  A: It's competitive with binary protocol...            │ │
│  │                         [Play Short] [Play Full] [Copy] │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  TTS Output: [Auto-play short] [Manual only]   Playing... ▶  │
│                                                               │
│  Topics:                                                      │
│  [General] [SIMD] [PMR] [SBE] [Queue]                       │
│  [Index] [CMake] [CI/CD] [C++23] [All 182]                  │
│                                                               │
│  ┌──────────────────────────────────────────────┐  [Search]  │
│  │ Or type keyword manually...                   │           │
│  └──────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

**TTS Controls**:
- `[Play Short]` - Play 5-10s summary answer via TTSOut sink (attendee hears it)
- `[Play Full]` - Play full 30-90s answer via TTSOut sink
- `[Auto-play short]` toggle - Automatically play short answer for #1 match when score > threshold
- `[Manual only]` toggle - Only play when presenter clicks Play
- Playing indicator shows current playback status
- Clicking any Play while another is playing stops the previous

### Interaction Modes

**Mode 1: Category Browse**
- Click topic button -> show all Q&A in that category
- Click a question -> expand answer

**Mode 2: Keyword Search**
- Type keyword (e.g., "PMR", "latency", "SIMD")
- Fuzzy match against question text + keywords array
- Show ranked results

**Mode 3: Popular Questions**
- Landing page shows 5-8 most likely questions
- One-click access to answers

**Mode 4: Voice Recognition (Presenter Assistant only)**
- Click "Listen" button to start capturing audio
- Web Speech API transcribes speech to text in real-time
- Transcript auto-populates the search box
- Q&A results update live as speech is recognized
- Click "Stop" to end capture

**Mode 5: TTS Voice Response**
- **Booth mode**: Click speaker icon on any answer -> Browser SpeechSynthesis reads answer aloud (zero storage)
- **Presenter mode**: Click [Play Short] -> pre-generated .mp3 plays via TTSOut sink -> attendee hears answer in Gather Town
- **Presenter mode**: Click [Play Full] -> full-length .mp3 plays for detailed technical answers
- **Auto-play** (optional): When enabled, top match (score > threshold) automatically plays short answer

### Visual Design

| Element | Spec |
|---------|------|
| Theme | Dark mode (developer-friendly, matches conference vibe) |
| Font | Monospace for code snippets, sans-serif for text |
| Colors | Dark background (#1a1a2e), accent blue (#0f3460), text white |
| Code blocks | Syntax highlighted (highlight.js, inline) |
| Responsive | Must work in Gather Town iframe (variable width) |
| Animation | Typing effect for bot responses (optional, subtle) |

---

## Search Algorithm

Client-side keyword matching, no AI required:

```javascript
function search(query, qaData) {
    const terms = query.toLowerCase().split(/\s+/);

    return qaData
        .map(item => ({
            ...item,
            score: calculateScore(terms, item)
        }))
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5);
}

function calculateScore(terms, item) {
    let score = 0;
    const qLower = item.q.toLowerCase();
    const aLower = item.a.toLowerCase();

    for (const term of terms) {
        // Exact keyword match (highest weight)
        if (item.keywords?.includes(term)) score += 10;
        // Question text match
        if (qLower.includes(term)) score += 5;
        // Answer text match
        if (aLower.includes(term)) score += 2;
    }
    return score;
}
```

---

## Voice Recognition (Presenter Assistant Mode)

### Web Speech API Integration

```javascript
class VoiceRecognizer {
    constructor(onTranscript) {
        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = true;       // Don't stop after one sentence
        this.recognition.interimResults = true;   // Show partial results as user speaks
        this.recognition.lang = 'en-US';
        this.onTranscript = onTranscript;

        this.recognition.onresult = (event) => {
            let interim = '';
            let final = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    final += transcript;
                } else {
                    interim += transcript;
                }
            }

            // Display interim transcript (gray, updating)
            this.onTranscript({ interim, final });

            // Auto-search when a final result arrives
            if (final) {
                searchQA(final);  // Triggers Q&A matching
            }
        };

        this.recognition.onerror = (event) => {
            // 'no-speech' is expected during silence - just continue
            if (event.error !== 'no-speech') {
                console.error('Speech error:', event.error);
            }
        };

        // Auto-restart on end (continuous listening)
        this.recognition.onend = () => {
            if (this.listening) {
                this.recognition.start();
            }
        };
    }

    start() {
        this.listening = true;
        this.recognition.start();
    }

    stop() {
        this.listening = false;
        this.recognition.stop();
    }
}
```

### How It Works

1. Presenter clicks **[Listen]** button
2. Chrome requests microphone permission (select PulseAudio monitor source)
3. Web Speech API captures audio from Gather Town output
4. Speech is transcribed to English text in real-time
5. Interim results shown in gray (updating as speaker talks)
6. Final results trigger automatic Q&A search
7. Top 3 matched answers displayed with **[Copy]** buttons
8. Presenter clicks [Copy] -> pastes into Gather Town text chat

### Transcript Display

```
Live transcript panel:
- Interim text: light gray, italic (updating in real-time)
- Final text: white, bold (confirmed recognition)
- Auto-scroll to latest text
- [Clear] button to reset transcript
- Red dot indicator when actively listening
```

### Limitations and Mitigations

| Limitation | Mitigation |
|------------|------------|
| Web Speech API needs internet | Conference venue has internet; offline fallback = manual typing |
| Recognition accuracy varies with accents | Keyword search is fuzzy; partial match still finds answers |
| Cannot distinguish presenter from attendee audio | Dual-sink isolation: Speech API on GatherIn, TTS on TTSOut |
| Browser may prompt for mic permission | Pre-approve during setup before conference |
| TTS feedback loop (TTS output re-captured by STT) | Dual PulseAudio sink isolation (GatherIn vs TTSOut) |

---

## TTS Voice Response System

### Strategy: Two-Tier TTS

| Mode | Engine | Storage | Quality | Latency |
|------|--------|---------|---------|---------|
| **Booth (attendees)** | Browser SpeechSynthesis API | Zero | Medium (robotic) | Real-time |
| **Presenter (live)** | Pre-generated edge-tts .mp3 | ~150MB local | High (neural voice) | Zero (pre-loaded) |

**Rationale**: Booth mode prioritizes zero-deployment (no audio files on GitHub Pages). Presenter mode prioritizes quality and reliability (pre-generated, offline-capable, verified pronunciation).

### Answer Versions

Each of the 182 Q&A pairs has two TTS versions:

| Version | Content | Duration | Use Case |
|---------|---------|----------|----------|
| **Short** | `a_short` field: 1-2 sentence core conclusion | 5-10s | Default playback, quick response |
| **Full** | `a` field: complete answer with technical details | 30-90s | On-demand, detailed explanation |

**Example**:
- **Short**: "Our structural index uses direct array access at 2.3ns per field, which is 10x faster than hash map lookup."
- **Full**: "Hash map (std::unordered_map<int, string_view>) has approximately 25ns per lookup due to hashing overhead and potential hash collisions. Our index array achieves 2.3ns per lookup through direct array access with the tag number as index..."

### TTS Engine: edge-tts

```bash
# Installation
pip install edge-tts

# Single file generation
edge-tts --text "Our structural index uses direct array access..." \
         --voice en-US-GuyNeural \
         --write-media audio/v0113_q09_short.mp3

# List available voices
edge-tts --list-voices | grep en-US

# Recommended voices:
#   en-US-GuyNeural      - Male, professional, clear (recommended)
#   en-US-AndrewNeural   - Male, warm
#   en-US-JennyNeural    - Female, professional
```

**Why edge-tts**:
- Free (uses Microsoft Azure Neural TTS, no API key required)
- High quality neural voices (near-human)
- Python CLI - one command per file
- SSML support for controlling pronunciation of technical terms
- 182 answers at ~50,000 total characters is well within limits

### SSML for Technical Terms

Technical terms like "SIMD", "PMR", "SBE" may be mispronounced. Use SSML to control pronunciation:

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-GuyNeural">
    Our structural index uses
    <phoneme alphabet="ipa" ph="es ai em di">SIMD</phoneme>
    instructions for parallel
    <phoneme alphabet="ipa" ph="es ou eitS">SOH</phoneme>
    byte scanning.
    The
    <phoneme alphabet="ipa" ph="pi em ar">PMR</phoneme>
    memory pool provides zero-allocation parsing.
  </voice>
</speak>
```

### Batch Generation Script

```python
#!/usr/bin/env python3
"""Generate TTS audio files for all 182 Q&A pairs."""

import asyncio
import json
import edge_tts

VOICE = "en-US-GuyNeural"
OUTPUT_DIR = "docs/chatbot/audio"

async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)

async def main():
    with open("docs/chatbot/qa-data.js", "r") as f:
        # Strip "const qaData = " prefix and trailing ";"
        content = f.read()
        json_str = content[content.index("{"):content.rindex("}") + 1]
        data = json.loads(json_str)

    tasks = []
    for category in data["categories"]:
        for i, qa in enumerate(category["questions"], 1):
            qa_id = f"{category['id']}_q{i:02d}"

            # Short version (a_short field)
            if qa.get("a_short"):
                tasks.append(generate_audio(
                    qa["a_short"],
                    f"{OUTPUT_DIR}/{qa_id}_short.mp3"
                ))

            # Full version (a field)
            tasks.append(generate_audio(
                qa["a"],
                f"{OUTPUT_DIR}/{qa_id}_full.mp3"
            ))

    # Generate all audio files (parallel, ~5 concurrent)
    semaphore = asyncio.Semaphore(5)
    async def limited(task):
        async with semaphore:
            await task
    await asyncio.gather(*[limited(t) for t in tasks])

    print(f"Generated {len(tasks)} audio files in {OUTPUT_DIR}/")

asyncio.run(main())
```

### Audio File Storage

```
Pre-generated audio (presenter mode, local only):

182 short versions:  ~5s each  = ~15 min total = ~15 MB
182 full versions:   ~45s each = ~135 min total = ~135 MB
Total: ~364 files, ~150 MB

Storage location: docs/chatbot/audio/ (gitignored, local only)
NOT committed to public repo.
```

| Storage | Booth Mode | Presenter Mode |
|---------|-----------|----------------|
| GitHub Pages | No audio files (SpeechSynthesis API) | N/A |
| Local (presenter laptop) | N/A | `docs/chatbot/audio/*.mp3` (~150MB) |

### TTS Playback Integration (tts.js)

```javascript
class TTSPlayer {
    constructor(outputSinkId) {
        this.audioContext = new AudioContext();
        this.currentAudio = null;
        this.outputSinkId = outputSinkId; // TTSOut sink ID
    }

    async playAnswer(qaItem, version = 'short') {
        // Stop any current playback
        this.stop();

        const audioPath = version === 'short'
            ? qaItem.audio_short
            : qaItem.audio_full;

        if (audioPath) {
            // Presenter mode: play pre-generated .mp3
            this.currentAudio = new Audio(audioPath);
            if (this.outputSinkId) {
                await this.currentAudio.setSinkId(this.outputSinkId);
            }
            await this.currentAudio.play();
        } else {
            // Booth mode fallback: Browser SpeechSynthesis
            const text = version === 'short'
                ? (qaItem.a_short || qaItem.a)
                : qaItem.a;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.9; // Slightly slower for clarity
            speechSynthesis.speak(utterance);
        }
    }

    stop() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
        speechSynthesis.cancel();
    }
}
```

### Audio Output Routing (setSinkId)

The `HTMLMediaElement.setSinkId()` API allows JavaScript to route audio output to a specific device (sink):

```javascript
// Enumerate audio output devices
const devices = await navigator.mediaDevices.enumerateDevices();
const outputs = devices.filter(d => d.kind === 'audiooutput');

// Find TTSOut sink
const ttsSink = outputs.find(d => d.label.includes('TTSOut'));

// Route audio to TTSOut
const audio = new Audio('audio/general_q01_short.mp3');
await audio.setSinkId(ttsSink.deviceId);
await audio.play();
// Audio goes to TTSOut -> Gather Town mic input (attendee hears it)
// Speech API on GatherIn does NOT hear it
```

**Browser support**: `setSinkId()` is supported in Chrome 49+ (2016). Works in all modern Chromium browsers.

### Audio Feedback Loop Prevention (Defense in Depth)

TTS output could be re-captured by Speech API, creating an infinite loop: TTS plays answer -> STT recognizes it as a new question -> matches Q&A -> plays again. Three layers of defense prevent this:

```
┌─────────────────────────────────────────────────────────────────────┐
│  L1: PulseAudio Sink Isolation (hardware-level)                     │
│  STT listens on GatherIn sink. TTS plays on TTSOut sink.           │
│  Physically separate audio paths - STT cannot hear TTS.            │
│  Reliability: highest. Complexity: PulseAudio config required.     │
├─────────────────────────────────────────────────────────────────────┤
│  L2: State Lock + STT Pause + Silence Buffer (software-level)      │
│  Pause Speech API during TTS playback + 500ms post-silence.        │
│  Works even if L1 is misconfigured. Core defense line.             │
│  Reliability: high. Complexity: ~30 lines in tts.js.               │
├─────────────────────────────────────────────────────────────────────┤
│  L3: Content Fingerprint Dedup (fallback)                           │
│  If recognized text is >50% similar to last played answer           │
│  within 5 seconds, discard as echo.                                │
│  Reliability: medium. Complexity: ~20 lines in voice.js.           │
└─────────────────────────────────────────────────────────────────────┘
```

**All three layers are implemented. Total: ~100 lines of code.**

#### L1: PulseAudio Sink Isolation

Covered in "Virtual Audio Routing Setup" section above. `GatherIn` sink for STT input, `TTSOut` sink for TTS output, completely isolated.

#### L2: State Lock + STT Pause + Silence Buffer

```javascript
// In tts.js - AudioPipeline class
class AudioPipeline {
    constructor(recognizer, ttsPlayer) {
        this.recognizer = recognizer;
        this.ttsPlayer = ttsPlayer;
        this.ttsPlaying = false;
    }

    onSpeechResult(transcript) {
        // L2: TTS playing -> ignore ALL speech results
        if (this.ttsPlaying) return;

        // L3: Echo detection (see below)
        if (this.isEcho(transcript)) return;

        const matches = search(transcript);
        if (matches.length > 0) {
            this.playAnswer(matches[0]);
        }
    }

    async playAnswer(qa) {
        // Step 1: Lock state
        this.ttsPlaying = true;

        // Step 2: Pause Speech API (stop buffering audio)
        this.recognizer.pause();

        try {
            // Step 3: Play TTS
            this.lastPlayedText = qa.a_short || qa.a;
            this.lastPlayedTime = Date.now();
            await this.ttsPlayer.play(qa);
        } finally {
            // Step 4: Post-silence buffer (drain any residual echo)
            await new Promise(resolve => setTimeout(resolve, 500));

            // Step 5: Resume Speech API
            this.ttsPlaying = false;
            this.recognizer.resume();
        }
    }
}
```

**Why pause + silence buffer**: Speech API has an internal audio buffer. Even after TTS stops playing, the buffer may contain 200-500ms of residual audio (echo, reverb). The 500ms silence window ensures the buffer drains before STT resumes.

#### L3: Content Fingerprint Dedup

```javascript
// In voice.js - echo detection
isEcho(transcript) {
    if (!this.lastPlayedText) return false;
    if (Date.now() - this.lastPlayedTime > 5000) return false;

    const wordsA = new Set(transcript.toLowerCase().split(/\s+/));
    const wordsB = new Set(this.lastPlayedText.toLowerCase().split(/\s+/));
    const overlap = [...wordsA].filter(w => wordsB.has(w)).length;
    const similarity = overlap / Math.max(wordsA.size, wordsB.size);

    if (similarity > 0.5) {
        console.log(`Echo detected (${(similarity * 100).toFixed(0)}% match), ignoring`);
        return true;
    }
    return false;
}
```

**Why 50% threshold**: TTS output re-captured by STT will have imperfect transcription (speech recognition errors), so exact match won't work. 50% word overlap reliably catches echoes while unlikely to match genuine attendee questions.

**Why 5-second window**: Answers are typically 5-10s (short) or 30-90s (full). The 5-second window covers the short version. For full versions, L2 (state lock) is the primary defense since STT is paused for the entire playback duration.

---

## File Structure

```
docs/chatbot/
├── index.html          # Booth mode (entry point, deployed to GitHub Pages)
├── presenter.html      # Presenter assistant mode (voice + TTS, local only)
├── style.css           # Shared dark theme styles
├── app.js              # Search logic, UI interaction, category filters
├── voice.js            # Web Speech API integration (presenter mode only)
├── tts.js              # TTS playback + audio sink routing (new)
├── qa-data.js          # All 182 Q&A pairs as JSON (includes a_short + audio paths)
├── generate_audio.py   # Batch TTS generation script (edge-tts)
├── audio/              # Pre-generated .mp3 files (gitignored, local only)
│   ├── general_q01_short.mp3
│   ├── general_q01_full.mp3
│   ├── ...
│   ├── v0115_q10_short.mp3
│   ├── v0115_q10_full.mp3
│   └── manifest.json   # Audio file <-> Q&A ID mapping + checksums
└── README.md           # Build/deploy/audio routing instructions
```

Single directory, no build step, no dependencies, no node_modules.

- `index.html` - Deployed to GitHub Pages, embedded in Gather Town booth iframe (uses Browser SpeechSynthesis for TTS)
- `presenter.html` - Run locally (`python3 -m http.server`), NOT deployed publicly (uses pre-generated .mp3)
- `audio/` - Gitignored, ~150MB, generated locally by `generate_audio.py`

---

## Implementation Tasks

### Phase 1: Data Extraction
- [ ] Parse TICKET_205 Q&A section into structured JSON
- [ ] Assign categories to each Q&A pair
- [ ] Add keyword arrays for search optimization
- [ ] Write `a_short` (1-2 sentence summary) for each of the 182 answers
- [ ] Validate: 182 questions, no missing answers, no missing `a_short`

### Phase 2: Core UI (Booth Mode)
- [ ] Create `index.html` with chat-style layout
- [ ] Implement dark theme CSS
- [ ] Category filter buttons
- [ ] Question list with expandable answers
- [ ] Code block syntax highlighting
- [ ] Speaker icon on answers (triggers Browser SpeechSynthesis)

### Phase 3: Search
- [ ] Implement client-side keyword search
- [ ] Search-as-you-type with debounce
- [ ] Result ranking and highlighting
- [ ] "No results" fallback with suggested categories

### Phase 4: Voice Recognition (Presenter Mode)
- [ ] Create `presenter.html` with split layout (transcript + Q&A results)
- [ ] Implement `voice.js` with Web Speech API
- [ ] Live transcript display (interim gray / final white)
- [ ] Auto-search on final transcript
- [ ] [Copy] button on each matched answer (copies to clipboard)
- [ ] [Listen] / [Stop] / [Clear] controls
- [ ] Status indicator (listening / stopped / error)
- [ ] Auto-restart on recognition end (continuous mode)

### Phase 4.5: TTS Audio Generation (New)
- [ ] Install edge-tts: `pip install edge-tts`
- [ ] Select voice: test en-US-GuyNeural vs en-US-AndrewNeural
- [ ] Create SSML pronunciation rules for technical terms (SIMD, PMR, SBE, SOH, etc.)
- [ ] Write `generate_audio.py` batch generation script
- [ ] Generate 182 short .mp3 files (~15MB total)
- [ ] Generate 182 full .mp3 files (~135MB total)
- [ ] Review: listen to 10-20 samples, fix mispronunciations
- [ ] Generate `manifest.json` (file mapping + checksums)
- [ ] Add `audio/` to `.gitignore`

### Phase 4.6: TTS Playback + Feedback Loop Prevention (New)
- [ ] Implement `tts.js` with TTSPlayer class
- [ ] Add [Play Short] / [Play Full] buttons to presenter.html results
- [ ] Implement `setSinkId()` routing to TTSOut sink
- [ ] Add auto-play toggle (auto-play short for top match)
- [ ] Add playback status indicator (playing / stopped)
- [ ] Stop current playback when new answer is played
- [ ] Booth mode: integrate Browser SpeechSynthesis as fallback
- [ ] **L2**: Implement AudioPipeline state lock (pause STT during TTS playback)
- [ ] **L2**: Add 500ms post-silence buffer before resuming STT
- [ ] **L3**: Implement echo detection (content fingerprint dedup in voice.js)
- [ ] **Test**: Play TTS -> verify STT does NOT produce transcript during playback
- [ ] **Test**: Play TTS -> verify no auto-triggered Q&A match after playback ends

### Phase 5: Audio Routing Setup (Updated)
- [ ] Document PulseAudio dual-sink setup (GatherIn + TTSOut)
- [ ] Create `setup_audio.sh` script for one-command sink creation
- [ ] Test: Gather Town audio -> GatherIn sink -> Speech API (STT)
- [ ] Test: TTS .mp3 -> TTSOut sink -> Gather Town mic input
- [ ] **Verify isolation**: TTS playback does NOT trigger Speech API
- [ ] **Verify isolation**: Speech API does NOT capture TTS output
- [ ] Test recognition accuracy with conference-style speech
- [ ] Document fallback: manual typing when voice fails

### Phase 6: Polish
- [ ] Welcome message with popular questions
- [ ] Smooth scroll and expand animations
- [ ] Mobile/iframe responsive layout (booth mode)
- [ ] GitHub repo link and project branding
- [ ] Presenter mode: keyboard shortcut for [Listen] toggle
- [ ] Presenter mode: keyboard shortcut for [Play/Stop] toggle

### Phase 7: Deploy & Test
- [ ] Deploy `index.html` to GitHub Pages (booth mode, no audio files)
- [ ] Test iframe embedding (simulate Gather Town)
- [ ] Test `presenter.html` locally with `python3 -m http.server`
- [ ] End-to-end test: speak English -> transcript -> Q&A match -> TTS answer plays
- [ ] End-to-end test: attendee hears TTS answer in Gather Town
- [ ] Verify audio isolation: no feedback loop during continuous operation
- [ ] Verify HTTPS and X-Frame-Options allow embedding
- [ ] Dry run: simulate 20-minute presentation with voice + TTS assistant

---

## Deployment Architecture: Server-side vs Laptop-side

### Design Analogy

The booth operates like a **24/7 unmanned convenience store with an occasional live attendant**:

- **Convenience store** (always open): Poster, diagrams, video, text-based Q&A chatbot. Attendees browse, search, and read answers on their own. Pure static content, no backend required.
- **Live attendant** (only when presenter is online): Voice interaction via STT + TTS. Attendees speak English, get spoken answers back. Only available during the 20-minute live session when the presenter's laptop is online and configured.

The store is always open. The attendant just adds a voice service window. Text Q&A works 24/7 regardless.

```
┌─────────────────────────────────────────────────────┐
│              Booth = Convenience Store                │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Self-service (24/7, no backend)                │ │
│  │  - Poster PDF         (view)                    │ │
│  │  - Architecture image (view)                    │ │
│  │  - YouTube video      (watch)                   │ │
│  │  - Q&A Chatbot        (type keyword -> answer)  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Voice service window (only when laptop online) │ │
│  │  - Attendee speaks    (STT on laptop)           │ │
│  │  - Answer plays back  (TTS from laptop)         │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### What Lives Where

Gather Town booth has two fundamentally different data paths. Understanding which content is server-hosted (always available) vs laptop-dependent (only during live session) is critical for deployment planning.

```
┌──────────────────────────────────────────────────────────────────────┐
│                  SERVER-SIDE (Gather Town + CDN)                      │
│                  Always available, 24/7, presenter offline OK        │
│                                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────────┐ │
│  │ Poster PDF │  │ Architecture│  │ YouTube    │  │ Q&A Chatbot   │ │
│  │ (Document) │  │ Diagram    │  │ Video      │  │ (Website)     │ │
│  │            │  │ (Image)    │  │            │  │               │ │
│  │ Uploaded   │  │ Uploaded   │  │ YouTube    │  │ GitHub Pages  │ │
│  │ to Gather  │  │ to Gather  │  │ CDN        │  │ (static HTML) │ │
│  │ Town       │  │ Town       │  │            │  │               │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────────┘ │
│                                                                       │
│  Attendee access: click object -> view directly in Gather Town       │
│  No dependency on presenter's laptop or internet connection          │
│                                                                       │
├──────────────────────────────────────────────────────────────────────┤
│                  LAPTOP-SIDE (Presenter's local machine)             │
│                  Only during live 20-min session, presenter online   │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Gather Town Proximity Voice Chat (WebRTC P2P)                  │ │
│  │ Attendee speaks -> WebRTC -> directly to presenter's browser   │ │
│  │ (No server-side access to this audio stream)                   │ │
│  └───────────────────────┬────────────────────────────────────────┘ │
│                           │                                          │
│                           v                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Presenter's Laptop                                             │ │
│  │                                                                 │ │
│  │  Chrome Tab 1: Gather Town                                     │ │
│  │    - Receives attendee voice (WebRTC)                          │ │
│  │    - Sends TTS audio back as microphone input                  │ │
│  │                                                                 │ │
│  │  Chrome Tab 2: presenter.html (localhost)                      │ │
│  │    - STT: attendee voice -> English text (Web Speech API)      │ │
│  │    - Search: text -> Q&A match (client-side)                   │ │
│  │    - TTS: matched answer -> .mp3 playback (edge-tts files)    │ │
│  │                                                                 │ │
│  │  PulseAudio: GatherIn sink + TTSOut sink (audio isolation)     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Attendee access: walk near booth -> proximity chat activates        │
│  Requires presenter to be in Gather Town with laptop configured      │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Why Voice Must Route Through Laptop

Gather Town proximity voice chat uses **WebRTC peer-to-peer**. The audio stream goes directly from attendee's browser to presenter's browser. There is no server-side hook, API, or webhook to intercept or process this audio. Therefore:

- STT (speech recognition) can only happen in the presenter's browser
- TTS (answer playback) can only be injected from the presenter's browser
- The entire STT -> Search -> TTS pipeline is laptop-local

### Why Voice Cannot Work 24/7 (WebRTC P2P Constraint)

The voice feature is **architecturally impossible** to make available 24/7. This is not a design choice but a fundamental constraint of WebRTC peer-to-peer:

```
Presenter ONLINE:   Attendee browser <--WebRTC P2P--> Presenter browser
                    Audio stream exists -> PulseAudio captures -> STT -> TTS

Presenter OFFLINE:  Attendee browser <--WebRTC P2P--> (nobody)
                    Connection never established -> no audio stream exists
```

**Analogy**: Like a phone call - if the other party is offline, the call is never established. There is no audio to intercept because no audio is ever transmitted.

**Alternatives considered and rejected**:

| Approach | Feasibility | Issue |
|----------|-------------|-------|
| Headless Chrome bot on server (Puppeteer) | Technically possible | Requires server with PulseAudio + Xvfb; see Mode C below |
| Gather Town WebSocket API | API exists for movement/chat | Audio streams are NOT exposed via WebSocket API |
| Server-side WebRTC client | Complex but possible | Depends on Gather Town's internal signaling protocol (undocumented) |

**Conclusion**: Text-based Q&A chatbot (Mode A) is the correct 24/7 solution. Voice (Mode B) is limited to the live session when the presenter's laptop is online and configured. This is an inherent P2P architectural constraint. **Mode C (server-hosted)** is a viable alternative if 24/7 voice is desired -- see below.

### Mode C: Server-Hosted Voice Assistant (Backup Plan)

**Goal**: Make voice STT + TTS available 24/7 by running the entire Mode B pipeline on a server instead of the presenter's laptop.

#### Gather Town Bot Policy (Investigated 2026-02-25)

Gather Town **officially supports bots** via their API ecosystem:

| Finding | Detail |
|---------|--------|
| **ToS on bots** | ToS prohibits "sending more messages than humanly possible" (anti-spam). Does NOT blanket-prohibit bots or automation. |
| **Official API** | HTTP API (beta) + WebSocket API with official npm packages (`@gathertown/gather-game-client`) |
| **API key system** | Gather issues API keys for programmatic access. Staff confirmed each bot needs its own key. |
| **Developer community** | Dedicated [Developers forum](https://forum.gather.town/c/developers/6) with API questions, tools, project showcases |
| **Known bot projects** | POAP distribution bots, conference bots (CodeCon), NPC/mascot bots, chatbots -- all showcased on Gather's own forum without restriction |

**Conclusion**: Bot accounts are well-established in the Gather Town ecosystem. No ToS risk for our use case.

#### Architecture

```
VPS (24/7):
    Xvfb (virtual display) + PulseAudio (virtual audio)
        -> Chrome (full, not headless -- WebRTC needs audio device)
            -> Logged into Gather Town with bot account
            -> Standing near poster booth (proximity chat active)
                -> Attendee speaks
                    -> WebRTC P2P to server Chrome
                    -> PulseAudio GatherIn sink -> Web Speech API (STT)
                    -> Client-side Q&A search
                    -> TTS .mp3 -> TTSOut sink -> WebRTC back to attendee
```

#### Server Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux (Ubuntu 22.04+) |
| CPU | 2 cores (Chrome + PulseAudio) |
| RAM | 2-4 GB |
| Display | Xvfb virtual framebuffer |
| Audio | PulseAudio with virtual sinks (same GatherIn + TTSOut setup) |
| Chrome | Full Chrome (not headless) -- WebRTC requires audio device access |
| Network | Stable connection, low latency to attendees |
| Duration | 3 days (conference duration) |
| Cost | ~$5-15 for a small VPS for 3 days |

#### Limitations

| Limitation | Mitigation |
|------------|------------|
| Web Speech API needs internet | Server has stable internet (better than laptop) |
| Bot must stay near booth | Use Gather WebSocket API to auto-position bot at booth coordinates |
| Chrome may crash over 3 days | Supervisor process (systemd) to auto-restart |
| Bot account needs conference ticket | Check if organizers provide bot/observer accounts |

#### Implementation Priority

**Mode C is a backup plan.** Mode A (text chatbot) + Mode B (laptop voice) are the primary deliverables. Mode C can be implemented later if:
- Mode B works well during testing and we want to extend it to 24/7
- A suitable VPS is available
- Conference organizers confirm bot accounts are acceptable

### Submission Timeline

| When | What | Submit To | Notes |
|------|------|-----------|-------|
| **Before conference** | Poster PDF | Gather Town admin upload | Organizers may upload for you |
| **Before conference** | Architecture diagram (PNG/SVG) | Gather Town admin upload | Object type: Image |
| **Before conference** | YouTube demo video URL | Gather Town admin config | Object type: Video |
| **Before conference** | Q&A Chatbot URL | Gather Town admin config | Object type: Website, GitHub Pages URL |
| **Before conference** | presenter.html + audio/ | Local laptop only | NOT uploaded anywhere |
| **Before conference** | setup_audio.sh | Local laptop only | PulseAudio configuration |
| **On-site (before live slot)** | Run setup_audio.sh | Local laptop terminal | Creates GatherIn + TTSOut sinks |
| **On-site (before live slot)** | Configure Chrome audio | Local laptop Chrome | Mic = Monitor of GatherIn, Output = TTSOut |

### Availability Matrix

| Content | During live session (20 min) | Rest of 3-day conference | After conference |
|---------|------------------------------|--------------------------|------------------|
| Poster PDF | Available | Available | Available (if booth persists) |
| Architecture diagram | Available | Available | Available |
| YouTube video | Available | Available | Available (YouTube) |
| Q&A Chatbot (text search) | Available | Available | Available (GitHub Pages) |
| Q&A Chatbot (voice TTS) | **Available** (laptop online) | **Not available** | Not available |
| Proximity voice chat | **Available** (laptop online) | Not available | Not available |

---

## Gather Town Booth Layout (Updated from TICKET_225)

| Object | Type | Content |
|--------|------|---------|
| 1 | Document | Main poster (Google Slides / PDF) |
| 2 | Image | Architecture diagram (pipeline, SIMD dispatch) |
| 3 | Video | Benchmark demo (YouTube, 3-5 min) |
| 4 | **Website** | **Q&A Chatbot (this ticket)** |

---

## Presenter Live Session Workflow

Step-by-step during the 20-minute presentation slot:

```
Before session:
1. Run setup_audio.sh (creates GatherIn + TTSOut PulseAudio sinks)
2. Open Gather Town in Chrome (Tab 1)
   - Set audio output to "GatherIn" (pavucontrol -> Playback)
   - Set audio input to "Monitor of TTSOut" (pavucontrol -> Recording)
3. Open presenter.html in Chrome (Tab 2) - localhost:8000/presenter.html
   - Set microphone to "Monitor of GatherIn" (Chrome Settings)
   - Set audio output to "TTSOut" (via setSinkId in tts.js)
4. Click [Listen] in presenter.html
5. Verify setup:
   a. Speak a test phrase in Gather Town -> transcript appears (STT works)
   b. Click [Play Short] on any answer -> audio plays (TTS works)
   c. Verify: TTS playback does NOT appear in transcript (isolation works)

During session:
1. Attendee walks to booth in Gather Town
2. Attendee speaks: "How does the structural index work?"
3. Audio flows: Gather Town -> GatherIn sink -> Monitor -> Speech API
4. presenter.html shows transcript: "how does the structural index work"
5. Auto-matched Q&A appears: v0.1.13 Q1 (score: 35)
6. Option A (TTS): Click [Play Short] -> attendee hears TTS answer directly
   Option B (TTS): If auto-play enabled, short answer plays automatically
   Option C (Text): Click [Copy] -> paste into Gather Town text chat
7. For follow-up: Click [Play Full] for detailed answer
8. Attendee hears/reads the answer

If voice recognition fails:
1. Read Chrome Live Caption (built-in subtitle) to understand the question
2. Switch to presenter.html, type keywords manually
3. Click [Play Short] or [Copy] + paste into Gather Town

If TTS playback fails:
1. Fall back to [Copy] + paste into Gather Town text chat
2. All text answers remain fully functional regardless of audio
```

---

## End-to-End Latency Analysis

Breakdown of each stage in the voice pipeline (Mode B: Presenter Assistant):

```
Attendee speaks
    -> WebRTC P2P transport              ~50-150ms  (network, depends on geography)
    -> Chrome audio decode + output      ~5-10ms
    -> PulseAudio route to GatherIn      ~2-5ms    (kernel-space audio routing)
    -> Monitor of GatherIn tap           ~0ms      (same-sink direct tap)
    -> Web Speech API (STT)              ~500-2000ms (Google server round-trip + recognition)
    -> Client-side keyword search        ~1-5ms    (in-memory operation)
    -> TTS .mp3 playback start           ~10-50ms  (local file, pre-loaded)
    -> PulseAudio TTSOut routing         ~2-5ms
    -> WebRTC P2P back to attendee       ~50-150ms
```

### Latency by Component

| Component | Latency | Notes |
|-----------|---------|-------|
| PulseAudio dual-sink routing (total) | ~5-10ms | Kernel-space memory copy, negligible |
| WebRTC network round-trip (both directions) | ~100-300ms | Depends on network quality |
| **Web Speech API (STT)** | **~500-2000ms** | **Bottleneck**: audio sent to Google servers for recognition, must wait for end of utterance |
| Search + TTS playback start | ~15-55ms | Negligible |

### Total End-to-End Latency

| Metric | Estimated | Design Target |
|--------|-----------|---------------|
| Speech end to answer display | ~1-2.5s | < 3 seconds |
| Speech end to attendee hears TTS | ~1.5-3s | < 5 seconds |

**Conclusion**: PulseAudio routing adds negligible latency (~5-10ms). The bottleneck is Web Speech API server-side recognition (~500-2000ms). Design targets of < 3s (display) and < 5s (TTS response) are achievable with margin.

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| All TICKET_205 Q&A accessible | 182/182 |
| All answers have short summaries (`a_short`) | 182/182 |
| All answers have pre-generated audio (short + full) | 364/364 .mp3 files |
| Search response time | < 50ms (client-side) |
| Voice-to-match latency | < 3 seconds (speech end to answer display) |
| Voice-to-TTS-response latency | < 5 seconds (speech end to attendee hears answer) |
| TTS audio isolation | Verified: TTS does NOT trigger STT |
| Works in Gather Town iframe (booth mode) | Verified |
| Voice recognition works with dual-sink routing | Verified |
| TTS playback audible to attendee via Gather Town | Verified |
| No external dependencies at runtime | 0 API calls (except Speech API) |
| Page load time | < 2 seconds |
| Accessible without presenter present | 24/7 during conference (booth mode) |
| End-to-end dry run completed (voice + TTS) | Before conference day |

---

## References

- TICKET_205 - Q&A data source (182 questions)
- TICKET_225 - Poster multimedia strategy (booth layout)
- [Gather Town: Embedded Websites](https://support.gather.town/hc/en-us/articles/15910417713940-Embedded-Websites) - iframe embedding docs
- [C++Online Posters](https://cpponline.uk/posters/) - Booth object types
- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) - Speech recognition API
- [Web Speech API Demo](https://addpipe.com/web-speech-api-demo/) - Live browser demo
- [SpeechSynthesis API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) - Browser TTS API (booth mode)
- [HTMLMediaElement.setSinkId() - MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/setSinkId) - Audio output device selection
- [edge-tts (PyPI)](https://pypi.org/project/edge-tts/) - Microsoft Azure Neural TTS CLI
- [PulseAudio module-null-sink](https://wiki.archlinux.org/title/PulseAudio) - Virtual sink creation for audio isolation
