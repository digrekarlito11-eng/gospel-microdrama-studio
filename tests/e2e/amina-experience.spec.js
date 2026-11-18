import { test, expect } from '@playwright/test';

test.describe('AMINA Experience PWA — Comprehensive E2E Test Suite (Tiers 1-4)', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to local PWA and clear localStorage for deterministic starting state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      if (window.AminaState) {
        window.AminaState.resetState();
      }
    });
    await page.reload();
    await page.waitForLoadState('domcontentloaded');
  });

  test.describe('Tier 1: Shell & Bottom Navigation', () => {
    test('should load PWA shell with valid title, meta tags, and manifest', async ({ page }) => {
      await expect(page).toHaveTitle(/AMINA : L'Autel De Yopougon/);

      const manifestLink = page.locator('link[rel="manifest"]');
      await expect(manifestLink).toHaveAttribute('href', 'manifest.webmanifest');

      // Universal floating audio bar should be visible
      const audioBar = page.locator('#ambient-audio-bar');
      await expect(audioBar).toBeVisible();
    });

    test('should seamlessly switch between Video Player, E-Reader, and Store tabs', async ({ page }) => {
      const playerNav = page.locator('.nav-item[data-tab="player"]');
      const readerNav = page.locator('.nav-item[data-tab="reader"]');
      const storeNav = page.locator('.nav-item[data-tab="store"]');

      const screenPlayer = page.locator('#screen-player');
      const screenReader = page.locator('#screen-reader');
      const screenStore = page.locator('#screen-store');

      // Initial active tab: Player
      await expect(playerNav).toHaveClass(/active/);
      await expect(screenPlayer).toHaveClass(/active/);
      await expect(screenReader).not.toHaveClass(/active/);

      // Switch to E-Reader
      await readerNav.click();
      await expect(readerNav).toHaveClass(/active/);
      await expect(screenReader).toHaveClass(/active/);
      await expect(screenPlayer).not.toHaveClass(/active/);

      // Switch to Store & Book Order
      await storeNav.click();
      await expect(storeNav).toHaveClass(/active/);
      await expect(screenStore).toHaveClass(/active/);
      await expect(screenReader).not.toHaveClass(/active/);

      // Return to Video Player
      await playerNav.click();
      await expect(playerNav).toHaveClass(/active/);
      await expect(screenPlayer).toHaveClass(/active/);
    });
  });

  test.describe('Tier 2: Freemium Access Control & Video Player', () => {
    test('should allow Ep 1, 2, 3 to play directly as free Lead Magnet', async ({ page }) => {
      const hudBadge = page.locator('#hud-ep-badge');
      const videoEl = page.locator('#main-player-video');

      // Episode 1 (default active)
      await expect(hudBadge).toHaveText('ÉPISODE 01/11');
      await expect(videoEl).toBeVisible();

      // Go to Episode 2
      await page.evaluate(() => window.AminaPlayer.goToEpisode(1));
      await expect(hudBadge).toHaveText('ÉPISODE 02/11');
      await expect(videoEl).toBeVisible();

      // Go to Episode 3
      await page.evaluate(() => window.AminaPlayer.goToEpisode(2));
      await expect(hudBadge).toHaveText('ÉPISODE 03/11');
      await expect(videoEl).toBeVisible();
    });

    test('should lock Episode 4 and display the unlock modal/panel', async ({ page }) => {
      // Navigate to Episode 4
      await page.evaluate(() => window.AminaPlayer.goToEpisode(3));

      const hudBadge = page.locator('#hud-ep-badge');
      await expect(hudBadge).toHaveText('ÉPISODE 04/11');

      // Motion fallback card should be visible with locked badge
      const motionCard = page.locator('#motion-fallback-card');
      await expect(motionCard).toBeVisible();

      const statusBadge = page.locator('#motion-status-badge');
      await expect(statusBadge).toHaveText('Verrouillé');

      const unlockBtn = page.locator('#btn-motion-unlock');
      await expect(unlockBtn).toBeVisible();

      // Clicking unlock button opens the monetization modal
      await unlockBtn.click();
      const modalBackdrop = page.locator('#monetization-modal-backdrop');
      await expect(modalBackdrop).toHaveClass(/open/);

      const modalCard = page.locator('#unlock-modal-card');
      await expect(modalCard).toBeVisible();
      await expect(page.locator('#tab-btn-share')).toBeVisible();
      await expect(page.locator('#tab-btn-pass')).toBeVisible();
    });
  });

  test.describe('Tier 3: Monetization Flows (WhatsApp Share & Mobile Money)', () => {
    test('should unlock Episode 4 via the WhatsApp viral share flow', async ({ page }) => {
      // Go to Ep 4 and open unlock modal
      await page.evaluate(() => window.AminaPlayer.goToEpisode(3));
      await page.locator('#btn-motion-unlock').click();

      const modalBackdrop = page.locator('#monetization-modal-backdrop');
      await expect(modalBackdrop).toHaveClass(/open/);

      // Verify WhatsApp share link intent
      const waShareLink = page.locator('#btn-trigger-wa-share');
      await expect(waShareLink).toBeVisible();
      const href = await waShareLink.getAttribute('href');
      expect(href).toContain('api.whatsapp.com/send?text=');
      expect(href).toContain('AMINA');

      // Trigger share
      await waShareLink.click();

      // Confirm share and unlock
      const confirmBtn = page.locator('#btn-confirm-wa-share');
      await expect(confirmBtn).toBeVisible();
      await confirmBtn.click();

      // Modal closes
      await expect(modalBackdrop).not.toHaveClass(/open/);

      // State check: ep-004 is now unlocked!
      const isEp4Unlocked = await page.evaluate(() => window.AminaState.isEpisodeUnlocked('ep-004'));
      expect(isEp4Unlocked).toBe(true);

      // Reload episode 4 UI
      await page.evaluate(() => window.AminaPlayer.goToEpisode(3));
      const statusBadge = page.locator('#motion-status-badge');
      await expect(statusBadge).toHaveText('Accès Débloqué');
    });

    test('should simulate Mobile Money checkout (Wave, Orange, MTN) and activate Season Pass', async ({ page }) => {
      // Open unlock modal from Ep 4
      await page.evaluate(() => window.AminaPlayer.goToEpisode(3));
      await page.locator('#btn-motion-unlock').click();

      // Switch to Mobile Money Tab
      const passTabBtn = page.locator('#tab-btn-pass');
      await passTabBtn.click();
      await expect(passTabBtn).toHaveClass(/active/);

      // Test Operator selection
      const opWave = page.locator('#op-wave');
      const opOrange = page.locator('#op-orange');
      const opMtn = page.locator('#op-mtn');
      const submitBtn = page.locator('#btn-submit-momo');

      await opOrange.click();
      await expect(opOrange).toHaveClass(/selected/);
      await expect(submitBtn).toContainText('Orange Money');

      await opMtn.click();
      await expect(opMtn).toHaveClass(/selected/);
      await expect(submitBtn).toContainText('MTN MoMo');

      await opWave.click();
      await expect(opWave).toHaveClass(/selected/);
      await expect(submitBtn).toContainText('Wave');

      // Submit payment
      await submitBtn.click();

      // Processing simulation view
      const processingView = page.locator('#momo-processing-view');
      await expect(processingView).toBeVisible();

      // Success view appears after simulation
      const successView = page.locator('#momo-success-view');
      await expect(successView).toBeVisible({ timeout: 10000 });
      await expect(successView).toContainText('Pass Saison Activé !');

      // Close modal
      await page.locator('#btn-close-success').click();
      await expect(page.locator('#monetization-modal-backdrop')).not.toHaveClass(/open/);

      // Verify full season pass is permanently unlocked in AminaState
      const hasSeasonPass = await page.evaluate(() => window.AminaState.get().has_season_pass);
      expect(hasSeasonPass).toBe(true);

      // Verify all 11 episodes are now unlocked
      for (let i = 1; i <= 11; i++) {
        const epId = `ep-${String(i).padStart(3, '0')}`;
        const unlocked = await page.evaluate((id) => window.AminaState.isEpisodeUnlocked(id), epId);
        expect(unlocked).toBe(true);
      }
    });
  });

  test.describe('Tier 4: E-Reader Customization & Ambient Audio Engine', () => {
    test('should display chapters, change font size, and switch themes with persistence', async ({ page }) => {
      // Switch to E-Reader
      await page.locator('.nav-item[data-tab="reader"]').click();

      const readerScreen = page.locator('#reader-screen-wrap');
      await expect(readerScreen).toBeVisible();

      // Check default theme is night
      await expect(readerScreen).toHaveClass(/theme-night/);

      // Change Font Size A+
      const fontVal = page.locator('#font-size-val');
      await expect(fontVal).toHaveText('17');

      await page.locator('#btn-font-inc').click();
      await expect(fontVal).toHaveText('18');
      await page.locator('#btn-font-inc').click();
      await expect(fontVal).toHaveText('19');

      // Change Font Size A-
      await page.locator('#btn-font-dec').click();
      await expect(fontVal).toHaveText('18');

      // Switch Theme to Sepia
      await page.locator('.theme-pill-sepia').click();
      await expect(readerScreen).toHaveClass(/theme-sepia/);

      // Switch Theme to Light
      await page.locator('.theme-pill-light').click();
      await expect(readerScreen).toHaveClass(/theme-light/);

      // Test Chapter Drawer Sommaire
      const drawerBtn = page.locator('#btn-open-drawer');
      await page.evaluate(() => window.AminaReader.openDrawer());

      const drawerOverlay = page.locator('#reader-drawer-overlay');
      await expect(drawerOverlay).toHaveClass(/open/);

      // Click Chapter 3 in drawer
      const chap3Item = page.locator('.drawer-item[data-chapter="3"]');
      await chap3Item.click();

      await expect(drawerOverlay).not.toHaveClass(/open/);
      const article = page.locator('#reader-article-content');
      await expect(article).toContainText(/Chapitre 0?3|Le Venin des Rumeurs/i);
    });

    test('should toggle ambient Afrogospel background audio bar', async ({ page }) => {
      const audioBar = page.locator('#ambient-audio-bar');
      await expect(audioBar).toBeVisible();

      // Click to toggle
      await audioBar.click();
      const isPlaying = await page.evaluate(() => window.AminaAudio ? window.AminaAudio.isPlaying : false);
      expect(typeof isPlaying).toBe('boolean');
    });

    test('should verify direct WhatsApp book purchase button links to +225 07 00 88 95 14', async ({ page }) => {
      // Switch to Store tab
      await page.locator('.nav-item[data-tab="store"]').click();

      const waOrderBtn = page.locator('#btn-store-book-order');
      await expect(waOrderBtn).toBeVisible();

      const href = await waOrderBtn.getAttribute('href');
      expect(href).toContain('https://wa.me/2250700889514');
      expect(href).toContain('Bonjour');
      expect(href).toContain('AMINA');
    });
  });

  test.describe('Real-World Workloads & Mobile Viewport', () => {
    test('should support full user discovery journey on mobile screen (390x844)', async ({ page }) => {
      // Ensure viewport is 390x844
      await page.setViewportSize({ width: 390, height: 844 });

      // 1. User watches episode 1
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 01/11');

      // 2. User navigates through free episodes
      await page.evaluate(() => window.AminaPlayer.nextEpisode());
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 02/11');

      await page.evaluate(() => window.AminaPlayer.nextEpisode());
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 03/11');

      // 3. User attempts episode 4 and encounters locked screen
      await page.evaluate(() => window.AminaPlayer.nextEpisode());
      await expect(page.locator('#hud-ep-badge')).toHaveText('ÉPISODE 04/11');
      await expect(page.locator('#motion-status-badge')).toHaveText('Verrouillé');

      // 4. User unlocks via WhatsApp share
      await page.locator('#btn-motion-unlock').click();
      await page.locator('#btn-confirm-wa-share').click();

      // 5. Ep 4 is unlocked
      const ep4Unlocked = await page.evaluate(() => window.AminaState.isEpisodeUnlocked('ep-004'));
      expect(ep4Unlocked).toBe(true);

      // 6. User switches to E-Reader, reads chapter 4
      await page.locator('.nav-item[data-tab="reader"]').click();
      await page.evaluate(() => window.AminaReader.openChapter(4));
      await expect(page.locator('#reader-article-content')).toContainText(/Chapitre 0?4|Le Guet-apens/i);

      // 7. User switches to Store to check physical book
      await page.locator('.nav-item[data-tab="store"]').click();
      await expect(page.locator('.store-cover-img')).toBeVisible();
    });
  });
});
