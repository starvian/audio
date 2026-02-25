#!/usr/bin/env bash
# setup_audio.sh - PulseAudio dual-sink setup for NexusFix Presenter Mode
#
# Creates two virtual audio sinks:
#   GatherIn  - Capture Gather Town audio for Speech API (STT input)
#   TTSOut    - Route TTS playback to Gather Town microphone (TTS output)
#
# This isolation prevents TTS audio from feeding back into STT.
#
# Usage:
#   ./setup_audio.sh setup     # Create sinks and loopback
#   ./setup_audio.sh verify    # Check sink status
#   ./setup_audio.sh teardown  # Remove sinks and loopback
#
# After setup, use pavucontrol to:
#   1. Recording tab: Set Chrome's speech recognition to capture from "GatherIn.monitor"
#   2. Playback tab: Set Chrome's TTS audio to output on "TTSOut"
#   3. Recording tab: Gather Town mic input captures from "TTSOut.monitor"

set -euo pipefail

GATHER_SINK="GatherIn"
TTS_SINK="TTSOut"

setup() {
    echo "=== Creating PulseAudio virtual sinks ==="

    # Create GatherIn sink (receives Gather Town audio for STT)
    if pactl list sinks short | grep -q "$GATHER_SINK"; then
        echo "  $GATHER_SINK already exists, skipping"
    else
        pactl load-module module-null-sink sink_name="$GATHER_SINK" \
            sink_properties=device.description="$GATHER_SINK"
        echo "  Created $GATHER_SINK"
    fi

    # Create TTSOut sink (receives TTS audio, loops back to Gather Town mic)
    if pactl list sinks short | grep -q "$TTS_SINK"; then
        echo "  $TTS_SINK already exists, skipping"
    else
        pactl load-module module-null-sink sink_name="$TTS_SINK" \
            sink_properties=device.description="$TTS_SINK"
        echo "  Created $TTS_SINK"
    fi

    # Loopback: TTSOut monitor -> default source (Gather Town picks up as mic)
    # This lets Gather Town attendees hear the TTS response
    if pactl list modules short | grep -q "module-loopback.*source=${TTS_SINK}.monitor"; then
        echo "  Loopback already exists, skipping"
    else
        pactl load-module module-loopback \
            source="${TTS_SINK}.monitor" \
            sink_input_properties=media.name="TTSOut-to-GatherMic"
        echo "  Created loopback: ${TTS_SINK}.monitor -> default sink"
    fi

    echo ""
    echo "=== Setup complete ==="
    echo ""
    echo "Next steps (pavucontrol):"
    echo "  1. Open pavucontrol"
    echo "  2. Recording tab: Set Chrome speech recognition to '${GATHER_SINK}.monitor'"
    echo "  3. Playback tab: Verify Chrome TTS outputs to '${TTS_SINK}'"
    echo "  4. Route Gather Town audio to '${GATHER_SINK}'"
    echo ""
    echo "Run './setup_audio.sh verify' to check status."
}

verify() {
    echo "=== Verifying PulseAudio sinks ==="
    echo ""

    echo "Sinks:"
    if pactl list sinks short | grep -q "$GATHER_SINK"; then
        echo "  [OK] $GATHER_SINK"
    else
        echo "  [MISSING] $GATHER_SINK"
    fi

    if pactl list sinks short | grep -q "$TTS_SINK"; then
        echo "  [OK] $TTS_SINK"
    else
        echo "  [MISSING] $TTS_SINK"
    fi

    echo ""
    echo "Sources (monitors):"
    if pactl list sources short | grep -q "${GATHER_SINK}.monitor"; then
        echo "  [OK] ${GATHER_SINK}.monitor"
    else
        echo "  [MISSING] ${GATHER_SINK}.monitor"
    fi

    if pactl list sources short | grep -q "${TTS_SINK}.monitor"; then
        echo "  [OK] ${TTS_SINK}.monitor"
    else
        echo "  [MISSING] ${TTS_SINK}.monitor"
    fi

    echo ""
    echo "Loopback modules:"
    pactl list modules short | grep "module-loopback" || echo "  (none)"
}

teardown() {
    echo "=== Removing PulseAudio virtual sinks ==="

    # Remove loopback modules first
    for module_id in $(pactl list modules short | grep "module-loopback" | awk '{print $1}'); do
        pactl unload-module "$module_id" && echo "  Removed loopback module $module_id"
    done

    # Remove sinks
    for module_id in $(pactl list modules short | grep "module-null-sink" | awk '{print $1}'); do
        local desc
        desc=$(pactl list modules | grep -A5 "Module #${module_id}" | grep "sink_name" || true)
        if echo "$desc" | grep -q "$GATHER_SINK\|$TTS_SINK"; then
            pactl unload-module "$module_id" && echo "  Removed null-sink module $module_id"
        fi
    done

    echo ""
    echo "=== Teardown complete ==="
}

# === Main ===
case "${1:-}" in
    setup)
        setup
        ;;
    verify)
        verify
        ;;
    teardown)
        teardown
        ;;
    *)
        echo "Usage: $0 {setup|verify|teardown}"
        echo ""
        echo "  setup     - Create GatherIn + TTSOut sinks and loopback"
        echo "  verify    - Check sink status"
        echo "  teardown  - Remove all virtual sinks and loopbacks"
        exit 1
        ;;
esac
