# E2E Test Infra: AMINA Experience PWA

## Test Philosophy
- Opaque-box, requirement-driven. Independent from implementation internals.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.
- Target Environment: Mobile browser emulation (iPhone 14 / WebKit, Pixel 7 / Chromium) and Desktop.

## Feature Inventory
| # | Feature | Source (Requirement) | Tier 1 (Happy Path) | Tier 2 (Boundaries) | Tier 3 (Cross-Feature) | Tier 4 (Real-World) |
|---|---------|----------------------|:-------------------:|:-------------------:|:----------------------:|:-------------------:|
| 1 | Mobile Shell & Navigation | ORIGINAL_REQUEST §1 | 5 | 5 | ✓ | ✓ |
| 2 | 9:16 Vertical Video Player & Gestures | ORIGINAL_REQUEST §2 | 5 | 5 | ✓ | ✓ |
| 3 | Safe-Zone Subtitles Display | ORIGINAL_REQUEST §2 & survey | 5 | 5 | ✓ | ✓ |
| 4 | Interactive E-Reader & Navigation | ORIGINAL_REQUEST §3 | 5 | 5 | ✓ | ✓ |
| 5 | E-Reader Font Sizing & 3 Themes | ORIGINAL_REQUEST §3 | 5 | 5 | ✓ | ✓ |
| 6 | Afrogospel Audio & Web Audio Fallback | ORIGINAL_REQUEST §3 | 5 | 5 | ✓ | ✓ |
| 7 | Freemium Rules (Ep 1-3 free, 4-11 locked) | ORIGINAL_REQUEST §4 | 5 | 5 | ✓ | ✓ |
| 8 | WhatsApp Share Unlock Flow | ORIGINAL_REQUEST §4 | 5 | 5 | ✓ | ✓ |
| 9 | Mobile Money CI Simulation Checkout | ORIGINAL_REQUEST §4 | 5 | 5 | ✓ | ✓ |
| 10 | WhatsApp Direct Book Order (+225 07 00 88 95 14) | ORIGINAL_REQUEST §4 | 5 | 5 | ✓ | ✓ |
| 11 | PWA Manifest & Service Worker Cache | ORIGINAL_REQUEST §5 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Unit Test Runner :** Node.js native test runner (`node --test tests/unit/*.test.js`).
- **E2E Test Runner :** Playwright (`npx playwright test`).
- **Pass/Fail Semantics :** Exit code 0, 100% assertions green, zero uncaught exceptions in console.
- **Directory Layout :**
  ```text
  tests/
  ├── unit/
  │   ├── state.test.js
  │   ├── subtitles.test.js
  │   └── monetization.test.js
  └── e2e/
      ├── amina-experience.spec.js
      └── mobile-interactions.spec.js
  ```

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | **Découverte Complète du Spectateur** : Arrivée sur l'app, visionnage ep 1, swipe vers ep 2 et 3, tentative ep 4 (blocage), déblocage via partage WhatsApp, lecture ep 4. | F1, F2, F3, F7, F8 | Élevée |
| 2 | **Parcours Fidélité & Paiement Mobile Money** : Choix du Pass Saison via Wave CI, simulation de paiement réussie, déblocage intégral de tous les épisodes et accès au roman. | F1, F7, F9, F11 | Élevée |
| 3 | **Immersion Nocturne du Lecteur** : Bascule vers la Liseuse, activation du thème Nuit, agrandissement de la police, activation de l'audio Afrogospel, navigation du Préambule au Chapitre 11. | F1, F4, F5, F6 | Élevée |
| 4 | **Achat Commercial du Livre Papier** : Consultation du Guide pratique, clic sur "Commander le livre dédicacé", vérification de l'ouverture du lien WhatsApp avec le numéro officiel `+225 07 00 88 95 14`. | F4, F10 | Moyenne |
| 5 | **Résilience & Hors-Ligne PWA** : Chargement de l'application, coupure simulée du réseau (offline), persistance des préférences et de l'état débloqué, vérification de l'activation du fallback audio. | F1, F5, F6, F11 | Élevée |

## Coverage Thresholds
- Tier 1: ≥5 per feature (55 tests)
- Tier 2: ≥5 per feature (55 tests)
- Tier 3: Pairwise combinations across major features (≥15 interaction tests)
- Tier 4: ≥5 realistic multi-step user scenarios
- **Total Minimum Test Cases : ~130 assertions/tests**
