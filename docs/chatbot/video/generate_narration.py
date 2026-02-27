#!/usr/bin/env python3
"""generate_narration.py - Generate narration audio for slideshow video.

Generates 15 .mp3 files (one per slide) using edge-tts.
Reuses SSML pronunciation rules from generate_audio.py.

Usage:
    pip install edge-tts
    python3 generate_narration.py
"""

import asyncio
import os
import re
import sys

try:
    import edge_tts
except ImportError:
    print("Error: edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)

# === Configuration ===
VOICE = "en-US-GuyNeural"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NARRATION_DIR = os.path.join(SCRIPT_DIR, "narration")
SCRIPT_FILE = os.path.join(SCRIPT_DIR, "script.txt")
MAX_CONCURRENT = 3

# === SSML Pronunciation Rules (from generate_audio.py) ===
PRONUNCIATION_MAP = {
    "SIMD": "S.I.M.D.",
    "PMR": "P.M.R.",
    "SBE": "S.B.E.",
    "SOH": "S.O.H.",
    "NexusFix": "Nexus Fix",
    "NexusFIX": "Nexus Fix",
    "P99": "P 99",
    "P50": "P 50",
    "MPSC": "M.P.S.C.",
    "constexpr": "const expr",
    "consteval": "const eval",
    "std::expected": "standard expected",
    "std::variant": "standard variant",
    "std::string_view": "standard string view",
    "std::span": "standard span",
    "std::pmr": "standard P.M.R.",
    "std::construct_at": "standard construct at",
    "std::source_location": "standard source location",
    "std::unreachable": "standard unreachable",
    "std::to_underlying": "standard to underlying",
    "std::print": "standard print",
    "FIX": "FIX",
    "FIXT": "FIXT",
    "IPC": "I.P.C.",
    "LMAX": "L. Max",
    "TCP": "T.C.P.",
    "FPGA": "F.P.G.A.",
    "AVX2": "A.V.X. 2",
    "AVX-512": "A.V.X. 512",
    "SSE4.2": "S.S.E. 4 point 2",
    "SSE": "S.S.E.",
    "AVX": "A.V.X.",
    "NEON": "Neon",
    "RDTSC": "R.D.T.S.C.",
    "FNV-1a": "F.N.V. one a",
    "CRTP": "C.R.T.P.",
    "xsimd": "x-simd",
    "simdjson": "simd-json",
    "mimalloc": "me-malloc",
    "glibc": "g-lib-c",
    "CMake": "C Make",
    "FetchContent": "Fetch Content",
    "MSVC": "M.S.V.C.",
    "GCC": "G.C.C.",
    "seq_cst": "sequential consistency",
    "string_view": "string view",
    "unordered_map": "unordered map",
}


def apply_pronunciation(text):
    """Replace technical terms with pronunciation-friendly versions."""
    result = text
    sorted_terms = sorted(PRONUNCIATION_MAP.keys(), key=len, reverse=True)
    for term in sorted_terms:
        replacement = PRONUNCIATION_MAP[term]
        pattern = re.compile(r'\b' + re.escape(term) + r'\b')
        result = pattern.sub(replacement, result)
    return result


def parse_script(filepath):
    """Parse script.txt into per-slide narration segments."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    segments = []
    parts = re.split(r'\nSLIDE \d+', content)
    # First part may start with "SLIDE 1"
    if content.startswith('SLIDE'):
        parts = re.split(r'SLIDE \d+', content)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Remove the header line (e.g., "- Title (10s)")
        lines = part.split('\n')
        header = lines[0] if lines else ''
        narration = '\n'.join(lines[1:]).strip()
        if narration:
            segments.append({
                'header': header.strip(' -'),
                'text': narration,
            })

    return segments


async def generate_one(text, output_path, semaphore):
    """Generate a single .mp3 file using edge-tts."""
    async with semaphore:
        if os.path.exists(output_path):
            print(f"  Skip (exists): {os.path.basename(output_path)}")
            return True

        tts_text = apply_pronunciation(text)
        try:
            communicate = edge_tts.Communicate(tts_text, VOICE)
            await communicate.save(output_path)
            print(f"  Generated: {os.path.basename(output_path)}")
            return True
        except Exception as e:
            print(f"  FAILED: {os.path.basename(output_path)} - {e}")
            return False


async def main():
    print(f"Parsing narration script from {SCRIPT_FILE}...")
    segments = parse_script(SCRIPT_FILE)
    print(f"Found {len(segments)} slide segments")

    if len(segments) != 15:
        print(f"WARNING: Expected 15 segments, found {len(segments)}")

    os.makedirs(NARRATION_DIR, exist_ok=True)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = []

    for i, segment in enumerate(segments, start=1):
        output_path = os.path.join(NARRATION_DIR, f"narration{i:02d}.mp3")
        print(f"  Slide {i}: {segment['header']}")
        tasks.append(generate_one(segment['text'], output_path, semaphore))

    print(f"\nGenerating {len(tasks)} narration files (concurrency={MAX_CONCURRENT})...")
    results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"\nDone: {success} generated, {failed} failed")


if __name__ == '__main__':
    asyncio.run(main())
