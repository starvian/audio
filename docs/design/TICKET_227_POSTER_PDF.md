# TICKET_227: Generate Poster PDF for Gather Town Upload

## Status: Done (Manual)
## Priority: High
## Category: Conference / Pre-Submission Deliverable
## Parent: TICKET_225
## Date: 2026-02-25
## Deadline: Before conference

---

## Objective

Generate a high-quality PDF from `post/poster.html` for upload to the Gather Town back-end. The organizers (or the presenter) will upload this PDF as the poster image in the poster booth.

## Source

- `post/poster.html` - NexusFIX C++Online 2026 poster (1600x900px landscape)

## Requirements

1. Render `poster.html` to PDF at full resolution (1600x900 or higher)
2. Landscape orientation
3. All fonts rendered (JetBrains Mono, Inter via Google Fonts)
4. SVG architecture diagram preserved
5. CSS gradients and backgrounds intact
6. No blank margins or page breaks

## Approach

Open `post/poster.html` in Chrome, Ctrl+P, Save as PDF (landscape, no margins).

Note: Chrome headless `--print-to-pdf` truncates the bottom section (Architecture, Use Cases, Resources, Footer) due to paper size limitations. Manual print from the browser captures the full content correctly.

## Output

- `post/poster.pdf` - Final poster PDF

## Upload Target

- Gather Town back-end (Object type: Image / Poster)
- Organizers may handle the upload

## Acceptance Criteria

- [ ] PDF generated from poster.html
- [ ] Landscape orientation, no margins
- [ ] All visual elements render correctly (fonts, SVG, gradients)
- [ ] File size reasonable (< 5MB)
