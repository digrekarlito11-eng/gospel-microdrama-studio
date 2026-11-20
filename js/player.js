/**
 * AMINA Experience — 9:16 Vertical Video Player Engine
 * Implements TikTok/Shorts vertical gestures, safe-zone subtitles,
 * single-active media lifecycle, motion card fallback, audio ducking
 */

(function (global) {
  'use strict';

  class PlayerEngine {
    constructor() {
      this.container = null;
      this.episodes = [];
      this.currentIndex = 0;
      this.videoEl = null;
      this.isPlaying = false;
      this.isMuted = true;
      this.activeSubtitleCue = null;
      this.touchStartY = 0;
      this.touchStartX = 0;
      this.isSwiping = false;
      this.wheelTimeout = null;
      this.motionTimer = null;
      this.motionCurrentTime = 0;
      this.activeSourceQueue = [];
      this.activeSourceIndex = 0;
      this.activeLoadToken = 0;
      this.isVideoActive = false;
      this.ccOverlayEnabled = false;
      this.userCcOverride = null;
      this.manifestHydrated = false;
    }

    init(container) {
      this.container = container;
      this.episodes = (typeof window !== 'undefined' && window.AMINA_EPISODES) || [];
      if (!this.episodes.length) {
        console.warn('[AminaPlayer] No episodes data found');
        return;
      }

      // Check last viewed episode preference
      const prefs = window.AminaState ? window.AminaState.getPreferences() : {};
      if (prefs.lastEpisode) {
        const foundIdx = this.episodes.findIndex(e => e.id === prefs.lastEpisode);
        if (foundIdx !== -1) this.currentIndex = foundIdx;
      }
      if (prefs.muted !== undefined) {
        this.isMuted = prefs.muted;
      }

      this._renderBaseLayout();
      this._bindGlobalEvents();
      this._updateSoundIcon();
      this.loadEpisode(this.currentIndex);
      this._hydrateFromManifest();
    }

    _hasPlayableVideo(ep) {
      return Boolean(ep && ((ep.hasRemoteVideo && ep.remoteVideoUrl) || (ep.hasLocalVideo && ep.videoSrc)));
    }

    _getVideoSources(ep) {
      if (!ep) return [];
      const candidates = [];
      if (ep.hasRemoteVideo && ep.remoteVideoUrl) {
        candidates.push(ep.remoteVideoUrl);
      }
      if (ep.hasLocalVideo && ep.videoSrc) {
        candidates.push(ep.videoSrc);
      }
      return [...new Set(candidates)];
    }

    _hydrateFromManifest() {
      if (typeof fetch !== 'function') return;
      fetch('./videos-manifest.json', { cache: 'no-store' })
        .then((response) => {
          if (!response || !response.ok) return null;
          return response.json();
        })
        .then((manifest) => {
          if (!manifest || !manifest.episodes) return;
          this.manifestHydrated = true;

          const curEp = this.episodes[this.currentIndex];
          const prevRemoteUrl = curEp ? curEp.remoteVideoUrl : null;
          let curEpChanged = false;

          this.episodes.forEach((ep) => {
            const entry = Array.isArray(manifest.episodes)
              ? manifest.episodes.find(item => item && item.id === ep.id)
              : manifest.episodes[ep.id];
            if (!entry || typeof entry !== 'object') return;

            const isCurrent = curEp && curEp.id === ep.id;

            if (typeof entry.videoUrl === 'string' && entry.videoUrl.trim()) {
              if (isCurrent && ep.remoteVideoUrl !== entry.videoUrl) curEpChanged = true;
              ep.remoteVideoUrl = entry.videoUrl;
              ep.hasRemoteVideo = true;
            }
            if (typeof entry.downloadUrl === 'string' && entry.downloadUrl.trim()) {
              if (isCurrent && ep.downloadUrl !== entry.downloadUrl) curEpChanged = true;
              ep.downloadUrl = entry.downloadUrl;
            }
            if (typeof entry.posterUrl === 'string' && entry.posterUrl.trim()) {
              if (isCurrent && ep.poster !== entry.posterUrl) curEpChanged = true;
              ep.poster = entry.posterUrl;
            }
            if (typeof entry.duration === 'number' && entry.duration > 0) {
              ep.duration = entry.duration;
              ep.estimatedDuration = Math.round(entry.duration);
              if (isCurrent) curEpChanged = true;
            }
            if (typeof entry.hasBurnedSubtitles === 'boolean') {
              if (isCurrent && ep.hasBurnedSubtitles !== entry.hasBurnedSubtitles) curEpChanged = true;
              ep.hasBurnedSubtitles = entry.hasBurnedSubtitles;
            }
          });

          if (curEp && curEpChanged) {
            const isUnlocked = window.AminaState ? window.AminaState.isEpisodeUnlocked(curEp.id) : curEp.isFree;
            const urlChanged = curEp.remoteVideoUrl !== prevRemoteUrl;
            if (urlChanged || (isUnlocked && !this.isVideoActive && this._hasPlayableVideo(curEp))) {
              this.loadEpisode(this.currentIndex);
            } else {
              this._updateDownloadAction(curEp, isUnlocked);
              if (this.videoEl && curEp.poster) {
                this.videoEl.poster = curEp.poster;
              }
              if (this.userCcOverride === null) {
                this.ccOverlayEnabled = !curEp.hasBurnedSubtitles;
                this._updateCcButton();
              }
            }
          }
        })
        .catch(() => {
          // Optional manifest — fail silently and keep episodes-data.js Release URLs
        });
    }

    _renderBaseLayout() {
      this.container.innerHTML = `
        <div class="player-screen" id="player-screen">
          <div class="player-viewport" id="player-viewport">
            <div class="player-slide" id="player-slide">
              <video class="player-video" id="main-player-video" playsinline webkit-playsinline preload="metadata" poster="assets/cover.jpg" loop muted></video>
              <div class="player-buffering" id="player-buffering" aria-live="polite" style="display: none;">
                <div class="player-spinner"></div>
                <span>Chargement HD...</span>
              </div>
              <div class="motion-card" id="motion-fallback-card" style="display: none;">
                <div class="motion-card-particles"></div>
                <div class="motion-card-content">
                  <div class="motion-badge-row">
                    <span class="badge badge-gold" id="motion-badge">Épisode 01/11</span>
                    <span class="badge badge-locked" id="motion-status-badge">Verrouillé</span>
                  </div>
                  <h2 class="motion-title" id="motion-title">Titre</h2>
                  <div class="motion-hook" id="motion-hook">"Hook"</div>
                  <div class="motion-psalm" id="motion-psalm">
                    <strong>BOUCLIER DE PRIÈRE — PSAUME 91</strong>
                    <span id="motion-psalm-text"></span>
                  </div>
                </div>
                <div class="motion-lock-box" id="motion-lock-box">
                  <div class="motion-lock-icon">
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                      <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                    </svg>
                  </div>
                  <h4 id="lock-box-title">Débloquez cet épisode</h4>
                  <p id="lock-box-desc">Partagez sur WhatsApp ou activez le Pass Saison Mobile Money.</p>
                  <button class="btn btn-gold" id="btn-motion-unlock">
                    <span>🔓 Débloquer l'Épisode</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Central Play/Pause Animation -->
            <div class="play-pause-overlay" id="play-pause-indicator">
              <svg id="indicator-icon" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>

            <!-- Top HUD Bar -->
            <div class="player-top-bar">
              <div class="top-bar-left">
                <span class="badge badge-gold" id="hud-ep-badge">ÉPISODE 01/11</span>
              </div>
              <div class="top-bar-right hud-interactive">
                <button class="icon-btn cc-toggle-btn" id="btn-cc-toggle" aria-label="Activer ou masquer les sous-titres superposés" aria-pressed="false" title="Sous-titres (CC)">
                  <span class="cc-badge-text">CC</span>
                </button>
                <button class="icon-btn" id="btn-sound-toggle" aria-label="Couper ou activer le son">
                  <svg id="sound-icon-svg" viewBox="0 0 24 24">
                    <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                  </svg>
                </button>
                <button class="icon-btn" id="btn-jump-reader-top" aria-label="Lire le chapitre du livre">
                  <svg viewBox="0 0 24 24">
                    <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Right Action Column -->
            <div class="player-actions-col hud-interactive">
              <div class="action-item">
                <button class="action-btn" id="btn-action-like" aria-label="Aimer cet épisode">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                  </svg>
                </button>
                <span class="action-label" id="action-like-count">1.4k</span>
              </div>
              <div class="action-item">
                <button class="action-btn" id="btn-action-share" aria-label="Partager sur WhatsApp">
                  <svg viewBox="0 0 24 24">
                    <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
                  </svg>
                </button>
                <span class="action-label">Partager</span>
              </div>
              <div class="action-item">
                <button class="action-btn" id="btn-action-book" aria-label="Lire le roman">
                  <svg viewBox="0 0 24 24">
                    <path d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.2 20.6 5.3 20 7 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm-1 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z"/>
                  </svg>
                </button>
                <span class="action-label">Roman</span>
              </div>
              <div class="action-item" id="action-download-item" style="display: none;">
                <a class="action-btn action-btn-download" id="btn-action-download" target="_blank" rel="noopener noreferrer" download aria-label="Télécharger l'épisode en HD (.mp4)">
                  <svg viewBox="0 0 24 24">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                  </svg>
                </a>
                <span class="action-label">HD .mp4</span>
              </div>
              <div class="action-item" id="action-lock-indicator-item" style="display: none;">
                <button class="action-btn" id="btn-action-lock" aria-label="Statut du Pass">
                  <svg viewBox="0 0 24 24">
                    <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                  </svg>
                </button>
                <span class="action-label" id="action-lock-label">Verrou</span>
              </div>
            </div>

            <!-- Safe-Zone Subtitles (Centered at y ≈ 75%) -->
            <div class="player-subtitles-container" id="player-subtitles-wrap">
              <div class="subtitle-cue" id="player-subtitle-cue" style="display: none;"></div>
            </div>

            <!-- Bottom Area / Scrubber / Metadata -->
            <div class="player-bottom-area hud-interactive">
              <div class="player-info">
                <div class="player-ep-title" id="hud-ep-title">L'Ombre du Maquis</div>
                <div class="player-hook-preview" id="hud-ep-hook">Hook dramatique de l'épisode...</div>
              </div>
              <div class="scrubber-container">
                <span class="time-display" id="time-current">00:00</span>
                <div class="scrubber-track" id="scrubber-track">
                  <div class="scrubber-fill" id="scrubber-fill">
                    <div class="scrubber-thumb"></div>
                  </div>
                </div>
                <span class="time-display" id="time-duration">01:15</span>
              </div>
            </div>

            <!-- Vertical Swipe Dots Indicator -->
            <div class="swipe-hint" id="swipe-dots-container"></div>
          </div>
        </div>
      `;

      this.videoEl = document.getElementById('main-player-video');
      this._renderSwipeDots();
    }

    _renderSwipeDots() {
      const container = document.getElementById('swipe-dots-container');
      if (!container) return;
      container.innerHTML = this.episodes.map((ep, idx) => `
        <div class="swipe-dot ${idx === this.currentIndex ? 'active' : ''}" data-index="${idx}"></div>
      `).join('');
    }

    _bindGlobalEvents() {
      const viewport = document.getElementById('player-viewport');
      if (!viewport) return;

      // 1. Touch gestures (Swipe Up / Down)
      viewport.addEventListener('touchstart', (e) => {
        if (!e.touches || !e.touches[0]) return;
        if (e.target.closest('.hud-interactive')) return;
        this.touchStartY = e.touches[0].clientY;
        this.touchStartX = e.touches[0].clientX;
        this.isSwiping = true;
      }, { passive: true });

      viewport.addEventListener('touchend', (e) => {
        if (!this.isSwiping) return;
        if (!e.changedTouches || !e.changedTouches[0]) { this.isSwiping = false; return; }
        this.isSwiping = false;
        const deltaY = e.changedTouches[0].clientY - this.touchStartY;
        const deltaX = e.changedTouches[0].clientX - this.touchStartX;

        // If predominantly vertical and exceeds threshold
        if (Math.abs(deltaY) > 50 && Math.abs(deltaY) > Math.abs(deltaX)) {
          if (deltaY < 0) {
            this.nextEpisode();
          } else {
            this.prevEpisode();
          }
        } else if (Math.abs(deltaY) < 10 && Math.abs(deltaX) < 10) {
          // Tap on screen -> Play/Pause
          this.togglePlay();
        }
      });

      viewport.addEventListener('touchcancel', () => {
        this.isSwiping = false;
      }, { passive: true });

      // 2. Mouse Wheel Navigation (Debounced)
      viewport.addEventListener('wheel', (e) => {
        if (this.wheelTimeout) return;
        if (Math.abs(e.deltaY) > 30) {
          if (e.deltaY > 0) {
            this.nextEpisode();
          } else {
            this.prevEpisode();
          }
          this.wheelTimeout = setTimeout(() => {
            this.wheelTimeout = null;
          }, 400);
        }
      }, { passive: true });

      // 3. Keyboard navigation
      window.addEventListener('keydown', (e) => {
        const appState = window.AminaState ? window.AminaState.getPreferences() : {};
        if (appState.activeTab !== 'player') return;

        if (e.key === 'ArrowDown') {
          e.preventDefault();
          this.nextEpisode();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          this.prevEpisode();
        } else if (e.key === ' ' || e.code === 'Space') {
          e.preventDefault();
          this.togglePlay();
        } else if (e.key === 'm' || e.key === 'M') {
          this.toggleMute();
        }
      });

      // 4. Video Events (Buffering, Playback, Resilient Error Fallback)
      this.videoEl.addEventListener('loadstart', () => {
        if (this.isVideoActive && this.videoEl.getAttribute('src')) {
          this._setBuffering(true);
        }
      });
      this.videoEl.addEventListener('waiting', () => {
        if (this.isVideoActive && this.videoEl.getAttribute('src')) {
          this._setBuffering(true);
        }
      });
      this.videoEl.addEventListener('canplay', () => this._setBuffering(false));
      this.videoEl.addEventListener('loadeddata', () => this._setBuffering(false));
      this.videoEl.addEventListener('emptied', () => this._setBuffering(false));
      this.videoEl.addEventListener('playing', () => this._setBuffering(false));
      this.videoEl.addEventListener('error', () => this._handleVideoError());

      this.videoEl.addEventListener('timeupdate', () => this._onTimeUpdate());
      this.videoEl.addEventListener('play', () => {
        this.isPlaying = true;
        this._updatePlayPauseIndicator(true);
        if (window.AminaAudio) window.AminaAudio.duck();
      });
      this.videoEl.addEventListener('pause', () => {
        this.isPlaying = false;
        this._updatePlayPauseIndicator(false);
        if (window.AminaAudio) window.AminaAudio.unduck();
      });
      this.videoEl.addEventListener('ended', () => {
        // Continuous feed: auto advance to next episode if unlocked
        if (this.currentIndex < this.episodes.length - 1) {
          const nextEp = this.episodes[this.currentIndex + 1];
          if (window.AminaState && window.AminaState.isEpisodeUnlocked(nextEp.id)) {
            this.nextEpisode();
          }
        }
      });

      // 5. HUD Interactive Buttons
      document.getElementById('btn-cc-toggle')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleCcOverlay();
      });

      document.getElementById('btn-sound-toggle')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleMute();
      });

      document.getElementById('btn-jump-reader-top')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this._jumpToReader();
      });

      document.getElementById('btn-action-like')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this._handleLikeClick();
      });

      document.getElementById('btn-action-share')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this._handleShareClick();
      });

      document.getElementById('btn-action-book')?.addEventListener('click', (e) => {
        e.stopPropagation();
        this._jumpToReader();
      });

      document.getElementById('btn-action-download')?.addEventListener('click', (e) => {
        e.stopPropagation();
      });

      document.getElementById('btn-action-lock')?.addEventListener('click', (e) => {
        e.stopPropagation();
        const ep = this.episodes[this.currentIndex];
        if (window.AminaMonetization) {
          window.AminaMonetization.openUnlockModal(ep.id);
        }
      });

      document.getElementById('btn-motion-unlock')?.addEventListener('click', (e) => {
        e.stopPropagation();
        const ep = this.episodes[this.currentIndex];
        if (window.AminaMonetization) {
          window.AminaMonetization.openUnlockModal(ep.id);
        }
      });

      // 6. Scrubber Interaction
      const scrubber = document.getElementById('scrubber-track');
      if (scrubber) {
        scrubber.addEventListener('click', (e) => {
          e.stopPropagation();
          const rect = scrubber.getBoundingClientRect();
          const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
          this._seekToRatio(ratio);
        });
      }

      // 7. React to state changes (e.g. Unlocked from modal)
      if (window.AminaState) {
        window.AminaState.on('episodeUnlocked', (data) => {
          const curEp = this.episodes[this.currentIndex];
          if (curEp && curEp.id === data.episodeId) {
            this.loadEpisode(this.currentIndex);
          }
        });
        window.AminaState.on('seasonPassUnlocked', () => {
          this.loadEpisode(this.currentIndex);
        });
      }
    }

    _setBuffering(isBuffering) {
      const el = document.getElementById('player-buffering');
      if (!el) return;
      el.style.display = isBuffering ? 'flex' : 'none';
    }

    _clearVideoElement() {
      if (!this.videoEl) return;
      this.videoEl.pause();
      this.videoEl.removeAttribute('src');
      this.videoEl.load();
      this.videoEl.style.display = 'none';
    }

    _updateDownloadAction(ep, isUnlocked) {
      const downloadItem = document.getElementById('action-download-item');
      const downloadLink = document.getElementById('btn-action-download');
      if (!downloadItem || !downloadLink) return;

      if (isUnlocked && ep && ep.downloadUrl) {
        downloadLink.setAttribute('href', ep.downloadUrl);
        downloadLink.setAttribute('download', `${ep.id}.mp4`);
        downloadItem.style.display = 'flex';
      } else {
        downloadLink.removeAttribute('href');
        downloadLink.removeAttribute('download');
        downloadItem.style.display = 'none';
      }
    }

    _updateCcButton() {
      const btn = document.getElementById('btn-cc-toggle');
      if (!btn) return;
      btn.setAttribute('aria-pressed', this.ccOverlayEnabled ? 'true' : 'false');
      btn.classList.toggle('active', this.ccOverlayEnabled);
    }

    toggleCcOverlay() {
      this.ccOverlayEnabled = !this.ccOverlayEnabled;
      this.userCcOverride = this.ccOverlayEnabled;
      this._updateCcButton();

      if (!this.ccOverlayEnabled) {
        this._hideSubtitle();
      } else if (this.isVideoActive) {
        this._onTimeUpdate();
      }
    }

    loadEpisode(index) {
      if (index < 0 || index >= this.episodes.length) return;
      this.currentIndex = index;
      const ep = this.episodes[index];
      const loadToken = ++this.activeLoadToken;

      // Update state
      if (window.AminaState) {
        window.AminaState.setPreference('lastEpisode', ep.id);
      }

      const isUnlocked = window.AminaState ? window.AminaState.isEpisodeUnlocked(ep.id) : ep.isFree;

      // Update HUD elements
      const badgeText = `ÉPISODE ${String(ep.number).padStart(2, '0')}/11`;
      document.getElementById('hud-ep-badge').textContent = badgeText;
      document.getElementById('hud-ep-title').textContent = ep.title;
      document.getElementById('hud-ep-hook').textContent = ep.hook;

      // Update Like button
      const likeBtn = document.getElementById('btn-action-like');
      const isLiked = window.AminaState ? window.AminaState.isLiked(ep.id) : false;
      if (likeBtn) {
        likeBtn.classList.toggle('liked', isLiked);
      }
      const likeCount = document.getElementById('action-like-count');
      if (likeCount) {
        likeCount.textContent = isLiked ? '1.5k' : '1.4k';
      }

      // Update Lock indicator & gated HD download button
      const lockIndicator = document.getElementById('action-lock-indicator-item');
      if (lockIndicator) {
        lockIndicator.style.display = isUnlocked ? 'none' : 'flex';
      }
      this._updateDownloadAction(ep, isUnlocked);

      // Update CC overlay default (prevent double subtitles on burned-in MP4s)
      this.ccOverlayEnabled = this.userCcOverride !== null
        ? this.userCcOverride
        : !ep.hasBurnedSubtitles;
      this._updateCcButton();

      // Update Swipe dots
      this._renderSwipeDots();

      const motionCard = document.getElementById('motion-fallback-card');
      const videoEl = this.videoEl;

      // Always sync motion card metadata & status badge before toggling visibility
      document.getElementById('motion-badge').textContent = badgeText;
      const statusBadgeEl = document.getElementById('motion-status-badge');
      statusBadgeEl.textContent = isUnlocked ? 'Accès Débloqué' : 'Verrouillé';
      statusBadgeEl.className = `badge ${isUnlocked ? 'badge-free' : 'badge-locked'}`;
      document.getElementById('motion-title').textContent = ep.title;
      document.getElementById('motion-hook').textContent = `« ${ep.hook} »`;

      const psalmText = ep.psalmVerse && ep.psalmVerse.text
        ? `"${ep.psalmVerse.text}" (${ep.psalmVerse.ref})`
        : "Sous l'ombre du Tout-Puissant.";
      document.getElementById('motion-psalm-text').textContent = psalmText;

      // Reset subtitles & scrubber
      this._hideSubtitle();
      this._updateScrubber(0, ep.duration || ep.estimatedDuration || 75);

      if (this.motionTimer) {
        clearInterval(this.motionTimer);
        this.motionTimer = null;
      }

      if (isUnlocked && this._hasPlayableVideo(ep)) {
        // Episode is unlocked and has remote/local playable MP4 video
        this.activeSourceQueue = this._getVideoSources(ep);
        this.activeSourceIndex = 0;
        this.isVideoActive = true;

        motionCard.style.display = 'none';
        videoEl.style.display = 'block';
        videoEl.poster = ep.poster || ep.contactSheet || 'assets/cover.jpg';

        this._loadActiveSource(loadToken);
      } else {
        // Episode is locked OR has no playable video source
        this.isVideoActive = false;
        this.activeSourceQueue = [];
        this.activeSourceIndex = 0;
        this._setBuffering(false);
        this._clearVideoElement();
        this._showMotionFallbackCard(ep, isUnlocked, { isOfflineFallback: false });
      }
    }

    _loadActiveSource(loadToken) {
      if (loadToken !== this.activeLoadToken || !this.videoEl) return;
      const src = this.activeSourceQueue[this.activeSourceIndex];
      if (!src) {
        const ep = this.episodes[this.currentIndex];
        this.isVideoActive = false;
        this._setBuffering(false);
        this._clearVideoElement();
        if (ep) this._showMotionFallbackCard(ep, true, { isOfflineFallback: true });
        return;
      }

      this._setBuffering(true);
      this.videoEl.src = src;
      this.videoEl.muted = this.isMuted;
      this.videoEl.load();

      const playPromise = this.videoEl.play();
      if (playPromise !== undefined) {
        playPromise.then(() => {
          if (loadToken === this.activeLoadToken) {
            this.isPlaying = true;
          }
        }).catch((err) => {
          if (loadToken === this.activeLoadToken) {
            console.log('[AminaPlayer] Autoplay prevented, waiting for user gesture:', err);
            this.isPlaying = false;
            this._setBuffering(false);
          }
        });
      }
    }

    _handleVideoError() {
      // Ignore error events when video is inactive or intentionally cleared
      if (!this.isVideoActive || !this.videoEl || !this.videoEl.getAttribute('src')) {
        return;
      }

      const token = this.activeLoadToken;
      if (this.activeSourceIndex + 1 < this.activeSourceQueue.length) {
        this.activeSourceIndex += 1;
        this._loadActiveSource(token);
        return;
      }

      // All sources exhausted — degrade gracefully to unlocked offline fallback card
      const ep = this.episodes[this.currentIndex];
      this.isVideoActive = false;
      this._setBuffering(false);
      this._clearVideoElement();
      if (ep) {
        this._showMotionFallbackCard(ep, true, { isOfflineFallback: true });
      }
    }

    _showMotionFallbackCard(ep, isUnlocked, options = {}) {
      const motionCard = document.getElementById('motion-fallback-card');
      if (!motionCard) return;
      motionCard.style.display = 'flex';

      const statusBadgeEl = document.getElementById('motion-status-badge');
      if (statusBadgeEl) {
        statusBadgeEl.textContent = isUnlocked ? 'Accès Débloqué' : 'Verrouillé';
        statusBadgeEl.className = `badge ${isUnlocked ? 'badge-free' : 'badge-locked'}`;
      }

      const lockBox = document.getElementById('motion-lock-box');
      if (!lockBox) return;

      if (isUnlocked && options.isOfflineFallback) {
        lockBox.innerHTML = `
          <div class="motion-lock-icon" style="color: #10B981; border-color: #10B981; background: rgba(16,185,129,0.15)">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h4>Accès Débloqué</h4>
          <p>Vidéo HD momentanément indisponible (hors-ligne ou chargement).</p>
          <div class="motion-lock-actions">
            <button class="btn btn-gold" id="btn-motion-retry">
              <span>🔄 Réessayer la vidéo</span>
            </button>
            <button class="btn btn-outline-gold" id="btn-motion-read-chap">
              <span>📖 Lire le Chapitre ${ep.chapterNumber}</span>
            </button>
          </div>
        `;
        document.getElementById('btn-motion-retry')?.addEventListener('click', (e) => {
          e.stopPropagation();
          this.loadEpisode(this.currentIndex);
        });
        document.getElementById('btn-motion-read-chap')?.addEventListener('click', (e) => {
          e.stopPropagation();
          this._jumpToReader();
        });
      } else if (isUnlocked) {
        lockBox.innerHTML = `
          <div class="motion-lock-icon" style="color: #10B981; border-color: #10B981; background: rgba(16,185,129,0.15)">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h4>Épisode Débloqué !</h4>
          <p>Le master vidéo de cet épisode est en cours de post-production. Vous pouvez dès maintenant lire le chapitre complet du roman.</p>
          <button class="btn btn-gold" id="btn-motion-read-chap">
            <span>📖 Lire le Chapitre ${ep.chapterNumber}</span>
          </button>
        `;
        document.getElementById('btn-motion-read-chap')?.addEventListener('click', (e) => {
          e.stopPropagation();
          this._jumpToReader();
        });
      } else {
        lockBox.innerHTML = `
          <div class="motion-lock-icon">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
          </div>
          <h4>Épisode Verrouillé</h4>
          <p>Partagez sur WhatsApp avec vos proches ou activez le Pass Saison Mobile Money.</p>
          <button class="btn btn-gold" id="btn-motion-unlock">
            <span>🔓 Débloquer l'Épisode</span>
          </button>
        `;
        document.getElementById('btn-motion-unlock')?.addEventListener('click', (e) => {
          e.stopPropagation();
          if (window.AminaMonetization) {
            window.AminaMonetization.openUnlockModal(ep.id);
          }
        });
      }

      // Start simulated timer to cycle subtitles cues for the dramatic preview
      this._startMotionSubtitlesSimulation(ep);
    }

    _startMotionSubtitlesSimulation(ep) {
      if (this.motionTimer) {
        clearInterval(this.motionTimer);
        this.motionTimer = null;
      }
      if (!ep.subtitles || !ep.subtitles.length) return;
      this.motionCurrentTime = 0;
      const duration = ep.duration || ep.estimatedDuration || 75;

      this.motionTimer = setInterval(() => {
        this.motionCurrentTime = (this.motionCurrentTime + 1) % duration;
        this._updateScrubber(this.motionCurrentTime, duration);

        // Check subtitles match
        const cue = ep.subtitles.find(c => this.motionCurrentTime >= c.startSeconds && this.motionCurrentTime <= c.endSeconds);
        if (cue) {
          this._showSubtitle(cue.text);
        } else {
          this._hideSubtitle();
        }
      }, 1000);
    }

    _onTimeUpdate() {
      if (!this.videoEl || !this.isVideoActive) return;
      const cur = this.videoEl.currentTime;
      const ep = this.episodes[this.currentIndex];
      const dur = this.videoEl.duration || (ep && (ep.duration || ep.estimatedDuration)) || 75;
      this._updateScrubber(cur, dur);

      if (!ep || !ep.subtitles) return;

      const shouldShowOverlay = this.userCcOverride !== null
        ? this.ccOverlayEnabled
        : (!ep.hasBurnedSubtitles || this.ccOverlayEnabled);

      if (!shouldShowOverlay) {
        this._hideSubtitle();
        return;
      }

      const cue = ep.subtitles.find(c => cur >= c.startSeconds && cur <= c.endSeconds);
      if (cue) {
        this._showSubtitle(cue.text);
      } else {
        this._hideSubtitle();
      }
    }

    _showSubtitle(text) {
      const el = document.getElementById('player-subtitle-cue');
      if (!el) return;
      el.textContent = text;
      el.style.display = 'inline-block';
    }

    _hideSubtitle() {
      const el = document.getElementById('player-subtitle-cue');
      if (!el) return;
      el.style.display = 'none';
      el.textContent = '';
    }

    _updateScrubber(current, duration) {
      const fill = document.getElementById('scrubber-fill');
      const timeCur = document.getElementById('time-current');
      const timeDur = document.getElementById('time-duration');

      const ratio = duration > 0 ? (current / duration) * 100 : 0;
      if (fill) fill.style.width = `${Math.min(100, Math.max(0, ratio))}%`;

      if (timeCur) timeCur.textContent = this._formatTime(current);
      if (timeDur) timeDur.textContent = this._formatTime(duration);
    }

    _formatTime(secs) {
      const s = Math.floor(secs || 0);
      const m = Math.floor(s / 60);
      const rem = s % 60;
      return `${String(m).padStart(2, '0')}:${String(rem).padStart(2, '0')}`;
    }

    _seekToRatio(ratio) {
      const ep = this.episodes[this.currentIndex];
      const isUnlocked = window.AminaState ? window.AminaState.isEpisodeUnlocked(ep.id) : ep.isFree;

      if (isUnlocked && this.isVideoActive && this._hasPlayableVideo(ep) && this.videoEl) {
        const target = (this.videoEl.duration || ep.duration || ep.estimatedDuration || 75) * ratio;
        this.videoEl.currentTime = target;
      } else {
        this.motionCurrentTime = (ep.duration || ep.estimatedDuration || 75) * ratio;
        this._updateScrubber(this.motionCurrentTime, ep.duration || ep.estimatedDuration || 75);
      }
    }

    togglePlay() {
      const ep = this.episodes[this.currentIndex];
      const isUnlocked = window.AminaState ? window.AminaState.isEpisodeUnlocked(ep.id) : ep.isFree;

      if (isUnlocked && this.isVideoActive && this._hasPlayableVideo(ep) && this.videoEl) {
        if (this.videoEl.paused) {
          const p = this.videoEl.play();
          if (p && typeof p.catch === 'function') p.catch(() => {});
        } else {
          this.videoEl.pause();
        }
      } else {
        // Toggle simulated motion timer
        if (this.motionTimer) {
          clearInterval(this.motionTimer);
          this.motionTimer = null;
          this._updatePlayPauseIndicator(false);
        } else {
          this._startMotionSubtitlesSimulation(ep);
          this._updatePlayPauseIndicator(true);
        }
      }
    }

    _updatePlayPauseIndicator(isPlaying) {
      const indicator = document.getElementById('play-pause-indicator');
      const icon = document.getElementById('indicator-icon');
      if (!indicator || !icon) return;

      if (isPlaying) {
        icon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
      } else {
        icon.innerHTML = '<path d="M8 5v14l11-7z"/>';
      }
      indicator.classList.remove('animate');
      void indicator.offsetWidth; // Trigger reflow
      indicator.classList.add('animate');
      setTimeout(() => indicator.classList.remove('animate'), 450);
    }

    toggleMute() {
      this.isMuted = !this.isMuted;
      if (this.videoEl) {
        this.videoEl.muted = this.isMuted;
      }
      if (window.AminaState) {
        window.AminaState.setPreference('muted', this.isMuted);
      }
      this._updateSoundIcon();
    }

    _updateSoundIcon() {
      const btn = document.getElementById('btn-sound-toggle');
      const svg = document.getElementById('sound-icon-svg');
      if (!btn || !svg) return;

      btn.classList.toggle('active', !this.isMuted);
      if (this.isMuted) {
        svg.innerHTML = '<path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>';
      } else {
        svg.innerHTML = '<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>';
      }
    }

    nextEpisode() {
      if (this.currentIndex < this.episodes.length - 1) {
        this.loadEpisode(this.currentIndex + 1);
      } else {
        // Loop back to episode 1
        this.loadEpisode(0);
      }
    }

    prevEpisode() {
      if (this.currentIndex > 0) {
        this.loadEpisode(this.currentIndex - 1);
      } else {
        this.loadEpisode(this.episodes.length - 1);
      }
    }

    goToEpisode(indexOrId) {
      let idx = -1;
      if (typeof indexOrId === 'number') {
        idx = indexOrId;
      } else if (typeof indexOrId === 'string') {
        idx = this.episodes.findIndex(e => e.id === indexOrId);
      }
      if (idx >= 0 && idx < this.episodes.length) {
        this.loadEpisode(idx);
      }
    }

    getCurrentEpisode() {
      return this.episodes[this.currentIndex];
    }

    _handleLikeClick() {
      const ep = this.episodes[this.currentIndex];
      if (!ep) return;
      if (window.AminaState) {
        const liked = window.AminaState.toggleLike(ep.id);
        const likeBtn = document.getElementById('btn-action-like');
        const count = document.getElementById('action-like-count');
        if (likeBtn) likeBtn.classList.toggle('liked', liked);
        if (count) count.textContent = liked ? '1.5k' : '1.4k';
      }
    }

    _handleShareClick() {
      const ep = this.episodes[this.currentIndex];
      if (!ep) return;
      if (window.AminaMonetization) {
        window.AminaMonetization.openUnlockModal(ep.id);
      }
    }

    _jumpToReader() {
      const ep = this.episodes[this.currentIndex];
      if (window.AminaApp) {
        window.AminaApp.switchTab('reader');
      }
      if (window.AminaReader && ep) {
        window.AminaReader.openChapter(ep.chapterNumber);
      }
    }

    destroy() {
      this.activeLoadToken += 1;
      this.isVideoActive = false;
      this._setBuffering(false);
      this._clearVideoElement();
      if (this.motionTimer) {
        clearInterval(this.motionTimer);
      }
    }
  }

  const playerInstance = new PlayerEngine();

  if (typeof window !== 'undefined') {
    window.AminaPlayer = playerInstance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaPlayer = playerInstance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaPlayer: playerInstance, PlayerEngine };
  }
})(typeof window !== 'undefined' ? window : globalThis);
