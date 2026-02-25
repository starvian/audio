/* voice.js - Web Speech API integration (presenter mode) */

(function () {
    'use strict';

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('Web Speech API not supported in this browser');
        return;
    }

    // === VoiceRecognizer Class ===
    function VoiceRecognizer() {
        this.recognition = null;
        this.listening = false;
        this.paused = false;

        // Callbacks (set by consumer)
        this.onInterim = null;
        this.onFinal = null;

        // L3 echo detection state
        this._recentFinals = []; // { text, timestamp }
        this._echoWindowMs = 5000;
        this._echoThreshold = 0.5; // 50% word overlap

        this._init();
    }

    VoiceRecognizer.prototype._init = function () {
        var self = this;
        var rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';
        rec.maxAlternatives = 1;

        rec.onresult = function (event) {
            if (self.paused) return;

            var last = event.results[event.results.length - 1];
            var transcript = last[0].transcript.trim();

            if (!transcript) return;

            if (last.isFinal) {
                // L3 echo check
                if (self.isEcho(transcript)) {
                    console.log('Echo detected, ignoring:', transcript);
                    return;
                }
                self._recordFinal(transcript);
                if (self.onFinal) self.onFinal(transcript);
            } else {
                if (self.onInterim) self.onInterim(transcript);
            }
        };

        rec.onerror = function (event) {
            if (event.error === 'no-speech') return; // Ignore silence
            if (event.error === 'aborted') return;   // Intentional stop
            console.error('Speech recognition error:', event.error);
        };

        rec.onend = function () {
            // Auto-restart if still supposed to be listening
            if (self.listening && !self.paused) {
                try {
                    rec.start();
                } catch (e) {
                    // Already started - ignore
                }
            }
        };

        this.recognition = rec;
    };

    VoiceRecognizer.prototype.start = function () {
        if (this.listening) return;
        this.listening = true;
        this.paused = false;
        try {
            this.recognition.start();
        } catch (e) {
            console.error('Failed to start recognition:', e);
        }
    };

    VoiceRecognizer.prototype.stop = function () {
        this.listening = false;
        this.paused = false;
        try {
            this.recognition.stop();
        } catch (e) {
            // Ignore if not started
        }
    };

    VoiceRecognizer.prototype.pause = function () {
        if (!this.listening) return;
        this.paused = true;
        try {
            this.recognition.stop();
        } catch (e) {
            // Ignore
        }
    };

    VoiceRecognizer.prototype.resume = function () {
        if (!this.listening) return;
        this.paused = false;
        try {
            this.recognition.start();
        } catch (e) {
            // Ignore if already started
        }
    };

    // === L3 Echo Detection ===

    VoiceRecognizer.prototype._recordFinal = function (text) {
        this._recentFinals.push({ text: text, timestamp: Date.now() });
        this._pruneOldFinals();
    };

    VoiceRecognizer.prototype._pruneOldFinals = function () {
        var cutoff = Date.now() - this._echoWindowMs;
        while (this._recentFinals.length > 0 && this._recentFinals[0].timestamp < cutoff) {
            this._recentFinals.shift();
        }
    };

    VoiceRecognizer.prototype.isEcho = function (transcript) {
        this._pruneOldFinals();
        var words = transcript.toLowerCase().split(/\s+/);
        if (words.length === 0) return false;

        for (var i = 0; i < this._recentFinals.length; i++) {
            var prevWords = this._recentFinals[i].text.toLowerCase().split(/\s+/);
            var overlap = 0;
            for (var w = 0; w < words.length; w++) {
                if (prevWords.indexOf(words[w]) !== -1) {
                    overlap++;
                }
            }
            if (overlap / words.length >= this._echoThreshold) {
                return true;
            }
        }
        return false;
    };

    // Record TTS output text for echo detection
    VoiceRecognizer.prototype.recordTtsOutput = function (text) {
        this._recentFinals.push({ text: text, timestamp: Date.now() });
    };

    // === Expose globally ===
    window.voiceRecognizer = new VoiceRecognizer();
})();
