#!/usr/bin/env python3
"""assemble_video.py - Assemble slideshow video from HTML slides + narration.

Steps:
1. Screenshot each slide HTML to PNG via Chrome headless (1920x1080)
2. Combine each PNG + narration .mp3 into video clips
3. Concatenate with fade transitions into final .mp4

Usage:
    pip install moviepy
    python3 assemble_video.py

Requirements:
    - playwright (with chromium installed: playwright install chromium)
    - moviepy (includes ffmpeg)
    - 15 slide HTML files in slides/
    - 15 narration MP3 files in narration/
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(SCRIPT_DIR, "slides")
NARRATION_DIR = os.path.join(SCRIPT_DIR, "narration")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "nexusfix_overview.mp4")
NUM_SLIDES = 15
FADE_DURATION = 0.5


def screenshot_slides():
    """Screenshot each slide HTML to PNG via Playwright Chromium."""
    from playwright.sync_api import sync_playwright

    print("=== Step 1: Screenshotting slides ===")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        for i in range(1, NUM_SLIDES + 1):
            html_file = os.path.join(SLIDES_DIR, f"slide{i:02d}.html")
            png_file = os.path.join(SLIDES_DIR, f"slide{i:02d}.png")

            if os.path.exists(png_file):
                print(f"  Skip (exists): slide{i:02d}.png")
                continue

            if not os.path.exists(html_file):
                print(f"  ERROR: {html_file} not found")
                sys.exit(1)

            page.goto(f"file://{html_file}")
            page.wait_for_timeout(2000)
            page.screenshot(path=png_file, full_page=False)

            size = os.path.getsize(png_file)
            print(f"  Generated: slide{i:02d}.png ({size // 1024} KB)")

        browser.close()


def assemble_video():
    """Combine slide PNGs + narration into final video."""
    print("\n=== Step 2: Assembling video ===")

    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        print("Error: moviepy not installed. Run: pip install moviepy")
        sys.exit(1)

    clips = []
    for i in range(1, NUM_SLIDES + 1):
        png_file = os.path.join(SLIDES_DIR, f"slide{i:02d}.png")
        mp3_file = os.path.join(NARRATION_DIR, f"narration{i:02d}.mp3")

        if not os.path.exists(png_file):
            print(f"  ERROR: {png_file} not found")
            sys.exit(1)
        if not os.path.exists(mp3_file):
            print(f"  ERROR: {mp3_file} not found")
            sys.exit(1)

        audio = AudioFileClip(mp3_file)
        # Add 1 second padding after narration for breathing room
        duration = audio.duration + 1.0

        clip = (
            ImageClip(png_file)
            .with_duration(duration)
            .with_audio(audio)
        )

        # Add fade in/out for non-first/last clips
        if i > 1:
            clip = clip.with_effects([
                __import__('moviepy').video.fx.CrossFadeIn(FADE_DURATION)
            ])

        clips.append(clip)
        print(f"  Slide {i:02d}: {duration:.1f}s")

    print(f"\n  Concatenating {len(clips)} clips...")
    final = concatenate_videoclips(clips, method="compose", padding=-FADE_DURATION)
    total_duration = final.duration
    print(f"  Total duration: {total_duration:.0f}s ({total_duration/60:.1f} min)")

    print(f"\n  Writing to {OUTPUT_FILE}...")
    final.write_videofile(
        OUTPUT_FILE,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        preset="medium",
        threads=4,
        logger="bar",
    )

    # Cleanup
    for clip in clips:
        clip.close()
    final.close()

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\n  Output: {OUTPUT_FILE} ({size_mb:.1f} MB)")


def create_filelist():
    """Create ffmpeg concat filelist.txt for reference."""
    filelist_path = os.path.join(SCRIPT_DIR, "filelist.txt")
    with open(filelist_path, 'w') as f:
        for i in range(1, NUM_SLIDES + 1):
            f.write(f"file 'slides/slide{i:02d}.png'\n")
    print(f"  Created: {filelist_path}")


def main():
    print(f"Slides dir: {SLIDES_DIR}")
    print(f"Narration dir: {NARRATION_DIR}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    screenshot_slides()
    create_filelist()
    assemble_video()

    print("\n=== Done! ===")
    print(f"Video ready: {OUTPUT_FILE}")
    print("Next: Upload to YouTube")


if __name__ == '__main__':
    main()
