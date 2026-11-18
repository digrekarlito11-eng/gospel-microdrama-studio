/**
 * AMINA Experience — Afrogospel Ambient Audio Engine
 * Plays bgm_gospel.mp3 in loop, supports smooth ducking on video playback,
 * and features a procedural polyphonic Web Audio API synthesizer fallback.
 */

(function (global) {
  'use strict';

  class AudioEngine {
    constructor() {
      this.audioSrc = 'episodes/ep-001/audio/bgm_gospel.mp3';
      this.audioEl = null;
      this.isPlaying = false;
      this.isDucked = false;
      this.userVolume = 0.65;
      this.isMuted = false;
      this.isSynthFallback = false;
      this.audioCtx = null;
      this.synthNodes = [];
      this.masterGain = null;
      this.duckInterval = null;
    }

    init() {
      if (typeof window === 'undefined' || typeof document === 'undefined') return;

      // Check stored preference
      const prefs = window.AminaState ? window.AminaState.getPreferences() : {};
      if (prefs.volume !== undefined) this.userVolume = prefs.volume;

      if (typeof Audio !== 'undefined') {
        this.audioEl = new Audio();
        this.audioEl.src = this.audioSrc;
        this.audioEl.loop = true;
        this.audioEl.volume = this.userVolume;
        this.audioEl.preload = 'auto';

        // Fallback on error (e.g. offline or 404)
        this.audioEl.addEventListener('error', (err) => {
          console.warn('[AminaAudio] MP3 loading failed, switching to Web Audio procedural synth fallback', err);
          this._setupWebAudioSynth();
        });
      }

      this._updateUI();
    }

    play() {
      if (typeof window === 'undefined') return;

      if (this.isSynthFallback) {
        this._startWebAudioSynth();
        this.isPlaying = true;
        this._updateUI();
        return;
      }

      if (!this.audioEl) return;
      this.audioEl.volume = this.isDucked ? 0.08 : this.userVolume;
      const promise = this.audioEl.play();
      if (promise !== undefined) {
        promise.then(() => {
          if (this.audioEl && !this.audioEl.paused) {
            this.isPlaying = true;
            this._updateUI();
          }
        }).catch(err => {
          console.log('[AminaAudio] Audio autoplay blocked until user gesture:', err);
          this.isPlaying = false;
          this._updateUI();
        });
      }
    }

    pause() {
      if (this.isSynthFallback) {
        this._stopWebAudioSynth();
      } else if (this.audioEl) {
        this.audioEl.pause();
      }
      this.isPlaying = false;
      this._updateUI();
    }

    toggle() {
      if (this.isPlaying) {
        this.pause();
      } else {
        this.play();
      }
    }

    /**
     * Ducking: smoothly lowers ambient volume when a micro-drama video is playing
     */
    duck() {
      this.isDucked = true;
      if (this.duckInterval) clearInterval(this.duckInterval);

      if (this.isSynthFallback && this.masterGain) {
        if (this.audioCtx) {
          this.masterGain.gain.setValueAtTime(0.04, this.audioCtx.currentTime);
        }
        if (this.masterGain.gain) {
          this.masterGain.gain.value = 0.04;
        }
        return;
      }

      if (!this.audioEl) return;
      const targetVol = 0.05;
      const step = (this.audioEl.volume - targetVol) / 10;
      let count = 0;

      this.duckInterval = setInterval(() => {
        count++;
        if (this.audioEl.volume > targetVol) {
          this.audioEl.volume = Math.max(targetVol, this.audioEl.volume - step);
        }
        if (count >= 10 || this.audioEl.volume <= targetVol) {
          this.audioEl.volume = targetVol;
          clearInterval(this.duckInterval);
          this.duckInterval = null;
        }
      }, 30);
    }

    /**
     * Unduck: smoothly restores ambient gospel music when video pauses or tab switches
     */
    unduck() {
      this.isDucked = false;
      if (this.duckInterval) clearInterval(this.duckInterval);

      if (this.isSynthFallback && this.masterGain) {
        this.masterGain.gain.setValueAtTime(this.userVolume * 0.25, this.audioCtx.currentTime);
        return;
      }

      if (!this.audioEl) return;
      const targetVol = this.userVolume;
      const step = (targetVol - this.audioEl.volume) / 10;
      let count = 0;

      this.duckInterval = setInterval(() => {
        count++;
        if (this.audioEl.volume < targetVol) {
          this.audioEl.volume = Math.min(targetVol, this.audioEl.volume + step);
        }
        if (count >= 10 || this.audioEl.volume >= targetVol) {
          this.audioEl.volume = targetVol;
          clearInterval(this.duckInterval);
          this.duckInterval = null;
        }
      }, 30);
    }

    setVolume(val) {
      this.userVolume = Math.max(0, Math.min(1, val));
      if (!this.isDucked && this.audioEl) {
        this.audioEl.volume = this.userVolume;
      }
      if (this.masterGain && this.audioCtx) {
        this.masterGain.gain.setValueAtTime(this.userVolume * 0.25, this.audioCtx.currentTime);
      }
      if (typeof window !== 'undefined' && window.AminaState) {
        window.AminaState.setPreference('volume', this.userVolume);
      }
    }

    /**
     * Procedural Web Audio API Synthesizer Fallback
     * Generates a warm, celestial polyphonic gospel chord pad
     * using harmonic sine waves with a gentle resonant lowpass filter
     */
    _setupWebAudioSynth() {
      if (typeof window === 'undefined') return;
      this.isSynthFallback = true;
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        this.audioCtx = new AudioContext();
      } catch (e) {
        console.warn('[AminaAudio] Web Audio API not supported', e);
      }
    }

    _startWebAudioSynth() {
      if (!this.audioCtx) this._setupWebAudioSynth();
      if (!this.audioCtx) return;

      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }

      this._stopWebAudioSynth(); // clear any prior nodes

      // Master Gain
      this.masterGain = this.audioCtx.createGain();
      this.masterGain.gain.setValueAtTime(this.isDucked ? 0.04 : this.userVolume * 0.22, this.audioCtx.currentTime);

      // Lowpass Biquad Filter for warm analog gospel warmth
      const filter = this.audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(650, this.audioCtx.currentTime);
      filter.Q.setValueAtTime(1.8, this.audioCtx.currentTime);

      // Celestial F Major 9 chord frequencies: F3 (174.61), A3 (220.00), C4 (261.63), E4 (329.63), G4 (392.00)
      const chordFreqs = [174.61, 220.00, 261.63, 329.63, 392.00];

      chordFreqs.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const oscGain = this.audioCtx.createGain();

        osc.type = idx % 2 === 0 ? 'sine' : 'triangle';
        osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);

        // Subtle slow chorus detune
        const detuneLfo = this.audioCtx.createOscillator();
        const detuneLfoGain = this.audioCtx.createGain();
        detuneLfo.frequency.setValueAtTime(0.2 + (idx * 0.08), this.audioCtx.currentTime);
        detuneLfoGain.gain.setValueAtTime(3.5, this.audioCtx.currentTime);
        detuneLfo.connect(detuneLfoGain);
        detuneLfoGain.connect(osc.detune);
        detuneLfo.start();

        oscGain.gain.setValueAtTime(0.18 / chordFreqs.length, this.audioCtx.currentTime);

        osc.connect(oscGain);
        oscGain.connect(filter);
        osc.start();

        this.synthNodes.push(osc, detuneLfo, detuneLfoGain, oscGain);
      });

      filter.connect(this.masterGain);
      this.masterGain.connect(this.audioCtx.destination);
    }

    _stopWebAudioSynth() {
      this.synthNodes.forEach(node => {
        try {
          if (node.stop) node.stop();
          if (node.disconnect) node.disconnect();
        } catch (e) {}
      });
      this.synthNodes = [];
    }

    _updateUI() {
      if (typeof document === 'undefined') return;
      const bar = document.getElementById('ambient-audio-bar');
      const label = document.getElementById('ambient-audio-label');
      if (!bar) return;

      if (this.isPlaying) {
        bar.classList.add('playing');
        if (label) label.textContent = 'Afrogospel On';
      } else {
        bar.classList.remove('playing');
        if (label) label.textContent = 'Musique';
      }
    }
  }

  const audioInstance = new AudioEngine();

  if (typeof window !== 'undefined') {
    window.AminaAudio = audioInstance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaAudio = audioInstance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaAudio: audioInstance, AudioEngine };
  }
})(typeof window !== 'undefined' ? window : globalThis);
