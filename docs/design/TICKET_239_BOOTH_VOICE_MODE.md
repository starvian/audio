# TICKET_239: Add Voice Mode to Booth Chatbot (GitHub Pages)

## Status: Open
## Priority: Medium
## Category: Conference / Feature
## Parent: TICKET_226
## Date: 2026-02-27
## Depends on: TICKET_234 (booth mode verified), TICKET_230 (GitHub Pages deployed)

---

## Problem

The booth chatbot (index.html) only supports text input. Attendees must type keywords to search.

The presenter mode (presenter.html) has voice input but requires PulseAudio routing, echo prevention, and a local Linux setup -- it cannot run on GitHub Pages for arbitrary visitors.

However, the voice pipeline is much simpler for a remote visitor:

- Visitor uses their OWN microphone (browser permission)
- Browser's Web Speech API does STT client-side (Chrome sends to Google, Edge processes locally)
- Q&A match is already client-side JavaScript
- TTS response plays pre-generated .mp3 through visitor's speakers/headphones
- No echo prevention needed: visitor's mic and speakers are physically separated (headphones) or the browser's AEC (Acoustic Echo Cancellation) handles it

**No server, no backend, no WebRTC, no PulseAudio.** Pure client-side, deployable on GitHub Pages.

---

## Objective

Add a microphone button to `index.html` that enables voice input. Visitors click the mic, speak a question, the browser transcribes it, searches Q&A, and plays the .mp3 answer.

---

## Architecture

```
Visitor speaks
    |
    v
Browser Web Speech API (STT) -- runs in visitor's Chrome/Edge
    |
    v
Transcript text -> search input -> app.js keyword search
    |
    v
Top Q&A match -> play .mp3 via <audio> element
    |
    v
Visitor hears answer through their speakers/headphones
```

Zero server-side processing. Zero new dependencies.

---

## What to Reuse

| Component | Source | Reuse Strategy |
|-----------|--------|----------------|
| SpeechRecognition setup | `voice.js` VoiceRecognizer | Extract core STT logic (no PulseAudio, no L2/L3) |
| Search + render | `app.js` searchQA / renderResults | Already exposed on `window` |
| .mp3 playback | `tts.js` TTSPlayer | Simplify: no setSinkId, no AudioPipeline |
| Q&A data | `qa-data.js` | Already loaded in index.html |

---

## Implementation Plan

### Step 1: Add Mic Button to index.html

Add a microphone toggle button next to the search input in the search bar.

```html
<div class="search-bar">
    <button id="mic-btn" class="mic-btn" title="Voice input (Chrome/Edge)">&#127908;</button>
    <input type="text" id="search-input" ...>
    <button id="search-btn" class="search-btn">Ask</button>
</div>
```

The mic button shows a microphone icon. States:
- Default: gray (idle)
- Listening: red pulse animation (recording)
- Not supported: hidden (Firefox/Safari)

### Step 2: Add Lightweight Voice Module to index.html

Add a new `<script src="booth-voice.js"></script>` to index.html (after app.js).

`booth-voice.js` contains a simplified voice handler:
- Feature-detect `SpeechRecognition` / `webkitSpeechRecognition`
- If not supported: hide mic button, exit
- On mic click: toggle listening on/off
- `onresult` (final): set search input value, trigger search via `window.searchQA` + `window.renderResults`
- No continuous mode: single utterance per click (simpler UX for booth visitors)
- No echo prevention (not needed for remote visitors)

### Step 3: Add Auto-Play .mp3 for Top Match

When voice input triggers a search and the top result scores above threshold:
- Automatically play the `audio_short` .mp3 of the top match
- Use a simple `<audio>` element (no setSinkId, no AudioPipeline)
- Show a small playback indicator on the result card
- Visitor can click "Play Full" for the complete answer

### Step 4: Un-gitignore Audio Files

Currently `docs/chatbot/audio/` is gitignored. To deploy on GitHub Pages:

1. Remove `audio/` from `.gitignore`
2. Commit the 364 .mp3 files (38MB total) to the repo
3. Push to GitHub -- GitHub Pages serves them as static assets

GitHub Pages limits:
- Repo size: 1GB soft limit (38MB is fine)
- Bandwidth: 100GB/month (38MB x ~2,600 full loads)
- Single file: 100MB max (our files are small)

### Step 5: Graceful Degradation

| Browser | Voice | Text Search | .mp3 Playback |
|---------|-------|-------------|---------------|
| Chrome (desktop) | Yes | Yes | Yes |
| Edge (desktop) | Yes | Yes | Yes |
| Chrome (Android) | Yes | Yes | Yes |
| Firefox | No (mic hidden) | Yes | Yes |
| Safari | No (mic hidden) | Yes | Yes |

When voice is unavailable, the page works exactly as before (text-only booth mode).

---

## Style

Mic button CSS:
- Circular button, matches dark theme (#0f3460 background)
- Idle: gray mic icon
- Listening: red background with pulse animation
- Hover: lighter shade

---

## Files to Create / Modify

| File | Action | Changes |
|------|--------|---------|
| `index.html` | Modify | Add mic button in search bar, add `<script src="booth-voice.js">` |
| `booth-voice.js` | **Create** | Lightweight voice input handler (~60-80 lines) |
| `style.css` | Modify | Add `.mic-btn` styles (idle, listening, pulse animation) |
| `.gitignore` | Modify | Remove `audio/` exclusion |

No changes to: `app.js`, `voice.js`, `tts.js`, `presenter.html`, `qa-data.js`

---

## Testing

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Open index.html in Chrome | Mic button visible | [ ] |
| 2 | Open index.html in Firefox | Mic button hidden, text search works | [ ] |
| 3 | Click mic, speak "polymorphic memory resource" | Search input fills, results appear | [ ] |
| 4 | Top match auto-plays .mp3 | Audio plays through speakers | [ ] |
| 5 | Click mic again while listening | Stops listening | [ ] |
| 6 | HTTPS required | Works on GitHub Pages (https://), fails on http:// (expected) | [ ] |
| 7 | Microphone permission denied | Graceful error message, falls back to text | [ ] |
| 8 | Multiple voice queries in sequence | Each query replaces previous, no overlap | [ ] |

---

## Acceptance Criteria

- [ ] Mic button added to index.html
- [ ] Voice input works in Chrome/Edge
- [ ] Graceful degradation in unsupported browsers
- [ ] Auto-play .mp3 for top voice match
- [ ] Audio files committed and served from GitHub Pages
- [ ] No changes to presenter mode functionality
- [ ] No new dependencies (zero libraries, zero backend)

---

## Dependencies

| Ticket | Dependency Type | Why |
|--------|----------------|-----|
| TICKET_230 | Depends on | GitHub Pages must be deployed |
| TICKET_234 | Depends on | Booth mode must be verified first |
| TICKET_226 | Parent | Main chatbot design spec |
