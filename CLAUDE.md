# CLAUDE.md

# C++Online 2026 Poster Q&A Chatbot

**Organization**: SilverstreamsAI
**Project Status**: Active Development
**Category**: Conference / Presentation Tool
**Parent Project**: NexusFIX (TICKET_225 -> TICKET_226)
**Date**: 2026-02-25

---

## Contact

For questions, collaboration, or consulting inquiries:

**Contact**: contact@silverstream.tech

---

## Repository Policy

### Parent Repository

This project lives under the NexusFIX ecosystem but is developed in a separate workspace.

| Repository | Path | Purpose |
|------------|------|---------|
| Source (this project) | `/data/ws/audio/` | Q&A Chatbot development |
| Parent project | `/data/ws/NexusFix/` | NexusFIX main repo |
| Design ticket | `docs/design/TICKET_226_CPPONLINE_QA_CHATBOT.md` | Full specification |

### Deployment Targets

| Target | Path | Visibility |
|--------|------|------------|
| Booth mode (attendees) | `docs/chatbot/index.html` | **Public** (GitHub Pages) |
| Presenter mode (live) | `docs/chatbot/presenter.html` | **Local only** |
| Audio files | `docs/chatbot/audio/` | **Local only** (gitignored) |

---

## 1. Project Overview

Deploy a self-service Q&A chatbot for the C++Online 2026 poster session. Two deployment modes:

**Mode A: Booth Chatbot** - Website object in Gather Town poster booth. Attendees type questions, get instant answers from 182 pre-written Q&A pairs. Works 24/7 without presenter.

**Mode B: Presenter Assistant** - Local on presenter's laptop during live 20-min slot. Captures attendee voice via Web Speech API + PulseAudio routing, auto-matches Q&A, responds with pre-generated TTS audio played back into Gather Town.

### Technology Stack

| Component | Choice |
|-----------|--------|
| Frontend | Static HTML + CSS + JavaScript (no build tools, no framework) |
| Search | Client-side keyword matching |
| Speech-to-Text | Web Speech API (Chrome native) |
| TTS (Booth) | Browser SpeechSynthesis API |
| TTS (Presenter) | Pre-generated edge-tts .mp3 files |
| Audio Routing | PulseAudio dual-sink isolation (Linux) |
| Data | Embedded JSON from TICKET_205 (182 Q&A pairs) |
| Hosting | GitHub Pages (booth) + localhost (presenter) |

### Data Source

182 Q&A pairs from TICKET_205: 16 general + 166 technical across 16 categories.

---

# CRITICAL RULES

## NO WORKAROUNDS - ROOT CAUSE ONLY

**ABSOLUTE PROHIBITION**:
- NO WORKAROUNDS of any kind
- NO BYPASSING errors or issues
- NO TEMPORARY FIXES or patches
- NO "QUICK SOLUTIONS" that avoid the real problem
- NO MOCKUP CODE - Never create placeholder, mock, or stub implementations

**MANDATORY APPROACH**:
- FIND ROOT CAUSE - Always investigate the true source of every problem
- FIX THE SOURCE - Address the actual underlying issue, never the symptoms
- DEEP INVESTIGATION - Trace problems through the complete system flow
- NO ASSUMPTIONS - Verify every hypothesis with evidence

## NO UNRELATED CODE CHANGES

**ABSOLUTE PROHIBITION**:
- NO UNRELATED MODIFICATIONS - Never modify code that is not directly related to the specific issue being addressed
- NO SCOPE CREEP - Do not expand changes beyond the identified problem area
- NO OPPORTUNISTIC FIXES - Do not fix other issues discovered during investigation unless explicitly requested
- NO FORMATTING CHANGES - Do not make cosmetic or formatting changes unrelated to the core issue
- NO REFACTORING - Do not refactor unrelated code during bug fixes

**MANDATORY APPROACH**:
- SURGICAL PRECISION - Make only the minimal changes required to fix the specific issue
- ISOLATED CHANGES - Ensure all modifications are directly traceable to the root cause
- CHANGE JUSTIFICATION - Every line changed must have a clear relationship to the problem being solved
- FOCUSED SCOPE - Maintain strict boundaries around the problem domain

## CODE REUSE MANDATORY

**ABSOLUTE PROHIBITION**: Implementing new code when existing, tested implementations can be reused.

**MANDATORY APPROACH**:
- SEARCH BEFORE IMPLEMENT - Always search for existing implementations before writing new code
- REUSE UTILITIES - Use existing search, TTS, voice recognition modules
- REUSE PATTERNS - Follow established patterns in app.js, voice.js, tts.js

## ENGLISH-ONLY CHARACTERS

**ABSOLUTE PROHIBITION**:
- NO NON-ENGLISH CHARACTERS - All characters in all code and documentation files must be English characters. This includes comments, variable names, and all other text.

## NO COMMITS WITHOUT AUTHORIZATION

**ABSOLUTE PROHIBITION**:
- NO GIT COMMITS without explicit user authorization
- NO automatic commits after implementing changes

**MANDATORY APPROACH**:
- WAIT FOR APPROVAL - After implementing changes, wait for user to explicitly request commit
- ASK BEFORE COMMIT - If unsure, ask user whether to commit
- SHOW CHANGES FIRST - Present `git diff` or summary before committing

## NO GIT PUSH - USER ONLY

**ABSOLUTE PROHIBITION**:
- NEVER execute `git push` under any circumstances
- Push credentials belong to the user - Claude must not authenticate pushes

