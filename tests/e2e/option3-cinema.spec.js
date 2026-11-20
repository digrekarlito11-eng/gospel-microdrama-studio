import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const MP4_FIXTURE_PATH = path.resolve(
  __dirname,
  '../../episodes/ep-001/output/episode_001_master_9x16.mp4'
);
const MP4_BUFFER = fs.readFileSync(MP4_FIXTURE_PATH);
const RELEASE_BASE =
  'https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1';
const RELEASE_TAG_URL =
  'https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/tag/episodes-v1';

/**
 * Fulfill an intercepted MP4 route with real local H.264/AAC bytes,
 * honoring HTTP Range requests (206 Partial Content) for deterministic <video> playback.
 */
async function fulfillMp4Route(route) {
  const headers = route.request().headers();
  const rangeHeader = headers['range'];
  const total = MP4_BUFFER.length;

  if (rangeHeader) {
    const match = /^bytes=(\d*)-(\d*)$/.exec(rangeHeader);
    if (match) {
      const start = match[1] ? parseInt(match[1], 10) : 0;
      const end = match[2] ? Math.min(parseInt(match[2], 10), total - 1) : total - 1;
      const chunk = MP4_BUFFER.subarray(start, end + 1);
      await route.fulfill({
        status: 206,
        contentType: 'video/mp4',
        headers: {
          'Accept-Ranges': 'bytes',
          'Content-Range': `bytes ${start}-${end}/${total}`,
          'Content-Length': String(chunk.length),
        },
        body: chunk,
      });
      return;
    }
  }

  await route.fulfill({
    status: 200,
    contentType: 'video/mp4',
    headers: {
      'Accept-Ranges': 'bytes',
      'Content-Length': String(total),
    },
    body: MP4_BUFFER,
  });
}

async function resetAppState(page) {
  await page.goto('/');
  await page.evaluate(() => {
    localStorage.clear();
    if (window.AminaState) {
      window.AminaState.resetState();
    }
  });
  await page.reload();
  await page.waitForLoadState('domcontentloaded');
}

