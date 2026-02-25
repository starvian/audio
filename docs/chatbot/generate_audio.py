#!/usr/bin/env python3
"""generate_audio.py - Batch TTS generation for NexusFix Q&A chatbot.

Generates 182 short + 182 full = 364 .mp3 files using edge-tts.
Output: docs/chatbot/audio/

Usage:
    pip install edge-tts
    python3 generate_audio.py
"""

import asyncio
import hashlib
import json
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
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
QA_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa-data.js")
MAX_CONCURRENT = 5

# === SSML Pronunciation Rules ===
# Technical terms that need pronunciation guidance
PRONUNCIATION_MAP = {
    "SIMD": "S.I.M.D.",
    "PMR": "P.M.R.",
    "SBE": "S.B.E.",
    "SOH": "S.O.H.",
    "NexusFix": "Nexus Fix",
    "NexusFIX": "Nexus Fix",
    "P99": "P 99",
    "MPSC": "M.P.S.C.",
    "constexpr": "const expr",
    "std::expected": "standard expected",
    "std::variant": "standard variant",
    "std::string_view": "standard string view",
    "std::span": "standard span",
    "std::pmr": "standard P.M.R.",
    "FIX": "FIX",
    "FIXT": "FIXT",
    "IPC": "I.P.C.",
    "LMAX": "L. Max",
    "TCP": "T.C.P.",
    "FPGA": "F.P.G.A.",
    "SOA": "S.O.A.",
    "AOS": "A.O.S.",
    "AVX": "A.V.X.",
    "SSE": "S.S.E.",
    "DPDK": "D.P.D.K.",
    "io_uring": "I.O. u-ring",
    "epoll": "e-poll",
    "uint8_t": "unsigned 8-bit integer",
    "uint64_t": "unsigned 64-bit integer",
}


def apply_pronunciation(text):
    """Replace technical terms with pronunciation-friendly versions."""
    result = text
    # Sort by length descending to match longer terms first
    sorted_terms = sorted(PRONUNCIATION_MAP.keys(), key=len, reverse=True)
    for term in sorted_terms:
        replacement = PRONUNCIATION_MAP[term]
        # Word-boundary-aware replacement
        pattern = re.compile(r'\b' + re.escape(term) + r'\b')
        result = pattern.sub(replacement, result)
    return result


def parse_qa_data(filepath):
    """Parse qa-data.js to extract Q&A items."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the JS variable declaration: "const qaData = " and trailing ";"
    match = re.search(r'const\s+qaData\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
    if not match:
        print("Error: Could not parse qa-data.js")
        sys.exit(1)

    data = json.loads(match.group(1))
    items = []
    for category in data['categories']:
        for question in category['questions']:
            items.append({
                'audio_short': question.get('audio_short', ''),
                'audio_full': question.get('audio_full', ''),
                'a_short': question.get('a_short', ''),
                'a': question.get('a', ''),
            })
    return items


def sha256_file(filepath):
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


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
    print(f"Parsing Q&A data from {QA_DATA_FILE}...")
    items = parse_qa_data(QA_DATA_FILE)
    print(f"Found {len(items)} Q&A items ({len(items) * 2} audio files to generate)")

    # Create output directory
    os.makedirs(AUDIO_DIR, exist_ok=True)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = []
    manifest_entries = []

    for item in items:
        # Short version
        if item['audio_short'] and item['a_short']:
            short_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                item['audio_short']
            )
            os.makedirs(os.path.dirname(short_path), exist_ok=True)
            tasks.append(generate_one(item['a_short'], short_path, semaphore))
            manifest_entries.append({
                'path': item['audio_short'],
                'abs_path': short_path,
                'version': 'short',
            })

        # Full version
        if item['audio_full'] and item['a']:
            full_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                item['audio_full']
            )
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            tasks.append(generate_one(item['a'], full_path, semaphore))
            manifest_entries.append({
                'path': item['audio_full'],
                'abs_path': full_path,
                'version': 'full',
            })

    print(f"\nGenerating {len(tasks)} audio files (concurrency={MAX_CONCURRENT})...")
    results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"\nDone: {success} generated, {failed} failed")

    # Build manifest
    print("Building manifest.json...")
    manifest = []
    for entry in manifest_entries:
        if os.path.exists(entry['abs_path']):
            manifest.append({
                'path': entry['path'],
                'version': entry['version'],
                'sha256': sha256_file(entry['abs_path']),
                'size': os.path.getsize(entry['abs_path']),
            })

    manifest_path = os.path.join(AUDIO_DIR, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written: {manifest_path} ({len(manifest)} entries)")


if __name__ == '__main__':
    asyncio.run(main())
