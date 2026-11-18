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
