/**
 * AMINA Experience — State Management & Reactive Store
 * Interface contract as specified in PROJECT.md
 * Persists to localStorage under 'amina_state_v1'
 */

(function (global) {
  'use strict';

  const STORAGE_KEY = 'amina_state_v1';

  // Default Initial State
  const DEFAULT_STATE = {
    unlocked_episodes: ['ep-001', 'ep-002', 'ep-003'],
    has_season_pass: false,
    whatsapp_shares: {
      count: 0,
      episodes: []
    },
    preferences: {
      theme: 'night',         // 'night' | 'sepia' | 'light'
      fontSize: 17,           // 15px - 24px
      volume: 0.7,
      muted: true,            // Mobile browsers require muted by default
      bgmEnabled: true,
      activeTab: 'player',    // 'player' | 'reader' | 'store'
      lastEpisode: 'ep-001',
      lastChapter: 1
    },
    likes: {
      'ep-001': false
    },
    reading_progress: {}      // { 'chapitre-01': 0.45 }
  };

  class StateStore {
    constructor() {
      this.listeners = new Map();
      this.state = this._loadState();
    }

    _loadState() {
      try {
        if (typeof localStorage !== 'undefined') {
          const raw = localStorage.getItem(STORAGE_KEY);
          if (raw) {
            const parsed = JSON.parse(raw);
            // Merge defaults to preserve schema upgrades
            const merged = {
              ...DEFAULT_STATE,
              ...parsed,
              preferences: {
                ...DEFAULT_STATE.preferences,
                ...(parsed.preferences || {})
              },
              whatsapp_shares: {
                ...DEFAULT_STATE.whatsapp_shares,
                ...(parsed.whatsapp_shares || {})
              },
              likes: {
                ...DEFAULT_STATE.likes,
                ...(parsed.likes || {})
              },
              reading_progress: {
                ...DEFAULT_STATE.reading_progress,
                ...(parsed.reading_progress || {})
              }
            };
            if (!Array.isArray(merged.whatsapp_shares?.episodes)) {
              merged.whatsapp_shares.episodes = [];
            }
            // Guarantee ep-001, ep-002, ep-003 are always included
            const unlockedSet = new Set(merged.unlocked_episodes || []);
            unlockedSet.add('ep-001');
            unlockedSet.add('ep-002');
            unlockedSet.add('ep-003');
            merged.unlocked_episodes = Array.from(unlockedSet);
            return merged;
          }
        }
      } catch (err) {
        console.warn('[AminaState] LocalStorage load failed, using defaults', err);
      }
      return JSON.parse(JSON.stringify(DEFAULT_STATE));
    }

    _saveState() {
      try {
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
        }
      } catch (err) {
        console.warn('[AminaState] LocalStorage save failed', err);
      }
    }

    /**
     * Returns a snapshot copy of the current state
     */
    get() {
      return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * Checks if an episode is unlocked
     * @param {string} episodeId - e.g. 'ep-001', 'ep-004'
     * @returns {boolean}
     */
    isEpisodeUnlocked(episodeId) {
      if (!episodeId) return false;
      const id = String(episodeId).toLowerCase().trim();
      // Free lead magnet: ep-001, ep-002, ep-003 always free!
      if (id === 'ep-001' || id === 'ep-002' || id === 'ep-003') {
        return true;
      }
      if (this.state.has_season_pass === true) {
        return true;
      }
      return Array.isArray(this.state.unlocked_episodes) && this.state.unlocked_episodes.includes(id);
    }

    /**
     * Unlocks a specific episode (via WhatsApp share or purchase)
     * @param {string} episodeId
     */
    unlockEpisode(episodeId) {
      if (!episodeId || typeof episodeId !== 'string') return;
      const id = episodeId.toLowerCase().trim();
      if (!id) return;
      if (!this.state.unlocked_episodes.includes(id)) {
        this.state.unlocked_episodes.push(id);
        this._saveState();
        this.emit('episodeUnlocked', { episodeId: id, state: this.get() });
        this.emit('stateChange', this.get());
      }
    }

    /**
     * Unlocks the full season pass (Mobile Money checkout or promo)
     */
    unlockSeasonPass() {
      this.state.has_season_pass = true;
      // Also unlock all 11 episodes in the array
      for (let i = 1; i <= 11; i++) {
        const id = `ep-${String(i).padStart(3, '0')}`;
        if (!this.state.unlocked_episodes.includes(id)) {
          this.state.unlocked_episodes.push(id);
        }
      }
      this._saveState();
      this.emit('seasonPassUnlocked', this.get());
      this.emit('stateChange', this.get());
    }

    /**
     * Returns preferences object
     */
    getPreferences() {
      return { ...this.state.preferences };
    }

    /**
     * Sets a single preference or object of preferences
     * @param {string|object} keyOrObj
     * @param {any} value
     */
    setPreference(keyOrObj, value) {
      let changed = false;
      if (typeof keyOrObj === 'object' && keyOrObj !== null) {
        for (const [k, v] of Object.entries(keyOrObj)) {
          if (this.state.preferences[k] !== v) {
            this.state.preferences[k] = v;
            changed = true;
          }
        }
      } else if (typeof keyOrObj === 'string') {
        if (this.state.preferences[keyOrObj] !== value) {
          this.state.preferences[keyOrObj] = value;
          changed = true;
        }
      }

      if (changed) {
        this._saveState();
        if (typeof keyOrObj === 'string' && keyOrObj === 'theme') {
          this.emit('themeChanged', { theme: value });
        }
        this.emit('preferenceChanged', { preferences: this.getPreferences() });
        this.emit('stateChange', this.get());
      }
    }

    /**
     * Toggle like state for an episode
     * @param {string} episodeId
     * @returns {boolean} new like status
     */
    toggleLike(episodeId) {
      if (!episodeId) return false;
      const current = !!this.state.likes[episodeId];
      this.state.likes[episodeId] = !current;
      this._saveState();
      this.emit('likeToggled', { episodeId, liked: !current });
      this.emit('stateChange', this.get());
      return !current;
    }

    isLiked(episodeId) {
      return !!this.state.likes[episodeId];
    }

    /**
     * Records a WhatsApp share for virality tracking
     * @param {string} episodeId
     */
    recordWhatsAppShare(episodeId) {
      this.state.whatsapp_shares.count = (this.state.whatsapp_shares.count || 0) + 1;
      if (episodeId && !this.state.whatsapp_shares.episodes.includes(episodeId)) {
        this.state.whatsapp_shares.episodes.push(episodeId);
      }
      this._saveState();
      this.emit('whatsappShared', { count: this.state.whatsapp_shares.count, episodeId });
      this.emit('stateChange', this.get());
    }

    /**
     * Updates reading progress for a chapter
     */
    setReadingProgress(chapterId, percentage) {
      this.state.reading_progress[chapterId] = Math.min(1, Math.max(0, percentage));
      this._saveState();
    }

    getReadingProgress(chapterId) {
      return this.state.reading_progress[chapterId] || 0;
    }

    /**
     * Event subscription (Pub/Sub)
     * @param {string} eventName
     * @param {Function} callback
     * @returns {Function} unsubscribe function
     */
    on(eventName, callback) {
      if (typeof callback !== 'function') return () => {};
      if (!this.listeners.has(eventName)) {
        this.listeners.set(eventName, new Set());
      }
      this.listeners.get(eventName).add(callback);
      return () => {
        const set = this.listeners.get(eventName);
        if (set) set.delete(callback);
      };
    }

    /**
     * Emit event to listeners
     */
    emit(eventName, data) {
      const set = this.listeners.get(eventName);
      if (set) {
        set.forEach(cb => {
          try {
            cb(data);
          } catch (e) {
            console.error(`[AminaState] Error in listener for ${eventName}:`, e);
          }
        });
      }
    }

    /**
     * Resets state to default (useful for testing and debug)
     */
    resetState() {
      this.state = JSON.parse(JSON.stringify(DEFAULT_STATE));
      this._saveState();
      this.emit('stateReset', this.get());
      this.emit('stateChange', this.get());
    }
  }

  const instance = new StateStore();

  if (typeof window !== 'undefined') {
    window.AminaState = instance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaState = instance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaState: instance, StateStore, DEFAULT_STATE };
  }
})(typeof window !== 'undefined' ? window : globalThis);
