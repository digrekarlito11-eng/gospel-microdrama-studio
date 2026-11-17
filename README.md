# 🕊️ AMINA : L'Autel De Yopougon — La Guerre Invisible

<div align="center">
  <img src="assets/cover.jpg" alt="Couverture Officielle — AMINA : L'Autel De Yopougon par Karl Digré" width="380" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />

  ### *Un roman chrétien puissant par Karl DIGRÉ*
  **Adapté en Usine Cloud de Micro-Dramas & Séries Verticales (9:16)**

  [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Cloud%20Production%2024%2F7-success?logo=github)](#)
  [![Format](https://img.shields.io/badge/Format-9%3A16%20Vertical%201080x1920-fe2c55)](#)
  [![Saison 1](https://img.shields.io/badge/Saison%201-11%20%C3%89pisodes%20Complets-gold)](#)
  [![Auteur](https://img.shields.io/badge/Auteur-Karl%20DIGR%C3%89-brightgreen)](#)
</div>

---

> *"Lorsque le juste refuse de se taire, qu'il prie par l'Esprit sans se laisser abattre et qu'il applique cette constance indéfectible (**hupopiazo**), il prive l'ennemi de tout repos, brise les trônes d'injustice et force les portes verrouillées à s'ouvrir."*  
> — **Karl DIGRÉ** (Inspiré des enseignements du pasteur Yvan Castanou, *La prière qui n'échoue jamais*)

---

## 📖 À Propos de l'Œuvre

Ancré dans les réalités urbaines et spirituelles d'Abidjan (**Yopougon, Rue Princesse, Siporex, maquis Le VIP**), ce roman raconte le combat sans merci d'**Amina**, jeune lycéenne de 17 ans dont la pureté et la foi inébranlable sont prises pour cibles par deux prédateurs :
* **Junior "Zagba" (23 ans) :** Le caïd arrogant des maquis, blessé dans son orgueil de rue.
* **M. Stéphane Koffi (45 ans) :** Le puissant homme d'affaires corrupteur, prédateur feutré opérant dans l'ombre d'une berline blindée.

Face à la calomnie, à l'expulsion, aux menaces physiques contre sa famille et à la maladie cardiaque de sa mère **Maman Hélène**, Amina active l'arme suprême : **l'autel de la prière persistante**.

---

## 🎬 La Série Complète en 11 Épisodes Verticaux (9:16)

Chaque chapitre du livre est découpé en un épisode de micro-drama ultra-rythmé de 60 à 75 secondes (format TikTok, Reels, YouTube Shorts) :

| # | Épisode | Thème & Enjeu Dramatique | Clé Spirituelle |
| :-: | :--- | :--- | :--- |
| **01** | [**L'Ombre du Maquis**](episodes/ep-001/) | Le pari de Zagba & la traque silencieuse de M. Koffi | La pureté face aux convoitises de la rue |
| **02** | [**Le Piège Doré**](episodes/ep-002/) | L'étal saccagé (300 000 F CFA) & la porte verrouillée chez Koffi | Refus de vendre son âme pour l'argent |
| **03** | [**Le Venin des Rumeurs**](episodes/ep-003/) | Évasion au candélabre & calomnie WhatsApp au lycée | La résistance face à la honte publique |
| **04** | [**Le Guet-apens de la Rue Princesse**](episodes/ep-004/) | Dette d'urgence à l'hôpital & traquenard nocturne de Zagba | La foi face à l'impossible |
| **05** | [**Le Sanctuaire de la Victoire**](episodes/ep-005/) | Pronostic vital engagé & activation de la prière en langues | Guérison miraculeuse & migraine de Koffi |
| **06** | [**Guerre dans l'Invisible**](episodes/ep-006/) | Frappes spirituelles continues privant l'ennemi de repos | Paranoïa & bagarre dans le camp de Zagba |
| **07** | [**La Contre-Attaque**](episodes/ep-007/) | Avis d'expulsion sous 48h & intimidation du petit frère Kévin | Sarah pousse au compromis, Amina s'enferme |
| **08** | [**Les 72 Heures de Feu**](episodes/ep-008/) | Jeûne et prière ininterrompus, épuisement physique | Les coups répétés d'usure (*hupopiazo*) |
| **09** | [**Le Piège de Minuit**](episodes/ep-009/) | Maman Hélène en cellule de police & tempête sur Abidjan | Marche résolue sous les éclairs |
| **10** | [**Le Choc des Rois**](episodes/ep-010/) | Face-à-face suprême dans le salon : *"Je ne négocie pas"* | Koffi terrassé par l'autorité spirituelle |
| **11** | [**L'Aube Nouvelle**](episodes/ep-011/) | Libération sans condition, repentance & triomphe | Restauration divine et paix éternelle |

---

## 🏛️ Architecture Technique du Studio

```text
gospel-microdrama-studio/
├── assets/
│   └── cover.jpg                  # Couverture officielle du roman
├── bible/
│   ├── characters.json            # Registre canonique & Prompts d'ancrage IA vidéo
│   ├── series-bible.md            # Bible complète de la saison en 11 épisodes
│   ├── world-state.json           # Mémoire narrative et continuité des intrigues
│   └── visual-style.md            # Charte cinématographique Abidjan Twilight Noir
├── source/
│   ├── livre-complet.md           # Manuscrit intégral de Karl DIGRÉ
│   ├── 00-preambule.md            # Dédicace, Préface & Introduction
│   ├── chapitre-01.md ... 11.md   # Les 11 chapitres individuels du livre
├── episodes/
│   ├── ep-001/ ... ep-011/        # 11 packages de production complets
│   │   ├── script.md              # Découpage plan par plan avec dialogues
│   │   ├── prompts-flow.txt       # Prompts vidéo Google Flow / Kling / Runway
│   │   ├── prompts-suno.txt       # Prompts musicaux Suno AI adaptés
│   │   ├── subtitles.srt          # Sous-titres Safe-Zone synchronisés
│   │   ├── manifest.json          # Registre des clips et timecodes
│   │   └── output/                # Master vidéo final & planche-contact QA
└── scripts/
    ├── generate_tts_edge.py       # Synthèse vocale multi-voix (Edge-TTS)
    └── build_episode.py           # Moteur FFmpeg d'assemblage et de mixage cloud
```

---

## ⚡ Commandes Rapides

### 1. Assembler un épisode précis en vidéo 9:16 :
```bash
python3 scripts/build_episode.py ep-001
python3 scripts/build_episode.py ep-005
```

### 2. Synthétiser les voix des personnages :
```bash
python3 scripts/generate_tts_edge.py
```

---

## 📞 Support Commercial & Édition
* **Auteur :** Karl DIGRÉ
* **Contact & Support Commercial :** `+225 07 00 88 95 14` (Abidjan, Côte d'Ivoire)
