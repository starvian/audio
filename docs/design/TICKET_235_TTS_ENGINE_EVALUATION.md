# TICKET_235: TTS Engine Evaluation and Contingency Plan

## Status: Open
## Priority: Medium
## Category: Conference / Audio Generation
## Parent: TICKET_226
## Date: 2026-02-26

---

## Objective

Document the TTS engine evaluation for generating 364 pre-recorded .mp3 files (182 short + 182 full) and establish a contingency plan if the current engine fails.

## Context

The project requires one-time batch generation of 364 audio files. Once generated, the files are decoupled from the TTS engine. The current implementation uses edge-tts (Microsoft Edge TTS, unofficial API).

## Current Choice: edge-tts

- **Voice**: en-US-GuyNeural
- **Implementation**: `docs/chatbot/generate_audio.py`
- **Status**: Implemented, ready to run
- **Cost**: Free
- **Quality**: Good (Neural voice)
- **Risk**: Unofficial API, could be blocked without notice

## Alternatives Evaluated

### Option A: Piper TTS (Preferred Backup)

- **Source**: Mozilla / open-source
- **Install**: `pip install piper-tts`
- **Runs**: Fully local, no network dependency
- **Quality**: Near-Neural quality
- **Speed**: 10-50x faster than real-time on CPU
- **Cost**: Free
- **Pros**: Offline, stable, no API risk
- **Cons**: Smaller voice selection than cloud services

### Option B: Microsoft Azure TTS

- **Free Tier**: 500,000 characters/month (sufficient for 364 files)
- **Quality**: Best (Neural + HD voices, full SSML + lexicon support)
- **Cost**: Free within tier
- **Pros**: Official API, stable SLA, best pronunciation control
- **Cons**: Requires Azure account setup, network dependency

### Option C: Other Open-Source (Coqui TTS, Bark)

- **Coqui TTS**: Good quality, multiple models, heavier setup
- **Bark**: Very natural output, slow generation, high resource usage
- **Cost**: Free
- **Pros**: Full control, no API dependency
- **Cons**: More complex setup, variable quality

## Decision

**Primary**: edge-tts (already implemented, good quality, zero cost)

**Contingency**: If edge-tts fails during generation, switch to Piper TTS. The switch requires updating `generate_audio.py` to use the piper-tts Python API instead of edge-tts.

## Rationale

1. Files are generated once and served as static .mp3 - no runtime TTS dependency
2. edge-tts quality is sufficient for conference presentation
3. generate_audio.py is already complete and tested
4. Risk is mitigated by the one-time nature of generation (files persist after generation)
5. Switching cost to Piper is low if needed (same Python script, different TTS call)

## Action Items

- [ ] Run `generate_audio.py` to produce all 364 .mp3 files
- [ ] Verify audio quality on a sample of files
- [ ] If edge-tts fails: install piper-tts and adapt generate_audio.py
- [ ] Store generated files in `docs/chatbot/audio/` (gitignored, local only)

## References

- `docs/chatbot/generate_audio.py` - Current batch generation script
- `docs/chatbot/tts.js` - TTS playback + sink routing
- TICKET_226 - Parent project specification
- [edge-tts (PyPI)](https://pypi.org/project/edge-tts/)
- [Piper TTS (GitHub)](https://github.com/rhasspy/piper)
- [Azure Speech Service pricing](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/)