**MANDATORY APPROACH**:
- After committing, remind the user to push manually
- If user asks to push, decline and instruct them to run `git push` themselves

## GIT AUTHOR CONFIGURATION

**All commits MUST use the following author information:**

```
Author: Alan <alan@silverstream.tech>
```

**PROHIBITION**:
- NO Co-Authored-By lines
- NO other author names or emails

**Commit message format:**
```bash
git commit -m "$(cat <<'EOF'
Your commit message here.
EOF
)"
```

---

# Design Principles

## Zero Dependencies, Zero Backend

- Pure client-side implementation: zero cost, zero backend, zero runtime failure modes
- No build tools, no framework, no node_modules
- Single directory deployment
- Embeddable in Gather Town iframe

## Deterministic, On-Brand

- Mirrors NexusFIX design philosophy: deterministic, zero-dependency
- All 182 Q&A pairs are pre-written (from TICKET_205), not AI-generated at runtime
- Search is client-side keyword matching, not AI/LLM

## Audio Isolation (Presenter Mode)

- PulseAudio dual-sink isolation prevents TTS -> STT feedback loop
- Three defense layers: L1 (sink isolation), L2 (state lock + STT pause), L3 (echo fingerprint dedup)
- Speech API listens on GatherIn sink; TTS plays on TTSOut sink

---

# File Structure

```
docs/chatbot/
├── index.html          # Booth mode (GitHub Pages, iframe-embeddable)
├── presenter.html      # Presenter assistant mode (local only)
├── style.css           # Shared dark theme styles
├── app.js              # Search logic, UI interaction, category filters
├── voice.js            # Web Speech API integration (presenter mode)
├── tts.js              # TTS playback + audio sink routing + feedback prevention
├── qa-data.js          # All 182 Q&A pairs as JSON (includes a_short + audio paths)
├── generate_audio.py   # Batch TTS generation script (edge-tts)
├── audio/              # Pre-generated .mp3 files (gitignored, local only)
│   ├── general_q01_short.mp3
│   ├── general_q01_full.mp3
│   ├── ...
│   └── manifest.json   # Audio file <-> Q&A ID mapping + checksums
└── README.md           # Build/deploy/audio routing instructions
```

---

# Implementation Phases

## Phase 1: Data Extraction
- Parse TICKET_205 Q&A into structured JSON
- Assign categories, add keyword arrays
- Write `a_short` (1-2 sentence summary) for each of the 182 answers
- Validate: 182 questions, no missing answers, no missing `a_short`

## Phase 2: Core UI (Booth Mode)
- `index.html` with chat-style layout
- Dark theme CSS (#1a1a2e background, #0f3460 accent, white text)
- Category filter buttons, expandable answers
- Code block syntax highlighting
- Browser SpeechSynthesis for read-aloud

## Phase 3: Search
- Client-side keyword search with scoring (keyword match: 10, question: 5, answer: 2)
- Search-as-you-type with debounce
- Result ranking and highlighting

## Phase 4: Voice Recognition (Presenter Mode)
- `presenter.html` with split layout (transcript + Q&A results)
- Web Speech API continuous mode
- Live transcript display (interim gray / final white)
- Auto-search on final transcript
- [Listen] / [Stop] / [Clear] controls

## Phase 4.5: TTS Audio Generation
- edge-tts batch generation (en-US-GuyNeural)
- SSML pronunciation for technical terms (SIMD, PMR, SBE, SOH)
- 182 short + 182 full = 364 .mp3 files (~150MB, local only)

## Phase 4.6: TTS Playback + Feedback Prevention
- `tts.js` with TTSPlayer class + setSinkId() routing
- [Play Short] / [Play Full] buttons
- AudioPipeline: L2 state lock + L3 echo detection

## Phase 5: Audio Routing Setup
- PulseAudio dual-sink setup script (GatherIn + TTSOut)
- Verify isolation: TTS does NOT trigger STT

## Phase 6: Polish
- Welcome message with popular questions
- Responsive layout for iframe
- Keyboard shortcuts for presenter mode

## Phase 7: Deploy & Test
- GitHub Pages deployment (booth mode, no audio files)
- End-to-end: speak -> transcript -> Q&A match -> TTS answer
- Dry run: simulate 20-minute presentation

---

# Success Criteria

| Criteria | Target |
|----------|--------|
| All TICKET_205 Q&A accessible | 182/182 |
| All answers have short summaries (`a_short`) | 182/182 |
| All answers have pre-generated audio (short + full) | 364/364 .mp3 files |
| Search response time | < 50ms (client-side) |
| Voice-to-match latency | < 3 seconds |
| Voice-to-TTS-response latency | < 5 seconds |
| TTS audio isolation | Verified: TTS does NOT trigger STT |
| Works in Gather Town iframe | Verified |
| No external dependencies at runtime | 0 API calls (except Speech API) |
| Page load time | < 2 seconds |

---

# References

- `docs/design/TICKET_226_CPPONLINE_QA_CHATBOT.md` - Full design specification (this project)
- TICKET_205 - Q&A data source (182 questions)
- TICKET_225 - Poster multimedia strategy (booth layout)
- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [SpeechSynthesis API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)
- [HTMLMediaElement.setSinkId() - MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/setSinkId)
- [edge-tts (PyPI)](https://pypi.org/project/edge-tts/)
- [PulseAudio module-null-sink](https://wiki.archlinux.org/title/PulseAudio)

---

# Communication

- No workarounds, no temporary solutions, no assumptions
- Always recommend best practices
- Short responses preferred
