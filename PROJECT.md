# Project: AMINA Experience PWA Transmédia

## Overview
L'application web mobile-first transmédia "AMINA Experience" adapte le roman chrétien à succès *"AMINA : L'Autel De Yopougon — La Guerre Invisible"* par Karl DIGRÉ (inspiré des enseignements du pasteur Yvan Castanou sur la prière persistante et le combat d'usure *hupopiazo*).

Elle réunit au sein d'une Progressive Web App (PWA) fluide, sans dépendance lourde, hébergeable directement sur GitHub Pages :
1. Une interface mobile immersive aux couleurs d'Abidjan la nuit (or céleste `#D4AF37`, ambre crépuscule `#FF7A00`, bleu nuit `#0A1128`, noir profond `#070709`).
2. Un lecteur vertical 9:16 pour les 11 épisodes de micro-dramas (gestes verticaux type TikTok/Reels, sous-titres Safe-Zone synchronisés, scrubber, HUD).
3. Une liseuse interactive complète des 11 chapitres, du préambule (Dédicace, Préface, Introduction) et du Guide pratique, avec réglage de police A-/A+, thèmes (Nuit, Sépia, Clair) et ambiance sonore Afrogospel en boucle (avec fallback synthétiseur Web Audio).
4. Un moteur de monétisation et de déblocage :
   - Épisodes 1, 2, 3 en accès libre (Lead Magnet viral).
   - Épisodes 4 à 11 déblocables par partage WhatsApp viral ou par simulation réaliste de Mobile Money ivoirien (Wave, Orange Money, MTN MoMo).
   - Passerelle de commande directe du roman papier/e-book au `+225 07 00 88 95 14`.

---

## Architecture
- **Modèle :** Single Page Application (SPA) PWA Vanilla ES6+ HTML5/CSS3.
- **Zéro dépendance lourde d'exécution :** Aucune librairie externe bloquante, chargement ultra-rapide (< 200ms FCP), 100% autonome et résiliente hors-ligne via Service Worker (`sw.js`).
- **Composants d'Interface :**
  - **Shell & Navigation :** Barre de navigation inférieure mobile (Micro-Dramas 9:16, Liseuse, Roman Papier & Pass Saison).
  - **Moteur Vidéo 9:16 (`js/player.js`, `css/player.css`) :** Défilement vertical à détection gestuelle (`touchstart`/`touchend`, molette, clavier), gestion d'un unique élément vidéo actif, synchronisation des sous-titres Safe-Zone SRT/VTT, lecteur de substitution cinématographique (motion cards) pour les épisodes verrouillés ou en cours de production.
  - **Moteur Liseuse (`js/reader.js`, `css/reader.css`) :** Rendu typographique élégant, lettrines dorées, tiroir de navigation latérale des chapitres, curseur de taille de police, 3 thèmes avec persistance.
  - **Moteur Audio (`js/audio.js`) :** Piste Afrogospel `bgm_gospel.mp3` en boucle avec contrôle de volume et atténuation automatique (ducking) lors de la lecture d'une vidéo ; générateur procédural polyphonique de secours via Web Audio API en cas de coupure réseau.
  - **Moteur de Monétisation & Déblocage (`js/monetization.js`, `css/modals.css`) :** Gestionnaire d'état réactif (`js/state.js`) sauvegardé dans `localStorage`, modal de partage WhatsApp avec compteur, modal de simulation Mobile Money Wave/Orange/MTN avec UX réaliste, liens directs d'achat WhatsApp `https://wa.me/2250700889514`.

---

