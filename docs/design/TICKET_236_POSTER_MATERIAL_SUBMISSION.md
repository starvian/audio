# TICKET_236: Poster Material Submission to C++Online 2026

## Status: Open
## Priority: Critical (Deadline: 2026-02-28)
## Category: Conference / Deployment
## Parent: TICKET_226
## Date: 2026-02-26
## Depends: TICKET_234 (local verification), TICKET_230 (GitHub Pages deploy)

---

## Objective

Submit the Q&A chatbot as poster material to C++Online 2026 via Dropbox before the February 28th deadline.

---

## Context

### Investigation Summary

C++Online poster booths support up to 3 objects of 4 types: Video, Image, Embedded Webpage, Text Link. The Q&A chatbot (`index.html` on GitHub Pages) matches the **Embedded Webpage** type:

- Loads inside a Gather Town popup panel (iframe)
- Attendees interact while in proximity video chat with presenter
- Works 24/7 without presenter present
- Supports multiple content types in a single interface (search, 182 Q&A pairs, categories, LLM fallback)

### Requirements Confirmed (from Poster Requirements page)

| Requirement | Status |
|-------------|--------|
| Webpage must be embeddable (no X-Frame-Options block) | Verified (TICKET_233, TICKET_234) |
| Interactive while in booth conversation | Yes - chatbot runs independently of video chat |
| Non-commercial content | Yes - educational Q&A only |
| Max 3 objects per booth | Using 1 (chatbot webpage) |

### Material Type Selection

| Slot | Type | Content | Purpose |
|------|------|---------|---------|
| 1 (Primary) | Embedded Webpage | Q&A Chatbot (`index.html`) | Interactive Q&A for attendees |
| 2 (Optional) | Image or Video | Poster image / demo video | Visual summary of NexusFIX |
| 3 | (Reserved) | - | - |

---

## Submission Steps

### Step 1: Prepare URL Text File

C++Online requires webpage links submitted as a text file uploaded to Dropbox.

Create file `poster_material.txt` containing:

```
Poster Material: NexusFIX - Zero-Cost FIX Engine for C++
Type: Embedded Webpage (Interactive Q&A Chatbot)
URL: https://silverstreamai.github.io/NexusFix/chatbot/
```

### Step 2: Verify GitHub Pages URL

Before submitting, confirm the live URL loads correctly:

```bash
curl -s -o /dev/null -w "%{http_code}" https://silverstreamai.github.io/NexusFix/chatbot/
```

Expected: HTTP 200

### Step 3: Upload to C++Online Dropbox

Upload `poster_material.txt` to the C++Online Dropbox link (provided in poster requirements email).

**This is a manual step - user must upload.**

### Step 4: Confirm Submission

Reply to C++Online organizers (via Discord or email) confirming material has been uploaded.

---

## Acceptance Criteria

| # | Criteria | Status |
|---|----------|--------|
| 1 | GitHub Pages URL is live and accessible | [ ] |
| 2 | Chatbot loads correctly in iframe (no CORS/CSP errors) | [ ] |
| 3 | Text file with URL uploaded to C++Online Dropbox | [ ] |
| 4 | Submission confirmed with organizers | [ ] |
| 5 | Submitted before 2026-02-28 deadline | [ ] |

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| GitHub Pages URL not live | Low (TICKET_230 done) | Verify URL before submission |
| Iframe embedding blocked | Low (verified in TICKET_233) | Test in Gather Town demo space |
| Organizers need different format | Low | Provide URL + screenshot as backup |
| Late submission | Medium | Submit by 2026-02-27 (1 day buffer) |

---

## Notes

- Presenter mode (`presenter.html`) is NOT submitted - it runs locally on the presenter laptop
- Audio files (`audio/`) are NOT deployed to GitHub Pages - booth mode uses browser SpeechSynthesis
- Optional: Submit a poster image (Slot 2) as a visual summary for the booth billboard object
