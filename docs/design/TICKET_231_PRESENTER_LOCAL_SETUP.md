# TICKET_231: Prepare Presenter Mode Local Environment

## Status: Pending (Blocked - TTS audio generation requires manual quality review)
## Priority: High
## Category: Conference / Pre-Session Self-Prepared
## Parent: TICKET_226
## Date: 2026-02-25
## Deadline: Before conference

---

## Objective

Prepare the presenter's laptop with `presenter.html`, pre-generated TTS audio files, and the PulseAudio routing script. Everything runs locally - nothing is uploaded.

## Deliverables

### A. Pre-Generated TTS Audio (364 .mp3 files)

Run `generate_audio.py` to produce audio for all 182 Q&A pairs:
- 182 short answers (`*_short.mp3`)
- 182 full answers (`*_full.mp3`)
- `manifest.json` with SHA256 checksums

```bash
cd docs/chatbot
pip install edge-tts
python3 generate_audio.py
```

Expected output: `docs/chatbot/audio/` (~150MB, 364 files + manifest)

### B. Presenter HTML

- `docs/chatbot/presenter.html` - Already implemented
- Verify it loads locally: `python3 -m http.server 8080 -d docs/chatbot/`
- Open `http://localhost:8080/presenter.html`

### C. PulseAudio Setup Script

- `docs/chatbot/setup_audio.sh` - Already implemented
- Creates GatherIn + TTSOut virtual sinks
- Run before the session: `bash docs/chatbot/setup_audio.sh setup`
- Verify: `bash docs/chatbot/setup_audio.sh verify`

## Acceptance Criteria

- [ ] 364 .mp3 files generated in `docs/chatbot/audio/`
- [ ] `manifest.json` created with correct checksums
- [ ] `presenter.html` loads and functions locally
- [ ] Voice recognition (Web Speech API) works in Chrome
- [ ] TTS playback plays audio files correctly
- [ ] `setup_audio.sh setup` creates virtual sinks without errors
- [ ] `setup_audio.sh verify` shows both sinks active

## Notes

- Audio files are gitignored - they stay on the laptop only
- Requires Chrome (Web Speech API support)
- Requires Linux with PulseAudio
- Test the full flow: speak -> transcript -> Q&A match -> audio playback