## Code Layout
```text
/home/antigravity/digrekarlito11-eng/gospel-microdrama-studio/
├── index.html                     # Application Shell mobile-first
├── manifest.webmanifest           # Manifest PWA (icônes, standalone, couleurs)
├── sw.js                          # Service Worker (stratégie Cache-First / Stale-While-Revalidate)
├── css/
│   ├── design-system.css          # Variables CSS, palette Abidjan, typographie, reset mobile
│   ├── player.css                 # Lecteur 9:16 vertical, gestures, scrubber, overlays, sous-titres
│   ├── reader.css                 # Liseuse de chapitres, navigation drawer, thèmes, audio bar
│   └── modals.css                 # Modales de monétisation Wave/Orange/MTN et partage WhatsApp
├── js/
│   ├── app.js                     # Point d'entrée, routage par onglets, service worker registration
│   ├── state.js                   # Gestionnaire d'état réactif (localStorage: amina_state_v1)
│   ├── player.js                  # Moteur gestuel 9:16, lecture vidéo, sous-titres, HUD
│   ├── reader.js                  # Moteur liseuse, pagination chapitres, réglages police, thèmes
│   ├── audio.js                   # Lecteur Afrogospel & fallback synthétiseur Web Audio
│   ├── monetization.js            # Déblocage, modales Wave/Orange/MTN, WhatsApp intent
│   └── data/
│       ├── episodes-data.js       # Registre complet des 11 épisodes (métadonnées, hooks, sous-titres)
│       └── book-data.js           # Texte intégral des 11 chapitres, préambule et guide pratique
└── tests/
    ├── e2e/
    │   └── amina.spec.js          # Tests E2E Playwright (mobile, desktop, navigation, déblocage)
    └── unit/
        ├── state.test.js          # Tests unitaires du modèle d'état et règles de déblocage
        └── subtitles.test.js      # Tests unitaires du parseur de sous-titres SRT
```

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Visual Identity & Mobile Shell | Charte Abidjan Twilight Noir (or, ambre, bleu nuit, noir), bottom navigation, PWA manifest, service worker | M1 | Survey & ORIGINAL_REQUEST |
| 2 | Data Layer (Episodes & Book) | Registre JavaScript des 11 épisodes et texte intégral des 11 chapitres + préambule + guide | M1 | Survey (`source/*.md`, `episodes/*`) |
| 3 | 9:16 Vertical Micro-Drama Player | Lecteur vertical gesture-based type TikTok/Reels, scrubber, play/pause, HUD, son toggle, swipe haut/bas | M2 | Survey & ORIGINAL_REQUEST |
| 4 | Safe-Zone Subtitles System | Affichage synchronisé des sous-titres SRT/VTT dans la safe-zone mobile (y=75%) | M2 | Survey & `episodes/*/subtitles.srt` |
| 5 | Video & Motion Fallback Player | Lecture des masters MP4 pour ep 1-3 et affichage cinématique motion card avec citation pour ep 4-11 | M2 | Survey |
| 6 | Interactive E-Book Reader | Liseuse des 11 chapitres + préambule + guide pratique, tiroir chapitres, lettrines, lecture fluide | M3 | Survey & ORIGINAL_REQUEST |
| 7 | Reader Customization & Themes | Slider de taille de police (15px-24px), 3 thèmes (Nuit, Sépia, Clair) avec persistance | M3 | Survey & ORIGINAL_REQUEST |
| 8 | Afrogospel Ambient Audio Engine | Musique ambiante `bgm_gospel.mp3` en boucle, volume, ducking vidéo, secours Web Audio synth | M3 | Survey & ORIGINAL_REQUEST |
| 9 | Freemium Access Control | Épisodes 1-3 en accès direct gratuit ; épisodes 4-11 verrouillés par modal de conversion | M4 | Survey & ORIGINAL_REQUEST |
| 10 | Viral WhatsApp Share Unlock | Modal de partage viral WhatsApp vers ses contacts/statuts débloquant l'épisode | M4 | Survey & ORIGINAL_REQUEST |
| 11 | Mobile Money Simulation Checkout | Parcours de paiement réaliste Wave CI, Orange Money CI, MTN MoMo CI débloquant le Pass Saison | M4 | Survey & ORIGINAL_REQUEST |
| 12 | Direct WhatsApp Book Purchase CTA | Bouton et bannières vers `https://wa.me/2250700889514` pour commande du livre dédicacé | M4 | Survey & ORIGINAL_REQUEST |
| 13 | Comprehensive E2E & Unit Test Suite | Tests unitaires Node.js + suite Playwright validant les 4 paliers (features, limites, interactions, E2E) | E2E Track | ORIGINAL_REQUEST |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **E2E** | E2E Testing Track | Test infra, unit tests, Playwright E2E suite (Tiers 1-4), `TEST_READY.md` | none | DONE |
| **M1** | Core Shell, Data & Design System | `index.html`, PWA manifest, `sw.js`, `design-system.css`, `state.js`, `episodes-data.js`, `book-data.js` | none | DONE |
| **M2** | 9:16 Vertical Video/Motion Player | `player.css`, `player.js`, swipe gestures, Safe-Zone subtitles parser, video player & motion fallback | M1 | DONE |
| **M3** | Interactive E-Reader & Ambient Audio | `reader.css`, `reader.js`, `audio.js`, chapter drawer, font size controls, themes, gospel loop & Web Audio | M1 | DONE |
| **M4** | Monetization, Unlock & WhatsApp Flow | `modals.css`, `monetization.js`, free/locked rules, WhatsApp share unlock, Wave/Orange/MTN simulation, direct book CTA | M2, M3 | DONE |
| **M5** | Final Integration & Adversarial Verification | 100% E2E test pass, static deployment check, adversarial stress testing | E2E, M4 | DONE |

