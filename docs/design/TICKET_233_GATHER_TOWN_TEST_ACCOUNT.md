# TICKET_233: Create Gather Town Test Environment

## Status: Open
## Priority: High (Blocks end-to-end verification)
## Category: Conference / Testing Infrastructure
## Parent: TICKET_226
## Date: 2026-02-25
## Blocks: TICKET_230 (iframe verification), TICKET_232 (audio routing verification)

---

## Problem

All code files exist but nothing has been tested end-to-end. A Gather Town test space is required to verify:

1. Booth mode iframe embedding (TICKET_230)
2. Presenter mode audio routing through proximity chat (TICKET_232)
3. Full pipeline: attendee speaks -> STT -> Q&A match -> TTS -> attendee hears answer

Without a test space, we cannot confirm the chatbot actually works in the target environment.

---

## Objective

Create a Gather Town test space with two accounts to verify booth mode (iframe) and presenter mode (voice + audio routing) before the conference.

---

## Step 1: Create Primary Account (Presenter)

Gather Town has no separate signup page. Login and registration use the same entry point.

1. Go to https://app.gather.town/signin (or click "Sign in" at https://www.gather.town/)
2. **IMPORTANT: Choose "Gather Classic (V1)"** when prompted (NOT V2 Beta)
   - V2 removed Mapmaker custom objects and Embedded Website iframe support
   - V1 supports all features we need: Embedded Website objects, Mapmaker, proximity voice chat
3. Option A (recommended): Click "Sign in with Google" -> select Google account -> done
4. Option B: Enter email -> click "Sign in with email" -> check inbox for 6-digit code -> enter code
5. First login automatically creates the account
6. Choose avatar appearance and display name in the character picker
7. Free plan: 30-day full trial (up to 50 users), then free for up to 25 users

## Step 2: Create Test Space

1. After login, go to https://www.gather.town/get-started (or click "Create a Space" in dashboard)
2. Choose a small template (e.g. "Blank" or "Office Small")
3. Name it (e.g. "NexusFix QA Test")
4. Note the space URL for later configuration

## Step 3: Add Website Object (Booth Chatbot)

1. Enter the space in Build mode (hammer icon or shortcut)
2. Place a "Website" object (Object Picker -> Embedded Website)
3. Set the URL to the chatbot:
   - For local testing: `http://localhost:8080/index.html` (will only work on same machine)
   - For deployed testing: GitHub Pages URL (after TICKET_230 deploy)
4. Set interaction distance (default is fine)
5. Test: walk avatar near the object -> iframe should open with the chatbot

## Step 4: Create Second Account (Attendee Simulator)

To test presenter mode (proximity voice chat), a second participant is needed:

1. Register a second Gather Town account with a different email
2. Or use a second browser profile / incognito window
3. Join the same test space with this second account
4. This account simulates an attendee asking questions via voice

## Step 5: Verify Booth Mode (Mode A)

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Walk to Website object | iframe opens with chatbot UI | [ ] |
| 2 | Type a question (e.g. "PMR") | Search results appear with relevant Q&A | [ ] |
| 3 | Click a category filter | Results filtered correctly | [ ] |
| 4 | Click "Expand" on an answer | Full answer displayed | [ ] |
| 5 | iframe renders correctly | No layout overflow, scrollable, dark theme visible | [ ] |
| 6 | No console errors | Check DevTools console | [ ] |

## Step 6: Verify Presenter Mode (Mode B) - Requires TICKET_231 + TICKET_232

| # | Test | Expected Result | Pass? |
|---|------|-----------------|-------|
| 1 | Attendee account speaks near presenter | Proximity chat audio reaches presenter | [ ] |
| 2 | PulseAudio GatherIn sink receives audio | `setup_audio.sh verify` confirms | [ ] |
| 3 | presenter.html transcript shows speech | Web Speech API captures from GatherIn monitor | [ ] |
| 4 | Q&A auto-match appears | Search results shown for recognized text | [ ] |
| 5 | Click [Play Short] | .mp3 plays through TTSOut sink | [ ] |
| 6 | Attendee hears TTS response | TTSOut routed to Gather Town mic input | [ ] |
| 7 | TTS does NOT re-trigger STT | Audio isolation verified (no echo in transcript) | [ ] |

---

## Gather Town Free Plan Limits

| Feature | Free Plan |
|---------|-----------|
| First 30 days | All features, up to 50 users |
| After 30 days | Free for up to 25 users |
| Custom maps | Yes |
| Website objects (iframe) | Yes |
| Proximity voice chat | Yes |
| Credit card required | No |
| Cost | $0 |

Free plan is sufficient for all testing needs.

---

## Notes

- Gather Town requires Chrome or a Chromium-based browser for best compatibility
- Proximity chat is WebRTC peer-to-peer: both accounts must be close to each other in the space
- Website object iframe: some URLs may be blocked by X-Frame-Options; GitHub Pages does not set this header, so it should work
- For local testing (localhost URL in iframe), both the space and the chatbot must be opened on the same machine

---

## Acceptance Criteria

- [ ] Primary account created and can access Gather Town
- [ ] Test space created with Website object configured
- [ ] Second account created (or second browser profile ready)
- [ ] Booth mode (Mode A) iframe embedding verified (Step 5 checklist)
- [ ] Presenter mode (Mode B) end-to-end verified (Step 6 checklist)

---

## Dependencies

| Ticket | Dependency Type | Why |
|--------|----------------|-----|
| TICKET_230 | Needs (for deployed URL) | GitHub Pages URL needed for iframe Website object |
| TICKET_231 | Needs (for presenter mode) | Audio files + presenter.html must be ready |
| TICKET_232 | Needs (for audio routing) | PulseAudio sinks must be configured |
