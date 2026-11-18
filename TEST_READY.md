# TEST_READY: AMINA Experience PWA Automated Test Suite

## Executive Summary
The automated test infrastructure and test suites (Tiers 1–4) for the **"AMINA Experience"** PWA (Transmedia Gospel Micro-Drama Studio & E-Reader) have been fully implemented, executed, and verified green with 100% passing results across all targets.

- **Unit Test Runner**: Node.js native test runner (`node --test tests/unit/*.test.js` or `npm test`)
- **E2E Test Runner**: Playwright (`npx playwright test` or `npm run test:e2e`)
- **Total Unit Tests**: 45 passed (0 failures)
- **Total E2E Tests**: 20 passed (10 Mobile Safari iPhone 14 + 10 Desktop Chromium, 0 failures)
- **Total Automated Test Assertions/Cases**: 65 test cases, >150 assertions

---

## Test Inventory & Coverage

### 1. Unit Test Suite (`tests/unit/`)
| Test File | Target Module | Test Areas / Scenarios Covered | Tests | Pass |
| :--- | :--- | :--- | :---: | :---: |
| `tests/unit/state.test.js` | `js/state.js` | Initial state schema, freemium rules (ep-001..ep-003 free, ep-004..ep-011 locked), single episode unlock via WhatsApp share, full Season Pass unlock via Mobile Money simulation, preference persistence (`theme`, `fontSize`, `volume`), likes and reading progress management, `localStorage` persistence under `amina_state_v1`. | 14 | 14 |
| `tests/unit/subtitles.test.js` | `episodes/*/subtitles.srt` | Timecode conversions (SRT format `HH:MM:SS,mmm` to seconds and back, WebVTT fallback dot handling), multiline dialogue cues, Windows CRLF vs Unix LF handling, graceful error handling of malformed input, validation against all 11 real on-disk `subtitles.srt` files. | 9 | 9 |
| `tests/unit/episodes-data.test.js` | `js/data/episodes-data.js` | Integrity of all 11 episodes (IDs `ep-001`..`ep-011`, sequential numbers 1..11, titles, hooks, cliffhangers, tiers), free lead magnet media validation (real MP4 master videos and contact sheets on disk for ep-001..ep-003), Suno prompt styles, Flow video prompts, and Psalm 91 verse attachments. | 10 | 10 |
| `tests/unit/book-data.test.js` | `js/data/book-data.js` | Metadata (author Karl DIGRÉ, spiritual inspiration Pastor Yvan Castanou, commercial contact `+225 07 00 88 95 14`, official cover image), Front Matter integrity (Dédicace, Préface, Introduction), all 11 chapters sequential text integrity and Psalm 91 verses, alignment with `source/` files on disk, Guide Pratique (3 spiritual principles and commercial notice). | 12 | 12 |
| **Total Unit** | | | **45** | **45** |

### 2. Playwright E2E Suite (`tests/e2e/`)
| Spec File | Target Environment | Scenarios Covered | Tests | Pass |
| :--- | :--- | :--- | :---: | :---: |
| `tests/e2e/amina-experience.spec.js` | **Mobile Safari (iPhone 14, 390x844)** | **Tier 1:** Shell loading, PWA manifest, meta tags, bottom navigation tab switching (Player ↔ Reader ↔ Store).<br>**Tier 2:** Lead Magnet playback (Ep 1–3 play directly), Ep 4 locked state & motion card display.<br>**Tier 3:** WhatsApp viral share unlock flow (intent link + confirm unlock -> Ep 4 unlocked in state and UI); Mobile Money simulation checkout (Wave CI, Orange Money, MTN MoMo) with realistic multi-step processing, celebration toast, and season pass activation.<br>**Tier 4:** E-Reader font size scaling (A-/A+), 3 themes (Night, Sepia, Light), chapter drawer navigation, floating ambient Afrogospel audio bar toggling, direct WhatsApp book purchase link (+225 07 00 88 95 14).<br>**Real-World Workload:** Complete spectator & reader mobile discovery journey from Ep 1 to unlocked Ep 4 to Chapter 4 reading to Store checkout. | 10 | 10 |
| `tests/e2e/amina-experience.spec.js` | **Desktop Chromium (1280x800)** | Same comprehensive multi-tier test matrix executed in desktop viewport. | 10 | 10 |
| **Total E2E** | | | **20** | **20** |

---

## Verification Commands & Execution

### Run All Unit Tests
```bash
npm test
# OR
npm run test:unit
# OR
node --test tests/unit/*.test.js
```

### Run Playwright E2E Tests
```bash
npm run test:e2e
# OR
npx playwright test
```

### Run Single Project (Mobile or Desktop)
```bash
# Mobile Viewport (iPhone 14 / Safari)
npx playwright test --project="Mobile Safari (iPhone 14)"

# Desktop Viewport (Chromium)
npx playwright test --project="Desktop Chromium"
```

---

## Authoritative Expected Output Sources
1. **ORIGINAL_REQUEST.md**:
   - 11 vertical episodes 9:16 (`episodes/ep-001/` to `episodes/ep-011/`).
   - Freemium rules: Ep 1, 2, 3 free Lead Magnet; Ep 4–11 locked by default.
   - WhatsApp viral share unlock mechanism.
   - Mobile Money Côte d'Ivoire simulation (Wave, Orange Money, MTN MoMo).
   - Direct WhatsApp book ordering with Karl DIGRÉ at `+225 07 00 88 95 14` (`https://wa.me/2250700889514`).
   - Roman complet: 11 chapters + Préambule (Dédicace, Préface, Intro) + Guide pratique inspired by Pastor Yvan Castanou (*hupopiazo* / persistent prayer).
2. **PROJECT.md & TEST_INFRA.md**:
   - Interface contracts: `AminaState` (`isEpisodeUnlocked`, `unlockEpisode`, `unlockSeasonPass`, `getPreferences`, `setPreference`, `on`).
   - UI Safe-Zones, design tokens (Abidjan Twilight Noir & Celestial Gold).
   - Tiers 1–4 progressive testing criteria.
3. **On-Disk Repositories**:
   - Actual master video files for Ep 1, 2, 3 (`episodes/ep-001/output/episode_001_master_9x16.mp4`, `episodes/ep-002/output/ep-002_master_9x16.mp4`, `episodes/ep-003/output/ep-003_master_9x16.mp4`).
   - Actual SRT files for all 11 episodes (`episodes/ep-*/subtitles.srt`).
   - Actual source chapters in `source/chapitre-01.md` through `source/chapitre-11.md`.