---

## Interface Contracts

### `state.js` ↔ All Modules
```javascript
// Exposes window.AminaState
AminaState.get(); // Returns current state object
AminaState.isEpisodeUnlocked(episodeId); // boolean (true for ep-001..ep-003, or if in unlocked_episodes, or has_season_pass)
AminaState.unlockEpisode(episodeId); // saves to localStorage & triggers event
AminaState.unlockSeasonPass(); // saves has_season_pass: true & triggers event
AminaState.getPreferences(); // { theme, fontSize, volume, lastChapter, lastEpisode }
AminaState.setPreference(key, value);
AminaState.on(eventName, callback); // 'stateChange', 'episodeUnlocked', 'themeChanged'
```

### `player.js` ↔ `audio.js`
```javascript
// When video plays:
AminaAudio.duck(); // lowers background audio volume or pauses background music
// When video pauses or user navigates to reader:
AminaAudio.unduck(); // restores ambient gospel music
```

### `monetization.js` ↔ `player.js` & `reader.js`
```javascript
AminaMonetization.openUnlockModal(episodeId); // opens modal with WhatsApp Share or Mobile Money choice
AminaMonetization.openOrderModal(); // opens direct WhatsApp book order modal
```

---

# Extension Option 3 : Cinéma Animé 100% Gratuit (Sans API Payante)

## Option 3 Architecture
Pipeline cloud 100% gratuit sur GitHub Actions (`ubuntu-latest`, **zéro clé API payante**) produisant automatiquement les **11 épisodes complets (`ep-001` à `ep-011`)** en Full HD **1080×1920 @ 24fps (9:16)** Motion-Cinema 2.5D, publiés sur GitHub Releases (`episodes-v1`) et streamés directement dans la PWA **AMINA Experience** sur GitHub Pages :

