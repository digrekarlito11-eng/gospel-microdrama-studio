/**
 * AMINA Experience — Application Entry Point & Tab Router
 * Coordinates PWA Shell, tabs, service worker registration, and audio state.
 */

(function (global) {
  'use strict';

  class AppEngine {
    constructor() {
      this.activeTab = 'player';
    }

    init() {
      // 1. Initialize State & Data
      const prefs = window.AminaState ? window.AminaState.getPreferences() : {};
      if (prefs.activeTab) this.activeTab = prefs.activeTab;

      // 2. Initialize Audio Engine
      if (window.AminaAudio) {
        window.AminaAudio.init();
      }

      // 3. Initialize Monetization Engine
      if (window.AminaMonetization) {
        window.AminaMonetization.init();
      }

      // 4. Initialize Player Engine
      const playerContainer = document.getElementById('screen-player');
      if (playerContainer && window.AminaPlayer) {
        window.AminaPlayer.init(playerContainer);
      }

      // 5. Initialize Reader Engine
      const readerContainer = document.getElementById('screen-reader');
      if (readerContainer && window.AminaReader) {
        window.AminaReader.init(readerContainer);
      }

      // 6. Bind Bottom Navigation & Ambient Audio Bar
      this._bindNavigation();
      this._bindAudioToggle();

      // 7. Initial Tab Activation
      this.switchTab(this.activeTab);

      // 8. Register Service Worker for Offline PWA
      this._registerServiceWorker();

      console.log('[AMINA Experience] PWA Initialized successfully');
    }

    _bindNavigation() {
      document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const targetTab = btn.getAttribute('data-tab');
          if (targetTab) this.switchTab(targetTab);
        });
      });

      // Store tab buttons
      document.getElementById('btn-store-season-pass')?.addEventListener('click', () => {
        if (window.AminaMonetization) {
          window.AminaMonetization.openUnlockModal('ep-004');
        }
      });

      document.getElementById('btn-store-book-order')?.addEventListener('click', () => {
        if (window.AminaMonetization) {
          window.AminaMonetization.openOrderModal();
        }
      });
    }

    _bindAudioToggle() {
      const audioBar = document.getElementById('ambient-audio-bar');
      if (audioBar) {
        audioBar.addEventListener('click', () => {
          if (window.AminaAudio) {
            window.AminaAudio.toggle();
          }
        });
      }
    }

    switchTab(tabName) {
      const validTabs = ['player', 'reader', 'store'];
      if (!validTabs.includes(tabName)) return;

      this.activeTab = tabName;

      // Update Nav active classes
      document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
      });

      // Update Screen views
      document.querySelectorAll('.screen-view').forEach(view => {
        const isCurrent = view.id === `screen-${tabName}`;
        view.classList.toggle('active', isCurrent);
      });

      // Save preference
      if (window.AminaState) {
        window.AminaState.setPreference('activeTab', tabName);
      }

      // Tab specific actions
      if (tabName === 'player') {
        // Leaving reading -> resuming video check
        const curEp = window.AminaPlayer ? window.AminaPlayer.getCurrentEpisode() : null;
        if (curEp && curEp.hasLocalVideo && window.AminaState && window.AminaState.isEpisodeUnlocked(curEp.id)) {
          // Video will manage its ducking on play
        }
      } else {
        // Pausing player video when reading or shopping to conserve resources
        if (window.AminaPlayer && window.AminaPlayer.videoEl) {
          window.AminaPlayer.videoEl.pause();
        }
        if (window.AminaAudio) {
          window.AminaAudio.unduck();
        }
      }
    }

    _registerServiceWorker() {
      if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('[ServiceWorker] Registered with scope:', reg.scope))
            .catch(err => console.log('[ServiceWorker] Registration failed:', err));
        });
      }
    }
  }

  const appInstance = new AppEngine();

  // Self-boot on DOMContentLoaded
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
      appInstance.init();
    });
  }

  if (typeof window !== 'undefined') {
    window.AminaApp = appInstance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaApp = appInstance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaApp: appInstance, AppEngine };
  }
})(typeof window !== 'undefined' ? window : globalThis);