test.describe('Option 3 Cinéma Animé — GitHub Releases Streaming & Pipeline Integration (Tiers 1-4)', () => {
  test.describe('Tier 1: Free Lead Magnet Streaming (Ep 1-3), Video Attributes & Store Releases Card', () => {
    test('streams Release .mp4 for ep-001..ep-003, omits crossorigin, exposes HD download & Store Releases link', async ({ page }) => {
      const pageErrors = [];
      page.on('pageerror', (err) => pageErrors.push(err.message));

      const requestedReleaseUrls = [];
      await page.route('**/releases/download/**', async (route) => {
        requestedReleaseUrls.push(route.request().url());
        await fulfillMp4Route(route);
      });
      await page.route('**/videos-manifest.json', async (route) => {
        await route.fulfill({ status: 404, body: 'Not Found' });
      });

      await resetAppState(page);

      const videoEl = page.locator('#main-player-video');
      const motionCard = page.locator('#motion-fallback-card');
      const downloadItem = page.locator('#action-download-item');
      const downloadLink = page.locator('#btn-action-download');

      // Ep 1 (default)
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 01/11');
      await expect(videoEl).toBeVisible();
      await expect(motionCard).toBeHidden();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-001.mp4`);

      // Must strictly omit crossorigin & include playsinline for iOS/302 compatibility
      const videoAttrs = await videoEl.evaluate((el) => ({
        crossorigin: el.getAttribute('crossorigin'),
        hasPlaysinline: el.hasAttribute('playsinline'),
      }));
      expect(videoAttrs.crossorigin).toBeNull();
      expect(videoAttrs.hasPlaysinline).toBe(true);

      // Gated HD .mp4 download link visible for free ep-001
      await expect(downloadItem).toBeVisible();
      await expect(downloadLink).toHaveAttribute('href', `${RELEASE_BASE}/ep-001.mp4`);
      await expect(downloadLink).toHaveAttribute('download', 'ep-001.mp4');

      // Ep 2
      await page.evaluate(() => window.AminaPlayer.goToEpisode(1));
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 02/11');
      await expect(videoEl).toBeVisible();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-002.mp4`);
      await expect(downloadLink).toHaveAttribute('href', `${RELEASE_BASE}/ep-002.mp4`);

      // Ep 3
      await page.evaluate(() => window.AminaPlayer.goToEpisode(2));
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 03/11');
      await expect(videoEl).toBeVisible();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-003.mp4`);
      await expect(downloadLink).toHaveAttribute('href', `${RELEASE_BASE}/ep-003.mp4`);

      // Confirm actual network fetches hit Release URLs for ep-001..ep-003
      expect(requestedReleaseUrls.some((u) => u.endsWith('/ep-001.mp4'))).toBe(true);
      expect(requestedReleaseUrls.some((u) => u.endsWith('/ep-002.mp4'))).toBe(true);
      expect(requestedReleaseUrls.some((u) => u.endsWith('/ep-003.mp4'))).toBe(true);

      // Store tab exposes #store-releases-card linking to episodes-v1
      await page.locator('.nav-item[data-tab="store"]').click();
      await expect(page.locator('#store-releases-card')).toBeVisible();
      const storeReleaseBtn = page.locator('#btn-store-releases');
      await expect(storeReleaseBtn).toBeVisible();
      await expect(storeReleaseBtn).toHaveAttribute('href', RELEASE_TAG_URL);

      expect(pageErrors).toEqual([]);
    });
  });

  test.describe('Tier 2: Strict Monetization Gating on Locked Episodes (Ep 4-11)', () => {
    test('clears <video> src and hides/strips #btn-action-download href for locked ep-004..ep-011', async ({ page }) => {
      await page.route('**/releases/download/**', fulfillMp4Route);
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      const videoEl = page.locator('#main-player-video');
      const downloadItem = page.locator('#action-download-item');
      const downloadLink = page.locator('#btn-action-download');
      const motionCard = page.locator('#motion-fallback-card');
      const statusBadge = page.locator('#motion-status-badge');

      // Spot-check start, middle, and finale of locked tier (ep-004, ep-007, ep-011)
      for (const idx of [3, 6, 10]) {
        await page.evaluate((i) => window.AminaPlayer.goToEpisode(i), idx);

        await expect(motionCard).toBeVisible();
        await expect(statusBadge).toHaveText('Verrouillé');
        await expect(videoEl).toBeHidden();
        await expect(downloadItem).toBeHidden();

        const gatedState = await page.evaluate(() => {
          const v = document.getElementById('main-player-video');
          const a = document.getElementById('btn-action-download');
          return {
            videoSrcAttr: v.getAttribute('src'),
            downloadHref: a.getAttribute('href'),
            downloadAttr: a.getAttribute('download'),
          };
        });
        expect(gatedState.videoSrcAttr).toBeNull();
        expect(gatedState.downloadHref).toBeNull();
        expect(gatedState.downloadAttr).toBeNull();
      }
    });
  });

  test.describe('Tier 3: Unlock-to-Stream & Burned-In Subtitle CC Toggle', () => {
    test('unlocking ep-004 via WhatsApp share immediately streams ep-004.mp4 and exposes HD .mp4 download link', async ({ page }) => {
      await page.route('**/releases/download/**', fulfillMp4Route);
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      await page.evaluate(() => window.AminaPlayer.goToEpisode(3));
      await expect(page.locator('#motion-status-badge')).toHaveText('Verrouillé');
      await expect(page.locator('#action-download-item')).toBeHidden();

      // Unlock via WhatsApp viral share modal
      await page.locator('#btn-motion-unlock').click();
      await expect(page.locator('#monetization-modal-backdrop')).toHaveClass(/open/);
      await page.locator('#btn-confirm-wa-share').click();
      await expect(page.locator('#monetization-modal-backdrop')).not.toHaveClass(/open/);

      // Immediately streams ep-004.mp4 without needing manual reload
      const videoEl = page.locator('#main-player-video');
      await expect(videoEl).toBeVisible();
      await expect(page.locator('#motion-fallback-card')).toBeHidden();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-004.mp4`);

      // HD .mp4 download link immediately exposed
      await expect(page.locator('#action-download-item')).toBeVisible();
      await expect(page.locator('#btn-action-download')).toHaveAttribute('href', `${RELEASE_BASE}/ep-004.mp4`);
      await expect(page.locator('#btn-action-download')).toHaveAttribute('download', 'ep-004.mp4');
    });

    test('unlocking Season Pass via Wave Mobile Money unlocks all 11 episodes and streams ep-011.mp4 immediately', async ({ page }) => {
      await page.route('**/releases/download/**', fulfillMp4Route);
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      // Navigate to locked finale ep-011
      await page.evaluate(() => window.AminaPlayer.goToEpisode(10));
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 11/11');
      await expect(page.locator('#motion-status-badge')).toHaveText('Verrouillé');

      // Open modal -> Mobile Money tab -> Wave CI -> Submit
      await page.locator('#btn-motion-unlock').click();
      await page.locator('#tab-btn-pass').click();
      await page.locator('#op-wave').click();
      await page.locator('#btn-submit-momo').click();

      await expect(page.locator('#momo-success-view')).toBeVisible({ timeout: 10000 });
      await page.locator('#btn-close-success').click();

      // All 11 episodes unlocked in state
      const allUnlocked = await page.evaluate(() =>
        window.AMINA_EPISODES.every((ep) => window.AminaState.isEpisodeUnlocked(ep.id))
      );
      expect(allUnlocked).toBe(true);

      // ep-011.mp4 streams immediately with HD download exposed
      const videoEl = page.locator('#main-player-video');
      await expect(videoEl).toBeVisible();
      await expect(page.locator('#motion-fallback-card')).toBeHidden();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-011.mp4`);
      await expect(page.locator('#btn-action-download')).toHaveAttribute('href', `${RELEASE_BASE}/ep-011.mp4`);
    });

    test('suppresses duplicate HTML subtitle cue by default on burned-in Release MP4 and toggles cleanly via #btn-cc-toggle', async ({ page }) => {
      await page.route('**/releases/download/**', fulfillMp4Route);
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      const videoEl = page.locator('#main-player-video');
      const ccBtn = page.locator('#btn-cc-toggle');
      const subtitleCue = page.locator('#player-subtitle-cue');

      await expect(videoEl).toBeVisible();
      await expect(ccBtn).toHaveAttribute('aria-pressed', 'false');

      // Wait until video metadata is loaded so currentTime seek is honored
      await page.waitForFunction(() => {
        const v = document.getElementById('main-player-video');
        return v && v.readyState >= 1;
      });

      // Seek inside cue #1 (0.5s - 4.5s) and dispatch timeupdate -> cue MUST stay hidden by default
      await page.evaluate(() => {
        const v = document.getElementById('main-player-video');
        v.pause();
        v.currentTime = 2.0;
        v.dispatchEvent(new Event('timeupdate'));
      });
      await expect(subtitleCue).toBeHidden();

      // Toggle CC ON -> aria-pressed="true" and HTML subtitle cue displays immediately
      await ccBtn.click();
      await expect(ccBtn).toHaveAttribute('aria-pressed', 'true');
      await expect(subtitleCue).toBeVisible();
      await expect(subtitleCue).toContainText('Yopougon');

      // Toggle CC OFF -> aria-pressed="false" and HTML subtitle cue hides immediately
      await ccBtn.click();
      await expect(ccBtn).toHaveAttribute('aria-pressed', 'false');
      await expect(subtitleCue).toBeHidden();
    });
  });

  test.describe('Tier 4: Offline Fallback, Retry Recovery & videos-manifest.json Hydration', () => {
    test('falls back seamlessly to local MP4 on ep-001 when remote Release is aborted', async ({ page }) => {
      await page.route('**/releases/download/**', (route) => route.abort());
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      const videoEl = page.locator('#main-player-video');
      await expect(videoEl).toBeVisible();
      await expect(videoEl).toHaveAttribute('src', /episodes\/ep-001\/output\/episode_001_master_9x16\.mp4$/);
      await expect(page.locator('#motion-fallback-card')).toBeHidden();
    });

    test('shows offline fallback card with Retry & Read Chapter for unlocked ep-004 when remote fails, and recovers on Retry', async ({ page }) => {
      let networkRestored = false;
      await page.route('**/releases/download/**', async (route) => {
        if (!networkRestored) {
          await route.abort();
          return;
        }
        await fulfillMp4Route(route);
      });
      await page.route('**/videos-manifest.json', (route) => route.fulfill({ status: 404, body: '' }));

      await resetAppState(page);

      // Unlock ep-004 while remote Release network is down
      await page.evaluate(() => {
        window.AminaState.unlockEpisode('ep-004');
        window.AminaPlayer.goToEpisode(3);
      });

      const motionCard = page.locator('#motion-fallback-card');
      const retryBtn = page.locator('#btn-motion-retry');
      const readChapBtn = page.locator('#btn-motion-read-chap');

      await expect(motionCard).toBeVisible();
      await expect(page.locator('#motion-status-badge')).toHaveText('Accès Débloqué');
      await expect(page.locator('#motion-lock-box')).toContainText('Vidéo HD momentanément indisponible');
      await expect(retryBtn).toBeVisible();
      await expect(readChapBtn).toBeVisible();

      // Clicking Read Chapter opens Chapter 4 in E-Reader
      await readChapBtn.click();
      await expect(page.locator('#screen-reader')).toHaveClass(/active/);
      await expect(page.locator('#reader-article-content')).toContainText(/Chapitre 0?4|Le Guet-apens/i);

      // Return to Player, restore network, and click Retry -> recovers streaming ep-004.mp4
      await page.locator('.nav-item[data-tab="player"]').click();
      networkRestored = true;
      await retryBtn.click();

      const videoEl = page.locator('#main-player-video');
      await expect(videoEl).toBeVisible();
      await expect(motionCard).toBeHidden();
      await expect(videoEl).toHaveAttribute('src', `${RELEASE_BASE}/ep-004.mp4`);
    });

    test('hydrates episode URLs & metadata from videos-manifest.json while 404 manifest degrades silently', async ({ page }) => {
      const pageErrors = [];
      page.on('pageerror', (err) => pageErrors.push(err.message));

      const hydratedVideoUrl = `${RELEASE_BASE}/ep-001.mp4?v=manifest2`;
      const hydratedDownloadUrl = `${RELEASE_BASE}/ep-001.mp4?dl=manifest2`;
      const hydratedManifest = {
        releaseTag: 'episodes-v1',
        releaseUrl: RELEASE_TAG_URL,
        generatedAt: '2026-11-18T23:55:00Z',
        episodes: {
          'ep-001': {
            id: 'ep-001',
            videoUrl: hydratedVideoUrl,
            downloadUrl: hydratedDownloadUrl,
            posterUrl: 'episodes/ep-001/output/contact_sheet.jpg',
            duration: 82.5,
            sizeBytes: 15200000,
            resolution: '1080x1920',
            hasBurnedSubtitles: true,
            providers: { pollinations: 5, aihorde: 4, fallback: 0 },
          },
        },
      };

      await page.route('**/releases/download/**', fulfillMp4Route);
      await page.route('**/videos-manifest.json', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(hydratedManifest),
        });
      });

      await resetAppState(page);

      await page.waitForFunction(() => window.AminaPlayer && window.AminaPlayer.manifestHydrated === true);

      await expect(page.locator('#main-player-video')).toHaveAttribute('src', hydratedVideoUrl);
      await expect(page.locator('#btn-action-download')).toHaveAttribute('href', hydratedDownloadUrl);

      const ep1Duration = await page.evaluate(() => window.AMINA_EPISODES[0].duration);
      expect(ep1Duration).toBe(82.5);
      expect(pageErrors).toEqual([]);
    });
  });
});
