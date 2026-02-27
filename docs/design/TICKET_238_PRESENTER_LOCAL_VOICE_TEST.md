# TICKET_238: Local Verification of Presenter Mode (Voice Pipeline)

## Status: Open
## Priority: High (Blocks conference readiness)
## Category: Conference / Testing
## Parent: TICKET_226
## Date: 2026-02-26
## Depends on: TICKET_231, TICKET_232
## Blocked by: None (all dependencies completed)

---

## Problem

Booth mode (index.html) has been verified locally (TICKET_234) and in Gather Town iframe (TICKET_233 Step 5). However, **presenter mode (presenter.html) has never been tested end-to-end**.

Gather Town free plan limits spaces to 1 concurrent user (TICKET_233), so proximity voice chat testing is impossible without a paid plan. The presenter mode voice pipeline must be verified locally using PulseAudio routing to simulate the Gather Town audio path.

---

## Objective

Verify the full presenter mode pipeline locally:

```
Simulated attendee voice -> GatherIn sink -> Chrome STT -> Q&A match -> TTS .mp3 -> TTSOut sink
```

Confirm all three feedback prevention layers (L1 sink isolation, L2 state lock, L3 echo dedup) work correctly.

---

## Prerequisites

- Chrome browser (Web Speech API requires Chrome)
- PulseAudio running (Linux)
- `espeak-ng` installed (for simulating attendee voice)
- `pavucontrol` installed (for audio routing verification)
- 364 .mp3 files in `docs/chatbot/audio/` (already generated)

---

## Step 1: PulseAudio Sink Setup

```bash
cd /data/ws/audio/docs/chatbot
./setup_audio.sh setup
./setup_audio.sh verify
```

| # | Check | Expected Result | Pass? |
|---|-------|-----------------|-------|
| 1 | GatherIn sink exists | `pactl list sinks short` shows GatherIn | [ ] |
| 2 | TTSOut sink exists | `pactl list sinks short` shows TTSOut | [ ] |
| 3 | Sinks are isolated | `setup_audio.sh verify` confirms no cross-talk | [ ] |

---

## Step 2: Start Local Server and Open Presenter

```bash
python3 -m http.server 8080 -d /data/ws/audio/docs/chatbot/
```

Open Chrome: `http://localhost:8080/presenter.html`

| # | Check | Expected Result | Pass? |
|---|-------|-----------------|-------|
| 1 | Page loads without errors | Split layout: transcript (left) + Q&A results (right) | [ ] |
| 2 | No console errors | DevTools console clean | [ ] |
| 3 | Listen/Stop/Clear buttons visible | Voice controls rendered | [ ] |

---

## Step 3: STT - Physical Microphone Test

Test Web Speech API with default microphone input (no PulseAudio routing yet).

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Click [Listen] (or press Space) | STT starts, status shows "Listening..." | [ ] |
| 2 | Speak "polymorphic memory resource" | Interim results appear gray in transcript | [ ] |
| 3 | Pause speaking | Final result appears white in transcript | [ ] |
| 4 | Auto-search triggers | Q&A results appear in right panel | [ ] |
| 5 | Click [Stop] | STT stops, status updates | [ ] |
| 6 | Click [Clear] | Transcript cleared | [ ] |

---

## Step 4: TTS - Audio Playback Test

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Search result shows [Play Short] / [Play Full] | Buttons visible on matched Q&A | [ ] |
| 2 | Click [Play Short] | .mp3 file plays, status shows "Playing..." | [ ] |
| 3 | Click [Play Full] | Full .mp3 file plays | [ ] |
| 4 | Playback completes | Status returns to idle | [ ] |

---

## Step 5: PulseAudio Routing - Simulated Attendee

Configure Chrome to capture audio from GatherIn sink instead of physical microphone.

### 5a: Route Chrome STT input to GatherIn

Using `pavucontrol`:
1. Open `pavucontrol`
2. Recording tab: find Chrome's audio input
3. Change input source to **GatherIn.monitor**

### 5b: Inject simulated attendee voice

```bash
# Simulate attendee asking about PMR
espeak-ng "What is polymorphic memory resource" --stdout | paplay --device=GatherIn

# Simulate attendee asking about SIMD
espeak-ng "How does SIMD optimization work in NexusFix" --stdout | paplay --device=GatherIn

# Simulate attendee asking about SBE encoding
espeak-ng "What is Simple Binary Encoding" --stdout | paplay --device=GatherIn
```

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | espeak plays into GatherIn | `pavucontrol` Playback tab shows paplay on GatherIn | [ ] |
| 2 | Chrome STT captures from GatherIn.monitor | Transcript shows recognized text | [ ] |
| 3 | Q&A auto-match triggers | Relevant results appear in right panel | [ ] |

