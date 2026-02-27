# TICKET_234: Local Verification of Booth Mode (index.html)

## Status: Done
## Priority: High (Blocks TICKET_230 deploy)
## Category: Conference / Testing
## Parent: TICKET_226
## Date: 2026-02-25
## Blocks: TICKET_230 (GitHub Pages deploy), TICKET_233 (Gather Town iframe test)

---

## Problem

All booth mode files exist in `docs/chatbot/` but have never been opened in a browser. Must verify basic functionality locally before deploying to GitHub Pages.

The target URL `https://silverstreamai.github.io/NexusFix/chatbot/` does not exist yet. The files live in this workspace (`/data/ws/audio/docs/chatbot/`) but must be pushed to the NexusFix main repository (`SilverstreamsAI/NexusFix`) under `docs/chatbot/`.

---

## Objective

Run `index.html` locally, verify all booth mode features work, fix any issues found.

---

## Step 1: Start Local Server

```bash
cd /data/ws/audio
python3 -m http.server 8080 -d docs/chatbot/
```

Open in Chrome: `http://localhost:8080/index.html`

## Step 2: Verify Core Features

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Page loads without errors | Dark theme UI, search bar, category buttons visible | [x] |
| 2 | Check DevTools console | No JavaScript errors | [x] |
| 3 | Type "PMR" in search box | Results with PMR-related Q&A appear | [x] |
| 4 | Type "SIMD" in search box | Results with SIMD-related Q&A appear | [x] |
| 5 | Click a category filter button | Results filtered to that category only | [x] |
| 6 | Click expand on an answer | Full answer text displayed | [x] |
| 7 | Search-as-you-type debounce | Results update as user types, no lag | [x] |
| 8 | Result highlighting | Search keywords highlighted in results | [x] |
| 9 | Code blocks in answers | Syntax highlighting renders correctly | [x] |
| 10 | All 182 Q&A accessible | Browse each category, verify counts match qa-data.js | [x] |

## Step 3: Verify LLM Fallback (Optional)

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | No API key set | Status shows "No API key configured" | [x] |
| 2 | Search with low score (e.g. "weather") | Graceful fallback: category suggestions + contact info | [x] |
| 3 | Set API key via settings gear icon | Key saved to localStorage, status updates | [x] |
| 4 | Search out-of-scope question with API key | LLM answer with "AI-generated" badge | [x] |
| 5 | Clear API key | Key removed, status resets | [x] |

## Step 4: Verify Browser SpeechSynthesis (Booth TTS)

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Read-aloud button on answer (if present) | Browser speaks the answer text | [x] |

## Step 5: Fix Issues

- Fixed: favicon.ico 404 - Added `<link rel="icon" href="data:,">` to index.html and presenter.html

---

## Deployment Path

After local verification passes:

1. Copy `docs/chatbot/` booth mode files to NexusFix repo (`/data/ws/NexusFix/docs/chatbot/`)
2. Files to copy: `index.html`, `style.css`, `app.js`, `llm.js`, `qa-data.js`
3. Files NOT to copy: `presenter.html`, `voice.js`, `tts.js`, `generate_audio.py`, `setup_audio.sh`, `audio/`
4. Push to `SilverstreamsAI/NexusFix` (user action)
5. Verify GitHub Pages is configured to serve from `docs/` directory
6. Confirm `https://silverstreamai.github.io/NexusFix/chatbot/` loads correctly

---

## Acceptance Criteria

- [x] `index.html` loads locally without errors
- [x] Search works for all 182 Q&A pairs
- [x] Category filters functional
- [x] No console errors
- [x] LLM fallback graceful when no API key
- [x] All issues found are fixed
- [x] Ready for TICKET_230 (GitHub Pages deploy)
- [x] GitHub Pages live: https://silverstreamai.github.io/NexusFix/chatbot/

---

## Dependencies

| Ticket | Dependency Type | Why |
|--------|----------------|-----|
| TICKET_230 | Blocks | Cannot deploy until local verification passes |
| TICKET_233 | Blocks | Cannot test iframe in Gather Town until deployed |
