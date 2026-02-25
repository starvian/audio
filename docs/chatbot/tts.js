/* tts.js - TTS playback + audio sink routing + feedback prevention */

(function () {
    'use strict';

    // === TTSPlayer Class ===
    function TTSPlayer() {
        this.audio = null;
        this.outputSinkId = '';
        this.playing = false;
        this.onPlayStart = null;
        this.onPlayEnd = null;

        this._initSink();
    }

    TTSPlayer.prototype._initSink = function () {
        var self = this;
        // Try to find TTSOut sink via device enumeration
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;

        navigator.mediaDevices.enumerateDevices().then(function (devices) {
            for (var i = 0; i < devices.length; i++) {
                if (devices[i].kind === 'audiooutput' &&
                    devices[i].label.indexOf('TTSOut') !== -1) {
                    self.outputSinkId = devices[i].deviceId;
                    console.log('TTSOut sink found:', devices[i].label);
                    return;
                }
            }
            console.log('TTSOut sink not found, using default output');
        }).catch(function (err) {
            console.warn('Device enumeration failed:', err);
        });
    };

    TTSPlayer.prototype.playAnswer = function (qaItem, version) {
        var self = this;
        var audioPath = version === 'full' ? qaItem.audio_full : qaItem.audio_short;

        // Stop any current playback
        this.stop();

        // Try pre-generated .mp3 first
        if (audioPath) {
            this._playFile(audioPath);
            return;
        }

        // Fallback to browser SpeechSynthesis
        var text = version === 'full' ? qaItem.a : qaItem.a_short;
        this._playSpeechSynthesis(text);
    };

    TTSPlayer.prototype._playFile = function (path) {
        var self = this;
        var audio = new Audio(path);

        // Route to TTSOut sink if available
        if (this.outputSinkId && audio.setSinkId) {
            audio.setSinkId(this.outputSinkId).catch(function (err) {
                console.warn('setSinkId failed:', err);
            });
        }

        audio.onplay = function () {
            self.playing = true;
            if (self.onPlayStart) self.onPlayStart();
        };

        audio.onended = function () {
            self.playing = false;
            self.audio = null;
            if (self.onPlayEnd) self.onPlayEnd();
        };

        audio.onerror = function () {
            console.warn('Audio file failed, falling back to SpeechSynthesis');
            self.playing = false;
            self.audio = null;
            // Cannot recover the text here - onPlayEnd signals completion
            if (self.onPlayEnd) self.onPlayEnd();
        };

        this.audio = audio;
        audio.play().catch(function (err) {
            console.error('Audio play failed:', err);
            self.playing = false;
            self.audio = null;
            if (self.onPlayEnd) self.onPlayEnd();
        });
    };

    TTSPlayer.prototype._playSpeechSynthesis = function (text) {
        var self = this;
        speechSynthesis.cancel();

        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;

        utterance.onstart = function () {
            self.playing = true;
            if (self.onPlayStart) self.onPlayStart();
        };

        utterance.onend = function () {
            self.playing = false;
            if (self.onPlayEnd) self.onPlayEnd();
        };

        utterance.onerror = function () {
            self.playing = false;
            if (self.onPlayEnd) self.onPlayEnd();
        };

        speechSynthesis.speak(utterance);
    };

    TTSPlayer.prototype.stop = function () {
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
            this.audio = null;
        }
        speechSynthesis.cancel();
        this.playing = false;
    };

    // === AudioPipeline Class ===
    // Coordinates VoiceRecognizer + TTSPlayer with feedback prevention
    function AudioPipeline() {
        this.ttsPlayer = new TTSPlayer();
        this.ttsPlaying = false;
        this.autoPlay = false;
        this._postSilenceMs = 500;
        this._postSilenceTimer = null;

        this._bindTtsCallbacks();
    }

    AudioPipeline.prototype._bindTtsCallbacks = function () {
        var self = this;

        this.ttsPlayer.onPlayStart = function () {
            self.ttsPlaying = true;
            self._updatePlaybackStatus('Playing...');
            // L2: Pause STT during playback
            if (window.voiceRecognizer) {
                window.voiceRecognizer.pause();
            }
        };

        this.ttsPlayer.onPlayEnd = function () {
            self.ttsPlaying = false;
            self._updatePlaybackStatus('');
            // L2: Post-silence buffer before resuming STT
            clearTimeout(self._postSilenceTimer);
            self._postSilenceTimer = setTimeout(function () {
                if (window.voiceRecognizer) {
                    window.voiceRecognizer.resume();
                }
            }, self._postSilenceMs);
        };
    };

    AudioPipeline.prototype.onSpeechResult = function (transcript) {
        // Skip if TTS is playing (L2 state lock)
        if (this.ttsPlaying) return;

        // L3: Echo check
        if (window.voiceRecognizer && window.voiceRecognizer.isEcho(transcript)) {
            console.log('Pipeline echo rejected:', transcript);
            return;
        }

        var results = window.searchQA(transcript);
        window.renderResults(results, transcript);

        // Auto-play top result if enabled
        if (this.autoPlay && results.length > 0) {
            this.playAnswer(results[0].item, 'short');
        }
    };

    AudioPipeline.prototype.playAnswer = function (qaItem, version) {
        // Record TTS text for L3 echo detection
        if (window.voiceRecognizer) {
            var text = version === 'full' ? qaItem.a : qaItem.a_short;
            window.voiceRecognizer.recordTtsOutput(text);
        }

        this.ttsPlayer.playAnswer(qaItem, version);
    };

    AudioPipeline.prototype.stop = function () {
        this.ttsPlayer.stop();
        this.ttsPlaying = false;
        this._updatePlaybackStatus('');
        clearTimeout(this._postSilenceTimer);
        if (window.voiceRecognizer) {
            window.voiceRecognizer.resume();
        }
    };

    AudioPipeline.prototype._updatePlaybackStatus = function (text) {
        var el = document.getElementById('playback-status');
        if (el) el.textContent = text;
    };

    // === Expose globally ===
    // Only initialize on presenter page
    if (document.body && document.body.classList.contains('presenter-mode')) {
        window.ttsPlayer = new TTSPlayer();
        window.audioPipeline = new AudioPipeline();
    } else {
        // Defer initialization until DOM is ready
        var initPresenter = function () {
            if (document.body && document.body.classList.contains('presenter-mode')) {
                window.ttsPlayer = new TTSPlayer();
                window.audioPipeline = new AudioPipeline();
            }
        };
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initPresenter);
        } else {
            initPresenter();
        }
    }
})();
