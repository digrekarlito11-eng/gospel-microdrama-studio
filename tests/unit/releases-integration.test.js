const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT_DIR = path.resolve(__dirname, '../../');
const {
  AMINA_EPISODES,
  AMINA_RELEASE_CONFIG,
  RELEASE_TAG,
  RELEASE_BASE_URL,
} = require('../../js/data/episodes-data.js');
const { PlayerEngine } = require('../../js/player.js');

const EXPECTED_REPO_SLUG = 'digrekarlito11-eng/gospel-microdrama-studio';
const EXPECTED_RELEASE_TAG = 'episodes-v1';
const EXPECTED_BASE_URL = `https://github.com/${EXPECTED_REPO_SLUG}/releases/download/${EXPECTED_RELEASE_TAG}`;
const EXPECTED_RELEASE_URL = `https://github.com/${EXPECTED_REPO_SLUG}/releases/tag/${EXPECTED_RELEASE_TAG}`;

describe('Option 3 GitHub Releases & PWA Integration (Unit Tests)', () => {
  describe('Tier 1: AMINA_RELEASE_CONFIG & Additive 11-Episode Schema', () => {
    it('should export valid AMINA_RELEASE_CONFIG pointing to episodes-v1', () => {
      assert.ok(AMINA_RELEASE_CONFIG && typeof AMINA_RELEASE_CONFIG === 'object');
      assert.equal(RELEASE_TAG, EXPECTED_RELEASE_TAG);
      assert.equal(AMINA_RELEASE_CONFIG.tag, EXPECTED_RELEASE_TAG);
      assert.equal(RELEASE_BASE_URL, EXPECTED_BASE_URL);
      assert.equal(AMINA_RELEASE_CONFIG.baseUrl, EXPECTED_BASE_URL);
      assert.equal(AMINA_RELEASE_CONFIG.releaseUrl, EXPECTED_RELEASE_URL);
      assert.match(AMINA_RELEASE_CONFIG.baseUrl, /^https:\/\/github\.com\/[^/]+\/[^/]+\/releases\/download\/episodes-v1$/);
      assert.match(AMINA_RELEASE_CONFIG.releaseUrl, /^https:\/\/github\.com\/[^/]+\/[^/]+\/releases\/tag\/episodes-v1$/);
    });

    it('should provide valid HTTPS remoteVideoUrl, downloadUrl, burned-subtitle flag, and poster for all 11 episodes', () => {
      assert.equal(AMINA_EPISODES.length, 11);

      AMINA_EPISODES.forEach((ep, idx) => {
        const expectedId = `ep-${String(idx + 1).padStart(3, '0')}`;
        const expectedAssetUrl = `${EXPECTED_BASE_URL}/${expectedId}.mp4`;

        assert.equal(ep.id, expectedId);
        assert.equal(ep.remoteVideoUrl, expectedAssetUrl, `${ep.id} remoteVideoUrl mismatch`);
        assert.equal(ep.downloadUrl, expectedAssetUrl, `${ep.id} downloadUrl mismatch`);
        assert.equal(ep.hasRemoteVideo, true, `${ep.id} must set hasRemoteVideo=true`);
        assert.equal(ep.hasBurnedSubtitles, true, `${ep.id} must set hasBurnedSubtitles=true`);
        assert.ok(typeof ep.poster === 'string' && ep.poster.trim().length > 0, `${ep.id} must define a poster`);

        const posterFullPath = path.join(ROOT_DIR, ep.poster);
        assert.ok(fs.existsSync(posterFullPath), `${ep.id} poster must exist on disk at ${posterFullPath}`);
      });
    });

    it('should strictly preserve freemium tier/isFree rules and local video fields', () => {
      AMINA_EPISODES.slice(0, 3).forEach((ep) => {
        assert.equal(ep.isFree, true, `${ep.id} must remain free`);
        assert.equal(ep.tier, 'free', `${ep.id} tier must remain free`);
        assert.equal(ep.hasLocalVideo, true, `${ep.id} must preserve hasLocalVideo=true`);
        assert.ok(typeof ep.videoSrc === 'string' && ep.videoSrc.endsWith('.mp4'), `${ep.id} must preserve videoSrc`);
        assert.ok(fs.existsSync(path.join(ROOT_DIR, ep.videoSrc)), `${ep.id} local video must exist`);
      });

      AMINA_EPISODES.slice(3).forEach((ep) => {
        assert.equal(ep.isFree, false, `${ep.id} must remain locked`);
        assert.equal(ep.tier, 'locked', `${ep.id} tier must remain locked`);
        assert.equal(ep.hasLocalVideo, false, `${ep.id} must preserve hasLocalVideo=false`);
        assert.equal(
          ep.videoSrc,
          `episodes/${ep.id}/output/${ep.id}_master_9x16.mp4`,
          `${ep.id} must preserve canonical local videoSrc path`
        );
      });
    });
  });

  describe('Tier 2: Service Worker v2 Streaming & Range Bypass (sw.js)', () => {
    const swSource = fs.readFileSync(path.join(ROOT_DIR, 'sw.js'), 'utf-8');

    function createSwSandbox() {
      const listeners = {};
      const sandbox = {
        URL,
        console: { log() {}, warn() {}, error() {} },
        caches: {
          open: async () => ({ addAll: async () => {}, put: async () => {} }),
          keys: async () => [],
          delete: async () => true,
          match: async () => undefined,
        },
        fetch: async () => ({ status: 200, type: 'basic', clone() { return this; } }),
        self: null,
      };
      sandbox.self = {
        location: { origin: 'https://digrekarlito11-eng.github.io' },
        addEventListener(type, fn) {
          listeners[type] = fn;
        },
        skipWaiting: async () => {},
        clients: { claim: async () => {} },
      };
      vm.runInNewContext(swSource, sandbox, { filename: 'sw.js' });
      return listeners;
    }

    function dispatchFetch(fetchHandler, { url, method = 'GET', headers = {}, destination = '' }) {
      const normalizedHeaders = new Map(
        Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v])
      );
      let responded = false;
      const event = {
        request: {
          url,
          method,
          destination,
          mode: 'cors',
          headers: {
            has: (key) => normalizedHeaders.has(String(key).toLowerCase()),
            get: (key) => normalizedHeaders.get(String(key).toLowerCase()) || null,
          },
        },
        respondWith(promise) {
          responded = true;
          if (promise && typeof promise.catch === 'function') {
            promise.catch(() => {});
          }
        },
      };
      fetchHandler(event);
      return responded;
    }

    it('should bump CACHE_NAME to amina-pwa-v2', () => {
      assert.match(swSource, /const\s+CACHE_NAME\s*=\s*['"]amina-pwa-v2['"]/);
      assert.doesNotMatch(swSource, /const\s+CACHE_NAME\s*=\s*['"]amina-pwa-v1['"]/);
    });

    it('should bypass cross-origin GitHub Releases & CDN requests', () => {
      const { fetch: fetchHandler } = createSwSandbox();
      assert.equal(typeof fetchHandler, 'function');

      const ghReleaseResponded = dispatchFetch(fetchHandler, {
        url: `${EXPECTED_BASE_URL}/ep-001.mp4`,
        destination: 'video',
      });
      const ghCdnResponded = dispatchFetch(fetchHandler, {
        url: 'https://objects.githubusercontent.com/github-production-release-asset/ep-001.mp4',
      });
      const googleFontsResponded = dispatchFetch(fetchHandler, {
        url: 'https://fonts.googleapis.com/css2?family=Cinzel',
      });

      assert.equal(ghReleaseResponded, false, 'Cross-origin GitHub Releases must bypass SW');
      assert.equal(ghCdnResponded, false, 'Cross-origin objects.githubusercontent.com must bypass SW');
      assert.equal(googleFontsResponded, false, 'Any cross-origin request must bypass SW');
    });

    it('should bypass Range header, video destination, .mp4 paths, videos-manifest.json, and non-GET requests', () => {
      const { fetch: fetchHandler } = createSwSandbox();

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/episodes/ep-001/audio/bgm_gospel.mp3',
          headers: { Range: 'bytes=0-1023' },
        }),
        false,
        'HTTP Range requests must bypass SW'
      );

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/stream/ep-001',
          destination: 'video',
        }),
        false,
        'Requests with destination="video" must bypass SW'
      );

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/episodes/ep-001/output/episode_001_master_9x16.mp4',
        }),
        false,
        'Same-origin .mp4 requests must bypass SW'
      );

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/videos-manifest.json',
        }),
        false,
        'videos-manifest.json must bypass SW to stay fresh'
      );

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/index.html',
          method: 'POST',
        }),
        false,
        'Non-GET requests must bypass SW'
      );
    });

    it('should still intercept and cache normal same-origin app-shell static assets', () => {
      const { fetch: fetchHandler } = createSwSandbox();

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/index.html',
          destination: 'document',
        }),
        true,
        'Same-origin index.html must still be handled by SW cache'
      );

      assert.equal(
        dispatchFetch(fetchHandler, {
          url: 'https://digrekarlito11-eng.github.io/css/player.css',
          destination: 'style',
        }),
        true,
        'Same-origin CSS must still be handled by SW cache'
      );
    });
  });

  describe('Tier 3: PlayerEngine Video Element Contract & Unified Video Helpers (js/player.js)', () => {
    const playerSource = fs.readFileSync(path.join(ROOT_DIR, 'js/player.js'), 'utf-8');

    it('should omit crossorigin attribute on <video> and include playsinline for iOS/GitHub 302 compatibility', () => {
      const videoTagMatch = playerSource.match(/<video\b[^>]*id="main-player-video"[^>]*>/);
      assert.ok(videoTagMatch, 'js/player.js must render <video id="main-player-video">');
      const videoTag = videoTagMatch[0];

      assert.doesNotMatch(videoTag, /\bcrossorigin\b/i, '<video> MUST omit crossorigin to allow GitHub Releases 302 redirects');
      assert.match(videoTag, /\bplaysinline\b/i, '<video> must include playsinline');
      assert.match(videoTag, /\bwebkit-playsinline\b/i, '<video> must include webkit-playsinline');
    });

    it('should expose unified _hasPlayableVideo and _getVideoSources helpers with remote-first priority and deduplication', () => {
      const engine = new PlayerEngine();
      assert.equal(typeof engine._hasPlayableVideo, 'function');
      assert.equal(typeof engine._getVideoSources, 'function');

      // Free episode with both remote + local -> remote first, local second
      const ep1 = AMINA_EPISODES[0];
      assert.equal(engine._hasPlayableVideo(ep1), true);
      assert.deepEqual(engine._getVideoSources(ep1), [ep1.remoteVideoUrl, ep1.videoSrc]);

      // Locked/cloud-only episode -> remote only
      const ep4 = AMINA_EPISODES[3];
      assert.equal(engine._hasPlayableVideo(ep4), true);
      assert.deepEqual(engine._getVideoSources(ep4), [ep4.remoteVideoUrl]);

      // Duplicate remote and local URL -> deduplicated
      const dupEp = {
        hasRemoteVideo: true,
        remoteVideoUrl: 'https://example.com/same.mp4',
        hasLocalVideo: true,
        videoSrc: 'https://example.com/same.mp4',
      };
      assert.deepEqual(engine._getVideoSources(dupEp), ['https://example.com/same.mp4']);

      // Empty / missing sources
      assert.equal(engine._hasPlayableVideo(null), false);
      assert.equal(engine._hasPlayableVideo({ hasRemoteVideo: false, hasLocalVideo: false }), false);
      assert.deepEqual(engine._getVideoSources(null), []);
      assert.deepEqual(engine._getVideoSources({ hasRemoteVideo: true, remoteVideoUrl: '' }), []);
    });

    it('should include CC overlay toggle, buffering indicator, and gated HD download elements in layout', () => {
      assert.match(playerSource, /id="btn-cc-toggle"/);
      assert.match(playerSource, /aria-pressed="false"/);
      assert.match(playerSource, /id="player-buffering"/);
      assert.match(playerSource, /id="action-download-item"/);
      assert.match(playerSource, /id="btn-action-download"/);
      assert.match(playerSource, /id="btn-motion-retry"/);
      assert.match(playerSource, /id="btn-motion-read-chap"/);
    });
  });

  describe('Tier 4: HTML Shell Favicon & Store Releases Card (index.html)', () => {
    const html = fs.readFileSync(path.join(ROOT_DIR, 'index.html'), 'utf-8');

    it('should declare a valid favicon link backed by an existing asset to avoid /favicon.ico 404', () => {
      const iconMatch = html.match(/<link\b[^>]*rel="icon"[^>]*href="([^"]+)"[^>]*>/i);
      assert.ok(iconMatch, 'index.html must include <link rel="icon" ...>');
      const iconPath = path.join(ROOT_DIR, iconMatch[1]);
      assert.ok(fs.existsSync(iconPath), `Favicon target must exist on disk: ${iconPath}`);
    });

    it('should include #store-releases-card linking directly to GitHub Releases tag episodes-v1', () => {
      assert.match(html, /id="store-releases-card"/);
      const releaseBtnMatch = html.match(/<a\b[^>]*href="([^"]+)"[^>]*id="btn-store-releases"[^>]*>|<a\b[^>]*id="btn-store-releases"[^>]*href="([^"]+)"[^>]*>/s);
      assert.ok(releaseBtnMatch, 'index.html must include #btn-store-releases anchor');
      const href = releaseBtnMatch[1] || releaseBtnMatch[2];
      assert.equal(href, EXPECTED_RELEASE_URL);
      assert.match(releaseBtnMatch[0], /target="_blank"/);
      assert.match(releaseBtnMatch[0], /rel="noopener noreferrer"/);
    });

    it('should preserve Mobile Money Pass Saison and WhatsApp direct book purchase CTA (+225 07 00 88 95 14)', () => {
      assert.match(html, /id="btn-store-season-pass"/);
      assert.match(html, /id="btn-store-book-order"/);
      assert.match(html, /https:\/\/wa\.me\/2250700889514/);
    });
  });
});
