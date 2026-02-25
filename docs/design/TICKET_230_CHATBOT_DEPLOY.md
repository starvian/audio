# TICKET_230: Deploy Q&A Chatbot to GitHub Pages

## Status: Ready to Deploy
## Priority: High
## Category: Conference / Pre-Submission Deliverable
## Parent: TICKET_226
## Date: 2026-02-25
## Deadline: Before conference

---

## Objective

Deploy the booth-mode Q&A chatbot (`docs/chatbot/index.html`) to GitHub Pages so it can be configured as a Website object in Gather Town.

## Source

- `docs/chatbot/index.html` - Booth mode entry point
- `docs/chatbot/style.css` - Styles
- `docs/chatbot/app.js` - Search logic
- `docs/chatbot/llm.js` - LLM fallback
- `docs/chatbot/qa-data.js` - 182 Q&A pairs

## Requirements

1. Push `docs/chatbot/` to the GitHub repository
2. Enable GitHub Pages (source: `docs/chatbot/` or configure appropriately)
3. Verify the chatbot loads correctly at the GitHub Pages URL
4. Ensure iframe embedding works (no X-Frame-Options blocking)
5. Test in a browser to confirm search, categories, and UI all function

## Files to Deploy (Public)

| File | Purpose |
|------|---------|
| `index.html` | Booth mode entry |
| `style.css` | Dark theme |
| `app.js` | Search engine + UI |
| `llm.js` | LLM fallback (optional) |
| `qa-data.js` | 182 Q&A pairs |

## Files NOT to Deploy

| File | Reason |
|------|--------|
| `presenter.html` | Local only |
| `voice.js` | Presenter mode only |
| `tts.js` | Presenter mode only |
| `generate_audio.py` | Build tool |
| `setup_audio.sh` | Local tool |
| `audio/` | Gitignored, local only |

## Output

- GitHub Pages URL: `https://silverstreamai.github.io/NexusFix/chatbot/` (or similar)

## Upload Target

- Gather Town back-end (Object type: Website)
- Paste the GitHub Pages URL

## Verification Completed

- Booth mode files (5): index.html, style.css, app.js, llm.js, qa-data.js
- No hard dependencies on presenter-only files (voice.js, tts.js)
- playQA() guarded by `if (window.audioPipeline)` - safe in booth mode
- No X-Frame-Options headers blocking iframe embedding
- LLM fallback (llm.js) gracefully handles missing API key

## Remaining Steps (User Action)

1. Push `docs/chatbot/` to GitHub repo
2. Enable GitHub Pages (source: docs/ directory or configure path)
3. Paste the resulting URL into Gather Town (Object type: Website)

## Acceptance Criteria

- [ ] Chatbot accessible via GitHub Pages URL
- [ ] Loads correctly in browser
- [ ] Search works for all 182 Q&A pairs
- [ ] Category filters functional
- [ ] Iframe embedding works (test in an iframe)
- [ ] No console errors
- [ ] LLM fallback gracefully handles missing API key
