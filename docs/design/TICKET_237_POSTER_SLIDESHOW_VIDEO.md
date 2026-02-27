# TICKET_237: Poster Slideshow Video for Gather Town Booth

## Status: Open
## Priority: High (Deadline: 2026-02-28)
## Category: Conference / Pre-Submission Deliverable
## Parent: TICKET_225
## Date: 2026-02-26
## Replaces: TICKET_229 (YouTube Demo Video - scope reduced to slideshow)

---

## Objective

Create a 15-slide slideshow video (~3-4 minutes) covering all NexusFIX categories, with English narration (edge-tts). Each slide corresponds to one Q&A category from `qa-data.js`. Upload to YouTube for embedding as a Video object in the Gather Town poster booth (Slot 3).

---

## Context

Booth has 3 object slots:

| Slot | Type | Content | Status |
|------|------|---------|--------|
| 1 | Image | Poster PDF (TICKET_227) | Done |
| 2 | Embedded Webpage | Q&A Chatbot (TICKET_236) | Ready |
| 3 | Video | **This ticket** | Open |

---

## Content Outline (15 slides, ~3-4 minutes)

Each slide ~15-20 seconds narration. Some related categories are merged to keep the total at 15.

| Slide | Category | Key Talking Points | ~Duration |
|-------|----------|-------------------|-----------|
| 1 | Title | NexusFIX - Zero-Cost FIX Engine for Modern C++ / SilverstreamsAI | 10s |
| 2 | General Project | Motivation, target audience, C++23 from first principles | 20s |
| 3 | v1.0.0 Architecture | Overall design, zero-copy, header-only, deterministic | 20s |
| 4 | v0.1.0 Parser Foundation | Two-stage parsing, SOH scanning, field extraction | 20s |
| 5 | v0.1.1 PMR Pools | Polymorphic memory resources, arena allocation, zero heap | 20s |
| 6 | v0.1.2 + v0.1.4 CMake & CI/CD | Build system, cross-platform, GitHub Actions, testing | 15s |
| 7 | v0.1.5 Object Construction | Message object lifecycle, in-place construction | 15s |
| 8 | v0.1.6 MPSC Queue | Lock-free queue, IPC pipeline, producer-consumer | 15s |
| 9 | v0.1.7 SBE Encoding | Simple Binary Encoding, internal wire format | 15s |
| 10 | v0.1.8 Utilities | Supporting tools, benchmarking infrastructure | 15s |
| 11 | v0.1.9 MsgType Dispatch | Compile-time dispatch, tag-based routing | 15s |
| 12 | v0.1.10 + v0.1.11 Compile-time & C++23 | constexpr, concepts, std::expected, quick wins | 20s |
| 13 | v0.1.12 Ranges & C++23 | Ranges pipelines, lazy evaluation, modern idioms | 15s |
| 14 | v0.1.13 + v0.1.14 Structural Index & mimalloc | simdjson-inspired index, custom allocator, 246ns | 20s |
| 15 | v0.1.15 xsimd SIMD + Closing | SIMD acceleration, benchmarks, CTA: try chatbot | 20s |

**Total: ~255s (~4 minutes)**

---

## Source Material

- `post/poster.html` / `post/poster.pdf` - Visual elements, layout, data
- `docs/chatbot/qa-data.js` - Key talking points from Q&A pairs (182 Q&A, 17 categories)

---

## Slide Design

- Resolution: 1920x1080 (landscape)
- Dark theme matching booth chatbot (#1a1a2e background, #0f3460 accent, white text)
- Each slide: category title + 3-4 bullet points + key visual/diagram
- Consistent layout: title bar at top, content in center, slide number at bottom
- Tool: HTML/CSS pages rendered to PNG via Chrome screenshot

---

## Production Steps

### Step 1: Create 15 Slide HTML Pages

- One HTML file per slide (or single HTML with 15 sections)
- Dark theme consistent with chatbot style
- Extract key points from `qa-data.js` for each category
- Render to PNG (1920x1080) via Chrome headless or manual screenshot

### Step 2: Generate Narration (edge-tts)

- Write narration script for each slide (2-3 sentences)
- Generate .mp3 per slide using edge-tts (en-US-GuyNeural)
- Apply SSML pronunciation rules for technical terms (reuse from `generate_audio.py`)
- Output: 15 x .mp3 files

### Step 3: Assemble Video (ffmpeg)

```bash
# Per slide: static image + narration audio -> video clip
ffmpeg -loop 1 -i slide01.png -i narration01.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -vf "fps=30" -shortest clip01.mp4

# Repeat for all 15 slides, then concatenate
ffmpeg -f concat -safe 0 -i filelist.txt -c copy nexusfix_overview.mp4
```

Optional: add fade transitions between slides:
```bash
# xfade filter for crossfade between clips
ffmpeg -i clip01.mp4 -i clip02.mp4 \
  -filter_complex "xfade=transition=fade:duration=0.5:offset=<duration>" \
  merged.mp4
```

### Step 4: Upload to YouTube

- Upload as unlisted or public
- Title: "NexusFIX - Zero-Cost FIX Engine for Modern C++ | C++Online 2026"
- Description: Category overview + link to Q&A chatbot
- Add English captions (auto or manual)
- Get YouTube URL for Gather Town

---

## File Output

```
docs/chatbot/video/
  slides/
    slide01.html    # or slide01.png
    slide02.html
    ...
    slide15.html
  narration/
    narration01.mp3
    narration02.mp3
    ...
    narration15.mp3
  script.txt        # Full narration script
  filelist.txt      # ffmpeg concat list
  nexusfix_overview.mp4   # Final video
```

---

## Acceptance Criteria

| # | Criteria | Status |
|---|----------|--------|
| 1 | 15 slides created (1920x1080 landscape, dark theme) | [ ] |
| 2 | Narration script written (15 segments, English) | [ ] |
| 3 | edge-tts audio generated (15 x .mp3) | [ ] |
| 4 | Video assembled (.mp4, ~3-4 minutes) | [ ] |
| 5 | Video uploaded to YouTube | [ ] |
| 6 | YouTube URL ready for Gather Town | [ ] |
| 7 | Submitted before 2026-02-28 deadline | [ ] |

---

## Notes

- Booth recommended viewing: 3-5 minutes - our ~4 min fits perfectly
- Each slide ~15-20 seconds gives viewers time to read bullets while hearing narration
- Reuse edge-tts + SSML setup from `generate_audio.py` for consistent voice
- Dark theme matches chatbot and poster for visual consistency across all 3 booth objects
- Video gitignored (too large for repo), uploaded directly to YouTube
- Captions recommended for accessibility