---

## Step 6: TTS Output Routing

Configure TTS playback to route to TTSOut sink.

Using `pavucontrol`:
1. Playback tab: find Chrome's audio output (during TTS playback)
2. Change output to **TTSOut**

Or verify that `tts.js` calls `setSinkId('TTSOut')` automatically.

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Click [Play Short] on a result | Audio plays through TTSOut (not default speakers) | [ ] |
| 2 | Verify in pavucontrol | Chrome playback stream shows TTSOut as output | [ ] |

---

## Step 7: Feedback Prevention (L1 + L2 + L3)

The critical integration test: TTS playback must NOT re-trigger STT.

### 7a: L1 - Sink Isolation

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | TTS plays on TTSOut | Audio does NOT appear on GatherIn.monitor | [ ] |
| 2 | STT listens on GatherIn.monitor | Does NOT hear TTSOut audio | [ ] |

### 7b: L2 - State Lock (STT pauses during TTS)

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | STT is running (Listening) | Transcript updating from GatherIn | [ ] |
| 2 | Click [Play Short] | STT pauses immediately (status changes) | [ ] |
| 3 | TTS playback completes | STT resumes after 500ms silence buffer | [ ] |
| 4 | No echo in transcript | TTS content does NOT appear as new transcript entry | [ ] |

### 7c: L3 - Echo Fingerprint Dedup

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Force a scenario where TTS audio leaks to STT | (e.g., temporarily route TTSOut to GatherIn) | [ ] |
| 2 | L3 detects 50%+ word overlap | Duplicate transcript entry suppressed | [ ] |
| 3 | Restore normal routing | Reset TTSOut away from GatherIn | [ ] |

---

## Step 8: Full Pipeline End-to-End

Automated flow: simulated voice -> STT -> match -> auto-play TTS.

1. Enable auto-play checkbox in presenter.html (if available)
2. Inject voice via espeak:
   ```bash
   espeak-ng "What is polymorphic memory resource" --stdout | paplay --device=GatherIn
   ```
3. Observe full pipeline without manual interaction.

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | espeak voice injected | GatherIn receives audio | [ ] |
| 2 | STT transcribes | Text appears in transcript panel | [ ] |
| 3 | Auto-search matches Q&A | Results shown in right panel | [ ] |
| 4 | Auto-play triggers (if enabled) | TTS .mp3 plays on TTSOut | [ ] |
| 5 | No echo loop | Pipeline completes without feedback | [ ] |
| 6 | Pipeline latency < 5 seconds | From espeak start to TTS playback start | [ ] |

---

## Step 9: Stress / Edge Cases

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Rapid sequential questions | Each question processed, no overlap/crash | [ ] |
| 2 | Long silence (30s) | STT stays in listening mode, no timeout | [ ] |
| 3 | Unintelligible speech | No match, graceful "no results" display | [ ] |
| 4 | Out-of-scope question ("What is the weather") | Low search score, LLM fallback or category suggestions | [ ] |
| 5 | TTS playback interrupted by new speech | Handles gracefully (stop current, process new) | [ ] |

---

## What This Test Does NOT Cover

| Aspect | Why | Mitigation |
|--------|-----|------------|
| Gather Town WebRTC audio delivery | Free plan 1-user limit | Audio path is identical once it reaches PulseAudio sink |
| Network latency / jitter | Local test has ~0 latency | Conference will have real network conditions |
| Multiple simultaneous attendees | Single pipeline test | Presenter mode handles one question at a time by design |

---

## Acceptance Criteria

- [ ] PulseAudio sinks created and verified (Step 1)
- [ ] presenter.html loads without errors (Step 2)
- [ ] STT works with physical microphone (Step 3)
- [ ] TTS .mp3 playback works (Step 4)
- [ ] STT captures from GatherIn via PulseAudio routing (Step 5)
- [ ] TTS routes to TTSOut (Step 6)
- [ ] Feedback prevention verified: L1, L2, L3 (Step 7)
- [ ] Full pipeline end-to-end passes (Step 8)
- [ ] Edge cases handled gracefully (Step 9)

---

## Dependencies

| Ticket | Dependency Type | Why |
|--------|----------------|-----|
| TICKET_231 | Depends on | Presenter setup (audio files + presenter.html) |
| TICKET_232 | Depends on | PulseAudio dual-sink configuration |
| TICKET_233 | Related | Gather Town test deferred presenter mode to local |
| TICKET_234 | Related | Booth mode local verification (completed) |
