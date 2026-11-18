const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert/strict');

// Mock localStorage for Node.js test environment
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

globalThis.localStorage = new MockLocalStorage();

// Import StateStore and default state from state.js
const { AminaState, StateStore, DEFAULT_STATE } = require('../../js/state.js');

describe('AminaState Store & Freemium Rules (Unit Tests)', () => {
  let store;

  beforeEach(() => {
    globalThis.localStorage.clear();
    store = new StateStore();
  });

  describe('Tier 1: Initial State & Free Lead Magnet', () => {
    it('should initialize with default state schema', () => {
      const state = store.get();
      assert.ok(Array.isArray(state.unlocked_episodes), 'unlocked_episodes should be an array');
      assert.equal(state.has_season_pass, false, 'has_season_pass should be false by default');
      assert.deepEqual(state.unlocked_episodes, ['ep-001', 'ep-002', 'ep-003']);
      assert.equal(state.preferences.theme, 'night');
      assert.equal(state.preferences.fontSize, 17);
      assert.equal(state.preferences.volume, 0.7);
    });

    it('should grant free access to episodes 1, 2, and 3 unconditionally', () => {
      assert.equal(store.isEpisodeUnlocked('ep-001'), true);
      assert.equal(store.isEpisodeUnlocked('ep-002'), true);
      assert.equal(store.isEpisodeUnlocked('ep-003'), true);
      assert.equal(store.isEpisodeUnlocked('EP-001'), true, 'Should be case-insensitive');
    });

    it('should lock episodes 4 through 11 by default', () => {
      for (let i = 4; i <= 11; i++) {
        const epId = `ep-${String(i).padStart(3, '0')}`;
        assert.equal(
          store.isEpisodeUnlocked(epId),
          false,
          `Episode ${epId} should be locked by default`
        );
      }
    });

    it('should return false for invalid or empty episode IDs', () => {
      assert.equal(store.isEpisodeUnlocked(''), false);
      assert.equal(store.isEpisodeUnlocked(null), false);
      assert.equal(store.isEpisodeUnlocked(undefined), false);
      assert.equal(store.isEpisodeUnlocked('ep-999'), false);
    });
  });

  describe('Tier 2: Single Episode Unlock via WhatsApp Share', () => {
    it('should unlock episode 4 upon calling unlockEpisode', () => {
      assert.equal(store.isEpisodeUnlocked('ep-004'), false);
      store.unlockEpisode('ep-004');
      assert.equal(store.isEpisodeUnlocked('ep-004'), true);
      assert.equal(store.isEpisodeUnlocked('ep-005'), false, 'ep-005 should still be locked');
    });

    it('should record WhatsApp shares and increment share count', () => {
      const initialCount = store.get().whatsapp_shares.count;
      store.recordWhatsAppShare('ep-004');
      assert.equal(store.get().whatsapp_shares.count, initialCount + 1);
      assert.ok(store.get().whatsapp_shares.episodes.includes('ep-004'));

      store.recordWhatsAppShare('ep-004');
      assert.equal(store.get().whatsapp_shares.count, initialCount + 2);
    });

    it('should emit events on episode unlock', () => {
      let eventPayload = null;
      const unsubscribe = store.on('episodeUnlocked', (data) => {
        eventPayload = data;
      });

      store.unlockEpisode('ep-006');
      assert.ok(eventPayload);
      assert.equal(eventPayload.episodeId, 'ep-006');
      unsubscribe();
    });

    it('should handle duplicate unlock calls idempotently without duplicating array entries', () => {
      store.unlockEpisode('ep-004');
      const countAfterFirst = store.get().unlocked_episodes.filter(id => id === 'ep-004').length;
      assert.equal(countAfterFirst, 1);

      store.unlockEpisode('ep-004');
      const countAfterSecond = store.get().unlocked_episodes.filter(id => id === 'ep-004').length;
      assert.equal(countAfterSecond, 1);
    });
  });

  describe('Tier 3: Full Season Pass via Mobile Money', () => {
    it('should unlock all 11 episodes when unlockSeasonPass is called', () => {
      assert.equal(store.get().has_season_pass, false);
      store.unlockSeasonPass();

      assert.equal(store.get().has_season_pass, true);
      for (let i = 1; i <= 11; i++) {
        const epId = `ep-${String(i).padStart(3, '0')}`;
        assert.equal(
          store.isEpisodeUnlocked(epId),
          true,
          `Episode ${epId} must be unlocked after Season Pass activation`
        );
      }
    });

    it('should emit seasonPassUnlocked and stateChange events', () => {
      let seasonPassEventFired = false;
      let stateChangeEventFired = false;

      store.on('seasonPassUnlocked', () => {
        seasonPassEventFired = true;
      });
      store.on('stateChange', () => {
        stateChangeEventFired = true;
      });

      store.unlockSeasonPass();
      assert.equal(seasonPassEventFired, true);
      assert.equal(stateChangeEventFired, true);
    });
  });

  describe('Tier 4: Preferences, LocalStorage Persistence & Resilience', () => {
    it('should update and persist preferences (theme, fontSize, volume)', () => {
      store.setPreference('theme', 'sepia');
      store.setPreference('fontSize', 22);
      store.setPreference('volume', 0.9);

      const prefs = store.getPreferences();
      assert.equal(prefs.theme, 'sepia');
      assert.equal(prefs.fontSize, 22);
      assert.equal(prefs.volume, 0.9);

      // Verify persistence in localStorage
      const rawStored = globalThis.localStorage.getItem('amina_state_v1');
      assert.ok(rawStored, 'localStorage should have amina_state_v1');
      const parsed = JSON.parse(rawStored);
      assert.equal(parsed.preferences.theme, 'sepia');
      assert.equal(parsed.preferences.fontSize, 22);
    });

    it('should restore persisted state in a new StateStore instance', () => {
      store.unlockEpisode('ep-007');
      store.setPreference('theme', 'light');

      // Create a brand new instance simulating page reload
      const reloadedStore = new StateStore();
      assert.equal(reloadedStore.isEpisodeUnlocked('ep-007'), true);
      assert.equal(reloadedStore.getPreferences().theme, 'light');
      assert.equal(reloadedStore.isEpisodeUnlocked('ep-001'), true, 'Free episodes must still be unlocked');
    });

    it('should manage likes and reading progress', () => {
      assert.equal(store.isLiked('ep-002'), false);
      const isLikedNow = store.toggleLike('ep-002');
      assert.equal(isLikedNow, true);
      assert.equal(store.isLiked('ep-002'), true);

      store.setReadingProgress('chapitre-01', 0.75);
      assert.equal(store.getReadingProgress('chapitre-01'), 0.75);

      // Out of bounds progress clamping
      store.setReadingProgress('chapitre-02', 1.5);
      assert.equal(store.getReadingProgress('chapitre-02'), 1);
      store.setReadingProgress('chapitre-03', -0.5);
      assert.equal(store.getReadingProgress('chapitre-03'), 0);
    });

    it('should reset state cleanly with resetState', () => {
      store.unlockSeasonPass();
      store.setPreference('theme', 'sepia');
      assert.equal(store.get().has_season_pass, true);

      store.resetState();
      assert.equal(store.get().has_season_pass, false);
      assert.equal(store.isEpisodeUnlocked('ep-004'), false);
      assert.equal(store.isEpisodeUnlocked('ep-001'), true);
    });
  });
});