1. **Storyboards Canoniques 11 Épisodes (`scripts/storyboards.py`) :** Adaptés fidèlement de `source/chapitre-01.md`..`chapitre-11.md` (résolvant le conflit d'ancien brouillon `ep-002/script.md`), avec 8–10 scènes cinématographiques par épisode (prompts anglais *Abidjan Twilight Noir*, mouvements de caméra 2.5D, dialogues multi-personnages français, humeur musicale et BPM issus de `prompts-suno.txt`, hook d'intro et CTA final `+225 07 00 88 95 14`).
2. **Moteur Voix Multi-Personnages Français (`scripts/voice_engine.py` + `bible/characters.json`) :** Utilise `edge-tts>=7.3.1` exclusivement sur des voix françaises Neural gratuites vérifiées (`fr-FR-VivienneMultilingualNeural`, `fr-FR-DeniseNeural`, `fr-FR-RemyMultilingualNeural`, `fr-FR-HenriNeural`, `fr-FR-EloiseNeural`, `fr-BE-GerardNeural`, `fr-CH-FabriceNeural`, `fr-BE-CharlineNeural`, `fr-CA-JeanNeural`), remplaçant les voix Azure payantes invalides (`fr-FR-AlainNeural`, `fr-FR-ClaudeNeural`). Génère des timings précis (`WordBoundary` avec repli `ffprobe`) et des sous-titres dynamiques ASS style TikTok/Reels (Safe-Zone `MarginL=60, MarginR=140, MarginV=440`, surbrillance dorée mot actif, nettoyage emojis `DejaVu Sans`).
3. **Générateur d'Images IA 100% Gratuit Bi-Fournisseur (`scripts/image_generator.py`) :**
   - **Fournisseur 1 :** Legacy `https://image.pollinations.ai/prompt/...` (`576×1024`, `nologo=true`, respect strict du quota `HTTP 402` + `Retry-After` 45s/IP ; sur un matrix 11 jobs GitHub Actions, chaque épisode dispose de sa propre IP publique).
   - **Fournisseur 2 :** **AI Horde anonyme** (`https://aihorde.net/api/v2/generate/async`, `apikey: 0000000000`, `384×640` portrait photoréaliste `ICBINP`/`Deliberate`/`Dreamshaper`/`AbsoluteReality`, zéro filigrane, ~9–25s) entrelacé avec Pollinations pour accélérer la production et garantir la résilience.
   - **Repli ultime :** Composite cinématographique PIL *Abidjan Twilight Noir* basé sur `assets/cover.jpg` uniquement si les deux fournisseurs gratuits échouent après retries sur une scène donnée (avec comptage `provider_stats` contrôlé par QA).
