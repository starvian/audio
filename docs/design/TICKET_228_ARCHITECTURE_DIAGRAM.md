# TICKET_228: Export Architecture Diagram (PNG/SVG) for Gather Town

## Status: Done
## Priority: High
## Category: Conference / Pre-Submission Deliverable
## Parent: TICKET_225
## Date: 2026-02-25
## Deadline: Before conference

---

## Objective

Export a standalone architecture diagram as PNG or SVG for upload to Gather Town as an Image object in the poster booth.

## Source

The poster (`post/poster.html`) contains an inline SVG architecture diagram showing:
- Network Input -> FIX Parser -> Session State Machine -> Transport Layer
- Side panel: Memory (PMR Arena, SessionHeap, SPSC Queue)
- Annotations: SIMD + Zero-Copy, O(1) Field Access, TCP / io_uring
- FIX 4.4 / 5.0 / FIXT 1.1 support note

## Requirements

1. Extract or recreate the architecture diagram as a standalone file
2. Format: PNG (high-res, 2x or 3x) or SVG
3. Dark background matching poster theme (#0A1628)
4. Clear labels, readable at booth viewing distance
5. Optional: expand the diagram with more detail than the poster version (e.g., add SPSC queue flow, io_uring event loop)

## Approach Options

**Option A**: Extract the inline SVG from poster.html, add background, save as standalone SVG/PNG.

**Option B**: Screenshot the architecture section from poster.html at high resolution.

**Option C**: Create an enhanced standalone architecture diagram with more detail.

## Output

- `post/architecture.png` or `post/architecture.svg`

## Upload Target

- Gather Town back-end (Object type: Image)

## Output Generated

- `post/architecture.svg` - Standalone SVG, 840x400 (2x), dark background (#0A1628)

## Acceptance Criteria

- [x] Standalone image file (SVG)
- [x] Dark theme consistent with poster
- [x] All components labeled clearly
- [x] Resolution suitable for Gather Town display
