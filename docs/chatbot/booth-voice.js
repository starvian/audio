/* booth-voice.js - Voice input for booth mode (GitHub Pages) */

(function () {
    'use strict';

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var micBtn = document.getElementById('mic-btn');

    if (!SpeechRecognition || !micBtn) {
        if (micBtn) micBtn.style.display = 'none';
        return;
    }

    var recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    var listening = false;
    var searchInput = document.getElementById('search-input');

    function startListening() {
        try {
            recognition.start();
            listening = true;
            micBtn.classList.add('listening');
        } catch (e) {
            // Already started
        }
    }

    function stopListening() {
        try {
            recognition.stop();
        } catch (e) {
            // Not started
        }
        listening = false;
        micBtn.classList.remove('listening');
    }

    micBtn.addEventListener('click', function () {
        if (listening) {
            stopListening();
        } else {
            startListening();
        }
    });

    recognition.onresult = function (event) {
        var last = event.results[event.results.length - 1];
        var transcript = last[0].transcript.trim();
        if (!transcript) return;

        if (searchInput) searchInput.value = transcript;

        if (last.isFinal) {
            var results = window.searchQA(transcript);
            window.renderResults(results, transcript);
            autoPlayTop(results);
        }
    };

    recognition.onend = function () {
        listening = false;
        micBtn.classList.remove('listening');
    };

    recognition.onerror = function (event) {
        if (event.error === 'no-speech' || event.error === 'aborted') return;
        if (event.error === 'not-allowed') {
            micBtn.title = 'Microphone blocked - check browser permissions';
        }
        listening = false;
        micBtn.classList.remove('listening');
    };

    // Auto-play short audio for top match
    var audioEl = null;

    function autoPlayTop(results) {
        if (!results || results.length === 0) return;
        var top = results[0];
        if (top.score < 10) return;
        var audioPath = top.item.audio_short;
        if (!audioPath) return;

        if (audioEl) {
            audioEl.pause();
            audioEl = null;
        }
        audioEl = new Audio(audioPath);
        audioEl.play().catch(function () {
            // Autoplay blocked - user interaction required, ignore
        });
    }
})();