4. **Score Musical Afrogospel (`scripts/afrogospel_bgm.py`) :** Synthétiseur musical Python + FFmpeg (accords piano/Rhodes gospel, nappes chaudes, basse mélodique, percussions Afrogospel) décliné en 4 ambiances dramatiques (`twilight_tension`, `sanctuary_prayer`, `spiritual_warfare`, `victory_dawn`), remplaçant définitivement le bruit rose d'origine (`episodes/ep-001/audio/bgm_gospel.mp3` inclus).
5. **Moteur de Rendu Cinéma 2.5D FFmpeg (`scripts/render_episode.py`) :** Entrée image unique (`-i scene.jpg`, jamais `-loop 1` avant `zoompan`), suréchantillonnage 2× (`2160×3840`) + Ken Burns fluide `zoom>=1.08` (recadrage propre sans marque d'angle), 6 mouvements de caméra rotatifs, transitions `xfade` 0.45s, étalonnage *Abidjan Twilight Noir* (`eq`, `colorbalance`, `vignette`), sous-titres ASS incrustés + barre de progression dorée, ducking `sidechaincompress` + `loudnorm` `-16 LUFS`, sortie universelle H.264 `yuv420p` + AAC `+faststart` + poster JPG + contact sheet JPG + JSON métadonnées.
6. **QA Automatisée & Publication (`scripts/verify_episode.py`, `scripts/publish_manifest.py`, `.github/workflows/produce-season-cinema.yml`) :**
   - `permissions: contents: write` explicite.
   - Matrix 11 épisodes en parallèle (`max-parallel: 11`, `fail-fast: false`), vérification `ffprobe` + `volumedetect` + variance d'image + ratio réel IA/TTS avant upload.
   - Publication de tous les 11 `ep-001.mp4`..`ep-011.mp4` + posters + `videos-manifest.json` dans la GitHub Release stable **`episodes-v1`**, et commit `[skip ci]` de `videos-manifest.json` sur `main` pour diffusion same-origin sur GitHub Pages.
7. **Intégration PWA AMINA Experience (`js/data/episodes-data.js`, `js/player.js`, `js/app.js`, `css/player.css`, `sw.js`, `index.html`) :**
   - Champs additifs sur les 11 épisodes (`remoteVideoUrl`, `downloadUrl`, `hasRemoteVideo`, `hasBurnedSubtitles`, `poster`) préservant 100% `videoSrc`/`hasLocalVideo` et les tests existants.
   - Chargement optionnel same-origin `./videos-manifest.json`.
   - Contournement Service Worker (`sw.js` v2) pour requêtes cross-origin, `Range` (`206`) et `.mp4`.
   - `<video>` sans `crossorigin` (compatibilité redirection 302 GitHub Releases -> `objects.githubusercontent.com`), file de repli multi-sources (`remote` -> `local` -> carte motion hors-ligne avec bouton Réessayer), suppression des sous-titres HTML en doublon par défaut sur les vidéos incrustées (avec bouton `#btn-cc-toggle`), et bouton `"HD .mp4"` strictement conditionné à `isEpisodeUnlocked(ep.id)`.

## Option 3 Code Layout (Additions)
```text
/home/antigravity/digrekarlito11-eng/gospel-microdrama-studio/
├── videos-manifest.json                   # Manifeste same-origin publié par CI (11 épisodes, Release episodes-v1)
├── bible/
│   └── characters.json                    # Mis à jour avec 13 rôles et voix Edge-TTS gratuites vérifiées
├── scripts/
│   ├── storyboards.py                     # 11 storyboards complets (8-10 scènes + dialogues multi-personnages chacun)
│   ├── voice_engine.py                    # Moteur Edge-TTS multi-personnages + timing WordBoundary/ffprobe + ASS/SRT
│   ├── image_generator.py                 # Moteur IA gratuit bi-fournisseur (Pollinations + AI Horde) + repli PIL
│   ├── afrogospel_bgm.py                  # Générateur musical Afrogospel (4 ambiances, remplace le bruit rose)
│   ├── render_episode.py                  # Moteur Cinéma 2.5D FFmpeg 1080x1920@24fps + xfade + ASS + ducking + faststart
│   ├── verify_episode.py                  # Porte QA automatisée (ffprobe, audio, frames, stats IA/TTS)
│   └── publish_manifest.py                # Générateur de videos-manifest.json depuis les métadonnées vérifiées
├── .github/workflows/
│   ├── produce-season-cinema.yml          # Workflow principal 11-way matrix + Release episodes-v1 + Pages manifest
│   └── assemble-episode.yml               # Mis à jour / aligné avec le pipeline Option 3
└── tests/
    ├── unit/
    │   ├── releases-integration.test.js   # Tests unitaires contrat Release, manifeste, sw.js bypass, PWA gating
    │   └── test_pipeline.py               # Tests unitaires Python (storyboards, voix, ASS, BGM, image/QA)
    └── e2e/
        └── option3-cinema.spec.js         # Tests Playwright E2E Option 3 (streaming mocké, unlock->video, CC, offline fallback)
```

## Option 3 Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 14 | Canonical 11-Episode Storyboards & Free Voice Cast | 11 storyboards multi-scènes issus de `source/chapitre-01..11.md` + 13 rôles mappés sur voix Edge-TTS gratuites valides | M6 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 15 | Dual-Provider Free AI Scene Generator | Pollinations legacy (`1/45s/IP`) + AI Horde anonyme (`0000000000`) + repli PIL Abidjan Twilight Noir | M6 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 16 | Multi-Character French Edge-TTS & Dynamic ASS Captions | Synthèse vocale multi-personnages (`edge-tts>=7.3.1`), timing exact, sous-titres TikTok/Reels dorés Safe-Zone | M6 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 17 | Musical Afrogospel BGM & 2.5D FFmpeg Cinema Engine | Score Afrogospel musical + Ken Burns 2× supersampled + `xfade` + color grade + `sidechaincompress` + `+faststart` | M6 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 18 | PWA Streaming, SW Bypass, CC Guard & Gated HD Download | Intégration des 11 vidéos Release dans `episodes-data.js`/`player.js`/`app.js`/`sw.js` sans casser la monétisation ni les 65 tests | M7 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 19 | Option 3 Unit, Python & Playwright E2E Test Suite | Tests complets (Tiers 1–4) pour le pipeline Python, l'intégration PWA Release, SW bypass, CC toggle et repli hors-ligne | E2E-Opt3 | ORIGINAL_REQUEST (Follow-up) |
| 20 | Automated GitHub Actions 11-Episode Release Pipeline | Workflow `.github/workflows/produce-season-cinema.yml` (`permissions: contents: write`, matrix 11×, QA gate, Release `episodes-v1`, Pages manifest) | M6 / M8 | Survey & ORIGINAL_REQUEST (Follow-up) |
| 21 | Live Cloud Production & 11-Episode Delivery Verification | Push `main`, exécution réelle `gh workflow run`, 11 `.mp4` HD générés, vérifiés et publiés dans Release `episodes-v1` + PWA live | M8 / M9 | ORIGINAL_REQUEST (Follow-up) |

## Option 3 Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **M6** | Free 2.5D Motion-Cinema Pipeline & GHA Workflow | `bible/characters.json`, `scripts/*.py`, musical `bgm_gospel.mp3`, `.github/workflows/produce-season-cinema.yml`, `.github/workflows/assemble-episode.yml`, local dry-run smoke verification | M5 | PENDING_GATE |
| **M7** | PWA Release Video Integration & Streaming Hardening | `js/data/episodes-data.js`, `js/player.js`, `js/app.js`, `css/player.css`, `sw.js`, `index.html`, update `tests/e2e/amina-experience.spec.js` if needed | M5 | PENDING_GATE |
| **E2E-Opt3** | Option 3 Test Track (Python + JS Unit + Playwright E2E) | `tests/unit/releases-integration.test.js`, `tests/unit/test_pipeline.py`, `tests/e2e/option3-cinema.spec.js`, `TEST_INFRA.md`, `TEST_READY.md` | M6, M7 | IN_PROGRESS |
| **M8** | Live GitHub Actions Cloud Run & 11-Episode Release | Commit & push `main`, trigger & verify `produce-season-cinema.yml` on `ubuntu-latest`, confirm all 11 valid `.mp4` in Release `episodes-v1` + live `videos-manifest.json` on GitHub Pages | M6, M7, E2E-Opt3 | PLANNED |
| **M9** | Final Whole-Project Verification & Adversarial Audit | 100% unit + Python + E2E pass, live Release & Pages audit, 2 Reviewers + 2 Challengers + Whole-Project Forensic Auditor CLEAN | M8 | PLANNED |

## Option 3 Interface Contracts

### GitHub Release ↔ PWA (`episodes-data.js` & `videos-manifest.json`)
- **Release Tag:** `episodes-v1`
- **Release Base URL:** `https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1`
- **Asset Filenames:** `ep-001.mp4` .. `ep-011.mp4`, `ep-001_poster.jpg` .. `ep-011_poster.jpg`, `videos-manifest.json`
- **`videos-manifest.json` Schema (committed same-origin at repo root):**
```json
{
  "releaseTag": "episodes-v1",
  "releaseUrl": "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/tag/episodes-v1",
  "generatedAt": "2026-11-18T00:00:00Z",
  "episodes": {
    "ep-001": {
      "id": "ep-001",
      "videoUrl": "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1/ep-001.mp4",
      "downloadUrl": "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1/ep-001.mp4",
      "posterUrl": "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1/ep-001_poster.jpg",
      "duration": 78.4,
      "sizeBytes": 14500000,
      "resolution": "1080x1920",
      "hasBurnedSubtitles": true,
      "providers": { "pollinations": 4, "aihorde": 4, "fallback": 0 }
    }
  }
}
```
- **PWA Episode Object Additive Fields (`js/data/episodes-data.js`):**
  - Preserves existing `videoSrc`, `hasLocalVideo`, `tier`, `isFree`, `contactSheet`, `hasContactSheet`, `subtitles`.
  - Adds `remoteVideoUrl`, `downloadUrl`, `hasRemoteVideo: true`, `hasBurnedSubtitles: true`, `poster`.
- **Subtitle SRT Sync Rule:** `episodes/ep-001..011/subtitles.srt` MUST NOT be overwritten by the video pipeline (pipeline writes dynamic ASS/SRT inside `episodes/ep-XXX/output/`), preserving 100% compatibility with `tests/unit/subtitles.test.js`.

