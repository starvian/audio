# TICKET_232: On-Site PulseAudio Sink Routing + Chrome Configuration

## Status: Open
## Priority: High
## Category: Conference / On-Site Configuration
## Parent: TICKET_226
## Date: 2026-02-25
## Deadline: At conference, before live session

---

## Objective

Configure PulseAudio sink routing and Chrome audio device selection on the presenter's laptop at the conference, before entering the Gather Town live session.

## Pre-Requisites

- TICKET_231 completed (presenter.html + audio + setup_audio.sh ready)
- Laptop running Linux with PulseAudio
- Chrome browser installed
- Microphone and speakers/headphones connected

## Step 1: PulseAudio Sink Setup

```bash
cd docs/chatbot
bash setup_audio.sh setup
bash setup_audio.sh verify
```

This creates:
- **GatherIn** sink: Chrome microphone input (STT listens here)
- **TTSOut** sink: TTS audio output (plays into Gather Town, not into STT)

## Step 2: Chrome Audio Device Selection (pavucontrol)

Open `pavucontrol` and configure:

### Playback Tab
- Chrome (Gather Town tab): Output to **default speakers/headphones** (to hear attendees)
- Chrome (presenter.html tab): Output to **TTSOut** sink (TTS goes into Gather Town)

### Recording Tab
- Chrome (presenter.html tab - Web Speech API): Input from **GatherIn** monitor
- This ensures STT captures Gather Town audio, not TTS feedback

## Step 3: Gather Town Audio Settings

In Gather Town settings:
- Microphone: Select **TTSOut.monitor** (so TTS audio is sent as your "voice")
- Speaker: Select **GatherIn** (so attendee audio goes to STT)

## Step 4: Verify Isolation

1. Start `presenter.html` listening (Space bar)
2. Play a test TTS audio
3. Confirm: TTS does NOT appear in the transcript (no feedback loop)
4. Confirm: Speaking into the physical mic DOES appear in the transcript via Gather Town round-trip

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| TTS echoes in transcript | Check pavucontrol: presenter.html playback must go to TTSOut, not default |
| No transcript from attendees | Check pavucontrol: presenter.html recording must use GatherIn.monitor |
| Gather Town cannot hear TTS | Check Gather Town mic setting: must be TTSOut.monitor |
| No audio from attendees | Check Gather Town speaker setting: must be GatherIn |

## Acceptance Criteria

- [ ] `setup_audio.sh setup` runs successfully
- [ ] `setup_audio.sh verify` shows both sinks active
- [ ] pavucontrol shows correct routing for all Chrome streams
- [ ] Gather Town audio settings configured correctly
- [ ] TTS playback does NOT trigger STT (isolation verified)
- [ ] Attendee speech IS captured by STT (round-trip verified)
- [ ] Full flow works: attendee speaks -> transcript -> Q&A match -> TTS plays into Gather Town

## Notes

- This must be done fresh each time the laptop restarts (PulseAudio sinks are not persistent)
- Run `setup_audio.sh teardown` after the session to clean up
- Keep pavucontrol open during the session for quick adjustments
