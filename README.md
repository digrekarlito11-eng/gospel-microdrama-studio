# 🕊️ Gospel Microdrama Studio — Usine Cloud de Séries & Micro-Dramas Verticaux (9:16)

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Cloud%20Assembler%2024%2F7-success?logo=github)](#)
[![Format](https://img.shields.io/badge/Format-9%3A16%20Vertical%201080x1920-fe2c55)](#)
[![Style](https://img.shields.io/badge/Genre-Abidjan%20Gospel%20Noir%20%2F%20Micro--Drama-gold)](#)
[![Propriétaire](https://img.shields.io/badge/Studio%20Lead-Karl-brightgreen)](#)

> **Gospel Microdrama Studio** est un studio de production cinématographique et d'adaptation automatisée conçu dans **Antigravity** et hébergé sur le cloud de **GitHub**. Il transforme des manuscrits littéraires en micro-dramas verticaux à très forte rétention (TikTok, Instagram Reels, YouTube Shorts) tout en préservant l'intégrité et la puissance du message chrétien.

---

## 🏛️ Architecture du Dépôt

```text
gospel-microdrama-studio/
├── .github/
│   ├── copilot-instructions.md    # Charte du Showrunner & directives multi-agents
│   └── workflows/
│       └── assemble-episode.yml   # Workflow d'assemblage automatique FFmpeg
├── bible/
│   ├── characters.json            # Registre immuable des personnages (Ingredients IA vidéo)
│   ├── world-state.json           # Mémoire narrative et continuité des intrigues
│   └── visual-style.md            # Charte cinématographique 9:16 (Abidjan Twilight Noir)
├── source/
│   └── chapitre-01.md             # Manuscrit original : Chapitre 1 (L'Ombre du Maquis)
├── episodes/
│   └── ep-001/
│       ├── script.md              # Scénario découpé plan par plan (18 plans, 75 secondes)
│       ├── prompts-flow.txt       # Prompts prêts pour Google Flow, Kling, Runway
│       ├── prompts-suno.txt       # Prompts musicaux Suno AI (Tension & Gospel)
│       ├── subtitles.srt          # Fichier de sous-titres synchronisés Safe-Zone
│       ├── manifest.json          # Registre léger des clips vidéo et assets cloud
│       ├── audio/                 # Pistes vocales et musicales
│       ├── clips/                 # Rushs vidéo 9:16 (shot_01.mp4 à shot_18.mp4)
│       └── output/
│           ├── episode_001_master_9x16.mp4  # Master final vertical assemblé
│           └── contact_sheet.jpg            # Planche-contact de validation QA
└── scripts/
    ├── generate_tts_edge.py       # Synthèse vocale multi-personnages (Edge-TTS)
    └── build_episode.py           # Moteur FFmpeg d'assemblage et mixage
```

---

## ⚡ Cycle de Production en 4 Étapes

1. **Extraction de la Bible :** Antigravity analyse le chapitre déposé dans `source/` et met à jour `bible/characters.json` et `bible/world-state.json`.
2. **Découpage & Prompts :** Génération du script de micro-drama ultra-rythmé (Hook 0-3s, escalade, fermeté spirituelle, cliffhanger) avec les prompts vidéo (`prompts-flow.txt`) et musicaux (`prompts-suno.txt`).
3. **Synthèse Audio :** Exécution de `scripts/generate_tts_edge.py` pour générer les voix françaises avec les intonations distinctes de chaque personnage.
4. **Assemblage Master :** Exécution de `scripts/build_episode.py` (ou déclenchement automatique via GitHub Actions) pour assembler la vidéo, appliquer l'audio ducking, incruster les sous-titres Safe-Zone et générer la planche-contact.
