#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Storyboards Canoniques Saison 1 (ep-001 à ep-011)
Adapté fidèlement du roman « AMINA : L'Autel De Yopougon — La Guerre Invisible »
de Karl DIGRÉ (source/chapitre-01.md .. chapitre-11.md).

Chaque épisode comporte 8 à 10 scènes cinématographiques 9:16 dans la charte
« Abidjan Twilight Noir » (prompts visuels anglais cohérents, mouvements 2.5D,
dialogues multi-personnages français, humeur Afrogospel et BPM).
"""

from typing import Dict, List, Any

BOOK_CTA = "Commandez le roman : +225 07 00 88 95 14"

VALID_MOTIONS = (
    "zoom_in",
    "zoom_out",
    "pan_left",
    "pan_right",
    "push_in_dramatic",
    "tilt_up",
)

VALID_MOODS = (
    "twilight_tension",
    "sanctuary_prayer",
    "spiritual_warfare",
    "victory_dawn",
)

VALID_TRANSITIONS = ("fade", "dissolve", "smoothleft", "fadeblack")

# Style suffix appended or embedded across scenes for visual cohesion
STYLE_SUFFIX = (
    "Abidjan Twilight Noir aesthetic, warm amber gold rim light contrasting with deep midnight blue shadows, "
    "photorealistic African cinema 35mm film grain, dramatic depth of field, vertical 9:16 portrait framing, "
    "no text, no letters, no watermark, no logo"
)

# Consistent character visual anchors
ANCHOR_AMINA_UNIFORM = (
    "Amina, stunning 17-year-old Ivorian schoolgirl with radiant dark ebony skin, neat cornrow braids pulled back, "
    "calm resolute eyes, wearing pressed sky-blue school uniform shirt and navy skirt"
)
ANCHOR_AMINA_NIGHT = (
    "Amina, 17-year-old Ivorian girl with dark ebony skin and neat cornrow braids, determined luminous eyes, "
    "wearing a modest dark raincoat over simple home clothes"
)
ANCHOR_KOFFI = (
    "Stephane Koffi, imposing 45-year-old West African billionaire businessman with graying temples, short manicured beard, "
    "cold calculating gaze, wearing luxurious embroidered midnight-blue and gold bazin boubou and heavy gold watch"
)
ANCHOR_ZAGBA = (
    "Junior Zagba, athletic 23-year-old Ivorian street boss with razor-sharp fade haircut, thin mustache, arrogant smirk, "
    "wearing luxury streetwear jersey, thick gold chain, sunglasses on forehead"
)
ANCHOR_HELENE = (
    "Maman Helene, 48-year-old Ivorian mother with warm weathered loving face, wearing colorful traditional African wax pagne and matching headwrap"
)
ANCHOR_SARAH = (
    "Sarah, 17-year-old Ivorian high school girl in sky-blue uniform with anxious conflicted eyes, clutching a glowing smartphone"
)
ANCHOR_KEVIN = (
    "Kevin, 10-year-old Ivorian schoolboy in khaki school uniform carrying a worn backpack, innocent frightened eyes"
)


def _scene(
    scene_id: str,
    title: str,
    prompt_body: str,
    motion: str,
    transition: str,
    dialogue: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "scene_id": scene_id,
        "title": title,
        "prompt": f"{prompt_body}, {STYLE_SUFFIX}",
        "motion": motion,
        "transition": transition,
        "dialogue": dialogue,
    }


STORYBOARDS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # EPISODE 1 — Chapitre 1 : L'Ombre du Maquis
    # =========================================================================
    "ep-001": {
        "episode_id": "ep-001",
        "episode_number": 1,
        "title": "L'Ombre du Maquis — Le Pari et la Traque",
        "short_title": "EP. 1 • L'OMBRE DU MAQUIS",
        "hook": "À Yopougon, deux prédateurs ont déjà fixé son prix.",
        "cliffhanger": "TU N'AS NULLE PART OÙ TE CACHER. BIENTÔT, TU SERAS À MOI.",
        "cta": BOOK_CTA,
        "mood": "twilight_tension",
        "bpm": 128,
        "scenes": [
            _scene(
                "s01",
                "Crépuscule sur Yopougon",
                "Wide vertical establishing view of bustling Yopougon Rue Princesse in Abidjan at twilight, orange sunset haze, glowing neon maquis signs, red plastic tarps, passing gbakas buses and warm grill smoke rising into dark blue evening sky",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "À Yopougon, quand le crépuscule tombe, la nuit réveille les appétits les plus sombres.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s02",
                "La marche d'Amina",
                f"Medium vertical tracking portrait of {ANCHOR_AMINA_UNIFORM}, clutching her school backpack tightly as she walks calmly with dignity down a lively dusty Yopougon street bathed in golden sunset backlight",
                "pan_right",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Amina, dix-sept ans, élève modèle. Une grâce silencieuse que deux prédateurs observent déjà dans l'ombre.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s03",
                "Zagba au maquis Le VIP",
                f"Dynamic low-angle portrait of {ANCHOR_ZAGBA}, sitting on an overturned red beer crate outside Le VIP maquis in Siporex Yopougon surrounded by laughing street followers under flashing crimson and amber neon lights",
                "push_in_dramatic",
                "smoothleft",
                [
                    {
                        "speaker": "char_acolyte",
                        "text": "Même un regard elle ne te donne pas, Zagba ! Elle marche comme si notre sol allait salir ses chaussures.",
                        "pause_after": 0.3,
                    }
                ],
            ),
            _scene(
                "s04",
                "Le pari arrogant de Zagba",
                f"Intense close-up portrait of {ANCHOR_ZAGBA}, glaring with bruised pride and a predatory smirk as he adjusts his gold chain, warm neon reflections across his face in the Yopougon night",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "char_zagba",
                        "text": "Avant la fin de ce mois, cette fille marche à mes côtés. C'est un pari !",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_zagba",
                        "text": "Tout s'achète ou se brise, mon frère. Tout.",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s05",
                "La berline noire aux vitres teintées",
                "Sleek black luxury sedan parked silently in the shadows of a narrow Abidjan alley, tinted windows reflecting colorful street neon lights, cold ominous atmosphere of covert surveillance",
                "pan_left",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Mais à cinquante mètres de là, un chasseur bien plus redoutable observe dans le silence climatisé d'une berline noire.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "M. Stéphane Koffi dans l'ombre",
                f"Atmospheric interior car portrait of {ANCHOR_KOFFI}, sitting in the dark leather backseat as cold blue smartphone light illuminates his heavy gold watch and ruthless calm smile, chauffeur visible in the rearview mirror",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Vous êtes certain qu'elle rentre directement chez elle tous les soirs ?",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_chauffeur",
                        "text": "Oui Monsieur le Directeur. Lycée, marché pour aider sa mère, puis maison. Une rigueur absolue.",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_koffi",
                        "text": "Plus le fruit est haut sur l'arbre, plus la chute est spectaculaire. Trouvez ses faiblesses d'ici vendredi.",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s07",
                "La paix de la cour familiale",
                f"Warm intimate evening scene in a humble terracotta Abidjan family courtyard, {ANCHOR_HELENE} sitting on a low wooden stool sorting red peppers in a calabash as {ANCHOR_AMINA_UNIFORM} leans tenderly to kiss her mother's forehead under a soft warm bulb",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Maman, comment te sens-tu ce soir ? Ton cœur ne te fait pas mal ?",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_helene",
                        "text": "La grâce de Dieu me maintient debout, ma fille. Va te reposer.",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s08",
                "L'enveloppe kraft sous la porte",
                "Dramatic overhead close-up of a mysterious thick brown kraft envelope slipped halfway beneath a worn wooden bedroom door on a concrete floor in dim amber shadows, unsettling suspense",
                "push_in_dramatic",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Mais en ouvrant sa chambre, Amina s'immobilise. Glissée sous la porte : une enveloppe kraft contenant sa photo volée quelques minutes plus tôt.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s09",
                "La menace au dos de la photo",
                f"Chilling dramatic close-up of {ANCHOR_AMINA_UNIFORM} in her dimly lit bedroom staring in frozen shock at a glossy photograph in her trembling hands, harsh cold blue light mixing with dim overhead tungsten bulb",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Tu n'as nulle part où te cacher. Bientôt, tu seras à moi.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 2 — Chapitre 2 : Le Piège Doré (Canon Chapitre 2!)
    # =========================================================================
    "ep-002": {
        "episode_id": "ep-002",
        "episode_number": 2,
        "title": "Le Piège Doré — L'Étal Saccagé et la Cage de Luxe",
        "short_title": "EP. 2 • LE PIÈGE DORÉ",
        "hook": "Un étal saccagé... 300 000 francs pour sauver sa mère.",
        "cliffhanger": "Le verrou automatique claque : Vous êtes chez moi maintenant.",
        "cta": BOOK_CTA,
        "mood": "twilight_tension",
        "bpm": 80,
        "scenes": [
            _scene(
                "s01",
                "L'assaut au marché de Yopougon",
                "Chaotic dramatic scene at a crowded Abidjan market stall in Yopougon, overturned crates of bright red tomatoes and spices scattered across dusty ground, municipal enforcement officers intimidating vendors while a suited emissary watches coldly from the background",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Dès le lendemain matin, le piège se referme sur le grand marché de Yopougon. L'étal de Maman Hélène est brutalement saccagé.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "Maman Hélène s'effondre",
                f"Emotional dramatic portrait of {ANCHOR_HELENE} clutching her chest in acute pain as she collapses beside scattered market produce while {ANCHOR_AMINA_UNIFORM} rushes desperately to catch her amidst blurred market chaos",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "char_helene",
                        "text": "Non ! Je vous en supplie, c'est tout ce que j'ai pour nourrir mes enfants !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s03",
                "Le verdict des urgences",
                "Dim sterile emergency room corridor in an Abidjan neighborhood hospital, serious 44-year-old Ivorian doctor in white coat with stethoscope speaking gravely to a devastated teenage girl seated on a plastic chair under cold fluorescent light",
                "pan_right",
                "fadeblack",
                [
                    {
                        "speaker": "char_medecin",
                        "text": "Votre mère a frôlé l'infarctus, mademoiselle. Sans trois cent mille francs avant ce soir, c'est la saisie définitive.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s04",
                "Sarah apporte la fausse délivrance",
                f"Medium vertical shot in the blue-lit hospital hallway of {ANCHOR_SARAH} rushing breathless toward {ANCHOR_AMINA_UNIFORM}, speaking urgently with nervous excitement while glancing toward the street outside",
                "zoom_in",
                "smoothleft",
                [
                    {
                        "speaker": "char_sarah",
                        "text": "Amina ! Quelqu'un a déjà payé toute la dette à la mairie ! Ta mère est sauvée !",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_amina",
                        "text": "Qui... Qui a fait ça, Sarah ?",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_sarah",
                        "text": "Monsieur Koffi. Il t'attend dans sa voiture, il veut juste que tu le remercies en personne. Ne fais pas la têtue !",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s05",
                "Le choix cornélien d'Amina",
                f"Poignant quiet hospital room shot of {ANCHOR_HELENE} sleeping weakly under an IV drip while {ANCHOR_AMINA_UNIFORM} looks at her mother with tears of fierce resolve in her eyes, warm bedside lamp versus deep blue twilight",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Je vais y aller.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s06",
                "La prison dorée",
                "Imposing luxury modern villa fortress in an upscale Abidjan neighborhood at dusk, towering concrete walls topped with electric razor wire, sleek black sedan entering heavy iron gates under cold architectural spotlights",
                "tilt_up",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Quinze minutes plus tard, la berline noire franchit les murs barbelés d'une résidence luxueuse : une véritable cage dorée.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s07",
                "Face au prédateur dans le salon",
                f"Vast cold minimalist luxury mansion living room at night, {ANCHOR_KOFFI} stepping slowly out of the shadows holding a crystal whisky glass, predatory triumphant smile beneath warm ceiling spotlights",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Dans la vie, Amina, tout se paye. Et ce que je veux, ce n'est pas votre argent.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "Le refus d'acier",
                f"Defiant vertical close-up of {ANCHOR_AMINA_UNIFORM} stepping back in the grand shadowy salon, her eyes burning with steel courage and refusal to bow, golden rim light framing her silhouette",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Je vous ai dit merci, Monsieur. Maintenant, je rentre chez moi.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s09",
                "Le verrou automatique claque",
                "Tense macro close-up of a young African woman's hand desperately pulling a heavy brass luxury mansion door handle while a red electronic security lock indicator glows shut, ominous shadow looming behind her",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Un clic métallique glacial retentit. La porte blindée vient de se verrouiller de l'extérieur.",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_koffi",
                        "text": "Personne ne sort d'ici avant d'avoir compris les règles du jeu. Vous êtes chez moi maintenant.",
                        "pause_after": 0.5,
                    },
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 3 — Chapitre 3 : Le Venin des Rumeurs
    # =========================================================================
    "ep-003": {
        "episode_id": "ep-003",
        "episode_number": 3,
        "title": "Le Venin des Rumeurs — L'Évasion et la Calomnie Virale",
        "short_title": "EP. 3 • LE VENIN DES RUMEURS",
        "hook": "Elle fracasse la table en verre et déclenche l'alarme incendie !",
        "cliffhanger": "Maman Hélène lit les calomnies et s'effondre inerte au sol !",
        "cta": BOOK_CTA,
        "mood": "spiritual_warfare",
        "bpm": 135,
        "scenes": [
            _scene(
                "s01",
                "L'éclat de survie",
                f"Explosive high-action cinematic shot inside a dark luxury living room, {ANCHOR_AMINA_UNIFORM} swinging a heavy bronze candelabra shattering a glass coffee table in a burst of sparkling shards as {ANCHOR_KOFFI} recoils in stunned shock",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Ne rends pas les choses plus difficiles, Amina...",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "narrator",
                        "text": "Mais d'un geste fulgurant, Amina saisit un lourd candélabre de bronze et pulvérise la table en verre !",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s02",
                "L'alarme incendie rouge",
                f"Intense kinetic shot of {ANCHOR_AMINA_UNIFORM} slamming a red emergency fire-alarm button on a sleek mansion wall as pulsing crimson strobe lights flood the dark modern villa corridor",
                "zoom_in",
                "smoothleft",
                [
                    {
                        "speaker": "narrator",
                        "text": "Elle écrase le bouton rouge d'alarme incendie. Les sirènes hurlent, les gyrophares inondent la villa !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s03",
                "La fuite dans la nuit",
                f"Breathless night escape scene of {ANCHOR_AMINA_UNIFORM} leaping over a half-open wrought-iron service gate surrounded by tropical garden foliage onto a rain-slicked Abidjan highway illuminated by passing headlights",
                "pan_right",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Avant l'arrivée des gardes, elle force l'issue de secours, escalade le portail et s'échappe de cet enfer doré.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s04",
                "L'ouragan au lycée",
                f"Tense wide-to-medium shot of a crowded Ivorian high school courtyard in Yopougon, {ANCHOR_AMINA_UNIFORM} walking alone down the center while dozens of students whisper behind their hands staring at glowing smartphone screens",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Le lendemain matin, la vengeance de Koffi frappe le lycée avec la violence d'une tempête.",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_eleve",
                        "text": "C'est elle ? Regarde sur le groupe WhatsApp du quartier, les photos devant la villa...",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s05",
                "Les photos truquées virales",
                "Dramatic close-up over a teenage girl's shoulder looking at a glowing smartphone screen in harsh daylight surrounded by mocking silhouettes, emotional shock and betrayal reflected in her eyes",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Des clichés soigneusement trafiqués à la sortie de la résidence. En quelques heures, sa réputation est assassinée dans tout Yopougon.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "Le sourire de Zagba et le silence de Sarah",
                f"Split tension portrait across a sunlit schoolyard wall: {ANCHOR_ZAGBA} leaning smugly with a cruel triumphant grin while {ANCHOR_SARAH} looks away in guilty shame unable to defend her friend",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Même toi, Sarah... tu ne dis rien ? Qu'ils parlent. Je ne baisserai pas la tête.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s07",
                "L'attroupement devant le portail",
                "Alarming late-afternoon scene outside a rusty corrugated-iron courtyard gate in Yopougon, panicked African neighbors gathered around the wide-open doorway while a teenage schoolgirl sprints homeward in dread",
                "zoom_in",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Mais le pire l'attend devant la cour familiale. La porte est grande ouverte. Un cri déchire l'intérieur.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "Maman Hélène inerte au sol",
                f"Heartbreaking cinematic shot inside a humble dim living room, {ANCHOR_HELENE} lying unconscious on the clay-tiled floor with crumpled printed gossip flyers scattered beside her as a tearful neighbor woman kneels holding a phone",
                "tilt_up",
                "dissolve",
                [
                    {
                        "speaker": "char_voisine",
                        "text": "Amina ! Quelqu'un a distribué ces tracts mensongers partout au marché ! En les lisant, ta mère a fait une crise fulgurante !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s09",
                "Le cri de douleur d'Amina",
                f"Devastating close-up of {ANCHOR_AMINA_UNIFORM} kneeling on the floor cradling her unconscious mother's head in trembling hands, deep twilight blue shadows and a single warm ray of light cutting through the doorway",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Maman ! Tiens bon, Maman, je suis là !",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "narrator",
                        "text": "Ses ennemis viennent de frapper là où son cœur saigne le plus.",
                        "pause_after": 0.5,
                    },
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 4 — Chapitre 4 : Le Guet-apens de la Rue Princesse
    # =========================================================================
    "ep-004": {
        "episode_id": "ep-004",
        "episode_number": 4,
        "title": "Le Guet-apens de la Rue Princesse — Le Rendez-vous Nocturne",
        "short_title": "EP. 4 • LE GUET-APENS",
        "hook": "200 000 francs avant demain matin, ou les soins s'arrêtent...",
        "cliffhanger": "Encerclée par Zagba dans la ruelle : un fracas déchire la nuit !",
        "cta": BOOK_CTA,
        "mood": "twilight_tension",
        "bpm": 130,
        "scenes": [
            _scene(
                "s01",
                "Le moniteur cardiaque aux urgences",
                f"Somber hospital ward at night, glowing green cardiac monitor casting eerie reflections across {ANCHOR_HELENE} lying unconscious in bed while {ANCHOR_AMINA_UNIFORM} grips her mother's cold hand in silent anguish",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Dans la chambre stérile des urgences, le bip du moniteur cardiaque résonne comme une bombe à retardement.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "L'ultimatum médical",
                "Serious Ivorian emergency doctor in white coat standing beside a dimly lit hospital bed holding medical charts, delivering devastating news under harsh blue overhead light",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "char_medecin",
                        "text": "Les médicaments d'urgence coûtent deux cent mille francs. Sans versement avant demain matin, nous devrons suspendre les soins intensifs.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s03",
                "Le SMS du numéro masqué",
                "Dramatic dark close-up of a glowing smartphone vibrating on a bedside hospital table at 8 PM, casting cold electric light on Amina's tense face in the dark room",
                "push_in_dramatic",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Vingt heures passées. Un numéro masqué lui envoie un ultimatum : viens seule derrière la Rue Princesse à vingt-et-une heures, ou ta mère meurt ce soir.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s04",
                "Dans le ventre de la Rue Princesse",
                f"Atmospheric nocturnal wide shot of {ANCHOR_AMINA_NIGHT} walking with a dark scarf over her shoulders through the electric neon glow, grill smoke, and vibrant crowds of Abidjan's Rue Princesse at night",
                "pan_right",
                "smoothleft",
                [
                    {
                        "speaker": "narrator",
                        "text": "Elle sait que c'est un traquenard. Mais entre la peur et la vie de sa mère, Amina fonce dans la nuit de Yopougon.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s05",
                "L'entrepôt désaffecté",
                f"Eerie noir alley behind abandoned concrete warehouses in Yopougon, a single flickering broken streetlamp illuminating {ANCHOR_AMINA_NIGHT} standing alone on dusty ground surrounded by deep ominous shadows",
                "zoom_out",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Il n'y a personne ? Je suis là ! Montrez-vous !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "Zagba surgit des ténèbres",
                f"Menacing low-angle shot of three dark silhouettes stepping out from cracked warehouse pillars, {ANCHOR_ZAGBA} striding forward at the center with hands in his pockets and a cruel mocking grin under flickering amber streetlight",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "char_zagba",
                        "text": "Je savais que tu viendrais, Amina. Les filles fières finissent toujours par plier le genou quand la réalité les rattrape.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s07",
                "Acculée contre le béton",
                f"Tense close-up of {ANCHOR_AMINA_NIGHT} backed up against a rough cold concrete wall, fists clenched tightly, fearless fire flashing in her dark eyes under moody twilight noir shadows",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "C'est toi qui as envoyé ce message ? Où est l'argent pour ma mère ?",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_zagba",
                        "text": "Tu effaces ton arrogance, et ta mère aura ses médicaments. Sinon, la nuit sera très longue pour elle.",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s08",
                "Un regard vers le ciel",
                f"Poignant cinematic tilt-up of {ANCHOR_AMINA_NIGHT} trapped by dark menacing shadows in the narrow alley, tears glistening as she raises her gaze toward the stormy midnight sky of Abidjan",
                "tilt_up",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Aucune issue. Seule face à la malice de la rue, Amina lève les yeux vers le ciel nocturne d'Abidjan.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s09",
                "Le fracas qui déchire la nuit",
                "Sudden dramatic flash of golden-white light bursting down the dark alleyway, shattered glass sparks and startled silhouettes of street thugs whipping their heads around in shock, high-contrast noir suspense",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Soudain, un fracas métallique strident déchire la nuit et fait sursauter Zagba et ses complices !",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 5 — Chapitre 5 : Le Sanctuaire de la Victoire
    # =========================================================================
    "ep-005": {
        "episode_id": "ep-005",
        "episode_number": 5,
        "title": "Le Sanctuaire de la Victoire — L'Autel de Prière Persistante",
        "short_title": "EP. 5 • LE SANCTUAIRE",
        "hook": "Le cœur de sa mère chute... Les médecins abandonnent avant minuit.",
        "cliffhanger": "À 3h du matin : guérison miraculeuse ! Koffi est frappé dans sa villa.",
        "cta": BOOK_CTA,
        "mood": "sanctuary_prayer",
        "bpm": 90,
        "scenes": [
            _scene(
                "s01",
                "La course vers l'hôpital",
                f"Dynamic motion shot of {ANCHOR_AMINA_NIGHT} sprinting fiercely down a dark Yopougon street away from the startled thugs behind her, streetlights streaking into golden bokeh trails",
                "pan_right",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Profitant de cette seconde d'inattention, Amina s'arrache au guet-apens et court à perdre haleine vers l'hôpital.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "La chute critique",
                "Tense emergency room interior, erratic red warning waves pulsing on a medical heart monitor beside Maman Helene while the grave Ivorian doctor shakes his head grimly",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "char_medecin",
                        "text": "Mademoiselle, la tension de votre mère chute à vue d'œil. Sans versement immédiat, nous ne pourrons pas la maintenir au-delà de minuit.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s03",
                "À genoux au pied du lit",
                f"Sacred emotional portrait of {ANCHOR_AMINA_NIGHT} dropping to her knees beside the hospital bed, hands clasped tightly over her worn Bible as a radiant warm golden shaft of spiritual light breaks through the dark room",
                "zoom_in",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Alors, au fond de l'abîme, une révélation foudroyante embrase le cœur d'Amina : ce combat ne se gagne pas par la chair, mais sur l'autel de la prière persistante.",
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "char_amina",
                        "text": "Seigneur, je refuse de céder ! Je ne laisserai aucun repos à l'ennemi cette nuit !",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s04",
                "L'arme d'Hupopiazo",
                f"Transcendent cinematic shot of {ANCHOR_AMINA_NIGHT} praying fervently with closed eyes and tears shining like gold, glowing ethereal amber sparks rising gently around her silhouette in the midnight blue room",
                "tilt_up",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Par l'Esprit, chaque prière proclamée sans relâche devient une frappe céleste — hupopiazo — brisant les forteresses invisibles dressées contre sa mère.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s05",
                "La migraine foudroyante de Koffi",
                f"Dramatic high-contrast shot inside a luxurious dark mansion bedroom, {ANCHOR_KOFFI} jolting upright drenched in cold sweat, clutching his temples in sudden agonizing migraine and unexplained panic",
                "push_in_dramatic",
                "smoothleft",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Qu'est-ce qui m'arrive... Cette douleur... Je n'arrive plus à respirer !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "Panique dans le camp de Zagba",
                f"Chaotic nighttime Yopougon street scene where {ANCHOR_ZAGBA} and his street accomplices argue violently in sudden irrational terror under flickering neon lights, haunted by an unseen spiritual pressure",
                "pan_left",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Au même instant, la panique frappe les deux camps ennemis : insomnie chez Koffi, terreur et discorde chez Zagba. L'adversaire perd tout repos !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s07",
                "Trois heures du matin — La paix royale",
                "Serene glowing hospital room at 3 AM, the cardiac monitor displaying a steady calm green heartbeat waveform as peaceful golden dawn light softly illuminates Maman Helene resting soundly",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "À trois heures du matin, un calme majestueux envahit la chambre. Sur le moniteur, le cœur de Maman Hélène bat de nouveau avec force.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "La stupeur du médecin",
                "Close-up of the 44-year-old Ivorian emergency doctor wiping his glasses in utter astonishment as he compares the medical chart with the stabilized patient monitor",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "char_medecin",
                        "text": "C'est inexplicable... Sa tension est revenue à la normale d'elle-même. Elle est totalement hors de danger !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s09",
                "Larmes de triomphe",
                f"Radiant uplifting portrait of {ANCHOR_AMINA_NIGHT} lifting her tear-streaked smiling face bathed in warm golden sanctuary light beside her sleeping mother",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Lorsque le juste refuse de se taire, les verrous les plus sombres finissent par sauter.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 6 — Chapitre 6 : Guerre dans l'Invisible
    # =========================================================================
    "ep-006": {
        "episode_id": "ep-006",
        "episode_number": 6,
        "title": "Guerre dans l'Invisible — La Panique des Ténèbres",
        "short_title": "EP. 6 • GUERRE INVISIBLE",
        "hook": "À genoux sur le béton : chaque prière frappe l'invisible.",
        "cliffhanger": "Bagarre au maquis, Koffi au bord de la folie jure sa vengeance ultime.",
        "cta": BOOK_CTA,
        "mood": "spiritual_warfare",
        "bpm": 85,
        "scenes": [
            _scene(
                "s01",
                "L'autel sur le béton brut",
                f"Intense spiritual portrait inside a humble locked Yopougon bedroom at night, {ANCHOR_AMINA_NIGHT} kneeling on raw concrete with iron determination, no longer weeping, bathed in a fierce vertical beam of warm amber light",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "La nuit à Abidjan est devenue un champ de bataille invisible. Enfermée dans sa chambre, Amina ne pleure plus : elle frappe le mal à sa racine.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "Les frappes chirurgicales de l'Esprit",
                f"Symbolic dramatic close-up of {ANCHOR_AMINA_NIGHT} whispering fervent prayers over an open Bible as subtle golden shockwaves of light ripple outward through deep midnight-blue mist",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Aucun complot forgé dans les ténèbres ne tiendra contre la lumière de Dieu !",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s03",
                "Koffi arraché au sommeil",
                f"Dark atmospheric master suite in an upscale Abidjan villa, {ANCHOR_KOFFI} stumbling out of bed soaked in cold sweat, gripping his head as if struck by invisible hammer blows, stormy shadows looming across luxury walls",
                "pan_left",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "À des kilomètres de là, dans sa villa climatisée, Monsieur Koffi est arraché au sommeil par une terreur suffocante.",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_koffi",
                        "text": "Qu'est-ce que... Pourquoi cette maison m'étouffe ?! Ouvrez les fenêtres !",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s04",
                "L'insomnie qui ronge l'oligarque",
                f"Restless vertical shot of {ANCHOR_KOFFI} pacing wildly across dark marble floors holding a glass of ice water with shaking hands, exhausted dark circles under his haunted eyes",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "L'ennemi harcelé par la prière incessante perd pied et transmet sa panique à ses propres serviteurs.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s05",
                "Tension au maquis de Zagba",
                f"Moody smoky interior of a dim Yopougon maquis bar by a green pool table, {ANCHOR_ZAGBA} sweating profusely with bloodshot eyes while his nervous street lieutenants glare angrily at each other",
                "pan_right",
                "smoothleft",
                [
                    {
                        "speaker": "char_acolyte",
                        "text": "C'est ta faute si on s'est plantés l'autre soir ! Tu nous as tous vendus !",
                        "pause_after": 0.3,
                    }
                ],
            ),
            _scene(
                "s06",
                "L'implosion de la bande",
                "Explosive chaotic bar fight inside a dark neon-lit Yopougon maquis, overturned plastic chairs, flying shadows and panicked gang members turning on each other while Zagba watches helplessly as his empire cracks",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_zagba",
                        "text": "Arrêtez ! Vous êtes devenus fous ou quoi ?! Arrêtez ça !",
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "narrator",
                        "text": "En quelques secondes, la paranoïa fait voler en éclats toute l'autorité de Zagba !",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s07",
                "Quatre heures du matin — Le ciel nettoyé",
                f"Peaceful radiant shot of {ANCHOR_AMINA_NIGHT} exhaling serenely on her knees in her small room as soft golden pre-dawn light fills the window, invincible royal peace on her face",
                "tilt_up",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "À quatre heures du matin, une paix royale descend sur Amina. Le ciel spirituel de sa vie vient d'être nettoyé.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "La fureur glaciale de Koffi",
                f"Chilling tight close-up of {ANCHOR_KOFFI} staring with veins bulging and venomous hatred at his glowing smartphone screen in the pitch-black villa before dawn",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Mais au bord de la folie, Stéphane Koffi saisit son téléphone. Puisque l'argent a échoué, il déclenche l'asphyxie totale.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 7 — Chapitre 7 : La Contre-Attaque
    # =========================================================================
    "ep-007": {
        "episode_id": "ep-007",
        "episode_number": 7,
        "title": "La Contre-Attaque — Le Compte à Rebours de 48 Heures",
        "short_title": "EP. 7 • LA CONTRE-ATTAQUE",
        "hook": "Expulsion sous 48h ! Son petit frère Kévin menacé dans la rue !",
        "cliffhanger": "Sarah supplie de capituler. Amina verrouille sa porte : guerre totale.",
        "cta": BOOK_CTA,
        "mood": "twilight_tension",
        "bpm": 100,
        "scenes": [
            _scene(
                "s01",
                "Le soleil de plomb sur Yopougon",
                f"Harsh midday Abidjan sunlight over corrugated iron roofs in Yopougon, {ANCHOR_AMINA_UNIFORM} gently helping her still-weak mother {ANCHOR_HELENE} back home toward their courtyard gate",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "À peine Maman Hélène est-elle rentrée de l'hôpital que la contre-attaque brutale de Koffi s'abat sur la cour.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "Le propriétaire corrompu",
                "Aggressive heavy-set 52-year-old West African landlord with thick glasses flanked by two muscular thugs outside a rusty courtyard gate, furiously waving official eviction papers in front of shocked neighbors",
                "push_in_dramatic",
                "smoothleft",
                [
                    {
                        "speaker": "char_proprietaire",
                        "text": "C'est fini ! Vous libérez cette maison dans quarante-huit heures ! Le contrat est rompu, sortez d'ici !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s03",
                "L'asphyxie financière",
                f"Emotional medium shot of {ANCHOR_AMINA_UNIFORM} catching her staggering mother {ANCHOR_HELENE} in her arms while locking eyes coldly with the corrupt landlord, realizing Koffi's hidden hand",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Amina reconnaît aussitôt la griffe de Monsieur Koffi : l'asphyxie totale pour les jeter à la rue.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s04",
                "Kévin intercepté à la tombée du soir",
                f"Ominous dusk street corner in Yopougon, {ANCHOR_KEVIN} frozen in fear as two intimidating dark-jacketed enforcers tower over him casting long menacing shadows across the dusty lane",
                "zoom_in",
                "fadeblack",
                [
                    {
                        "speaker": "char_homme_main",
                        "text": "Dis à ta sœur qu'au prochain coucher de soleil, c'est votre expulsion définitive... et bien pire encore si elle s'obstine.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s05",
                "Les larmes du petit frère",
                f"Tender heartbreaking scene in the dimly lit courtyard of {ANCHOR_KEVIN} trembling in tears clinging to {ANCHOR_AMINA_UNIFORM} as she wraps her protective arms around him",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "char_kevin",
                        "text": "Amina... ils ont dit qu'ils allaient nous faire du mal si tu n'obéis pas...",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "La supplique terrifiée de Sarah",
                f"Intense claustrophobic interior shot of {ANCHOR_SARAH} rushing in with red tearful eyes, grabbing {ANCHOR_AMINA_UNIFORM}'s hands desperately under a dim amber bulb",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_sarah",
                        "text": "Amina, tu es folle ! On ne gagne pas contre des hommes comme Koffi ! Va lui demander pardon, c'est le seul moyen de sauver ta famille !",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s07",
                "Un silence de cathédrale",
                f"Powerful still portrait of {ANCHOR_AMINA_UNIFORM} calmly freeing her hands from her fearful friend, her face serene and burning with unshakable spiritual authority in the golden-blue shadows",
                "tilt_up",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "S'il pense pouvoir nous écraser, c'est qu'il ignore qui combat à nos côtés.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s08",
                "Le verrou de la guerre totale",
                "Dramatic close-up of Amina's firm hand sliding a heavy iron deadbolt lock shut on her wooden bedroom door, turning away from fear toward her open Bible on the floor",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Quarante-huit heures au compteur. Amina tire les verrous à double tour. La bataille décisive commence.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 8 — Chapitre 8 : Les 72 Heures de Feu
    # =========================================================================
    "ep-008": {
        "episode_id": "ep-008",
        "episode_number": 8,
        "title": "Les 72 Heures de Feu — Le Combat d'Usure Spirituel",
        "short_title": "EP. 8 • 72 HEURES DE FEU",
        "hook": "Trois jours sans manger, à genoux devant l'Éternel.",
        "cliffhanger": "À la 70e heure, Amina s'effondre d'épuisement, le front sur sa Bible !",
        "cta": BOOK_CTA,
        "mood": "sanctuary_prayer",
        "bpm": 70,
        "scenes": [
            _scene(
                "s01",
                "Le serment sans retour",
                f"Reverent vertical shot of {ANCHOR_AMINA_NIGHT} kneeling alone on the cold floor of her small locked room in Yopougon, open worn Bible resting before her under warm golden candlelight",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Seigneur, je m'engage pour un combat sans retour. Je ne sortirai pas d'ici sans ta victoire.",
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "narrator",
                        "text": "Ainsi débutèrent les soixante-douze heures de feu.",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s02",
                "Premières 24 heures — L'air électrique",
                f"Atmospheric moody shot of {ANCHOR_AMINA_NIGHT} fighting waves of crushing physical fatigue and dizziness in her dim room, sweating slightly yet lifting her chin in fierce spiritual persistence",
                "pan_right",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Les premières vingt-quatre heures, l'air devient électrique. Fatigue, vertiges, oppression : tout tente de la faire taire.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s03",
                "Le marteau-pilon dans l'invisible",
                "Epic symbolic Abidjan Twilight Noir sky above Yopougon rooftops, dramatic golden shafts of light piercing dark brooding storm clouds like celestial lightning shattering invisible chains",
                "tilt_up",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "Mais chaque parole proclamée par l'Esprit frappe comme un marteau-pilon les forteresses qui téléguident ses ennemis.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s04",
                "Le lion en cage",
                f"Tense dramatic shot inside a sleek dark marble executive office, {ANCHOR_KOFFI} pacing furiously like a caged predator, eyes sunken from days of insomnia, frightened staff backing out the doorway",
                "push_in_dramatic",
                "smoothleft",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Sortez tous ! Laissez-moi ! Pourquoi personne n'arrive à briser une simple lycéenne ?!",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s05",
                "Deuxième jour — L'autel qui brûle",
                f"Intimate emotional close-up of {ANCHOR_AMINA_NIGHT} with bruised knees and parched lips, refusing food or rest as she maintains her unbroken whispered prayer through the deep Abidjan night",
                "zoom_in",
                "dissolve",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Tu es mon refuge et ma forteresse, ô Éternel... Même si mon corps fléchit, mon esprit ne se taira pas.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s06",
                "La soixante-dixième heure",
                f"Heart-stopping dramatic portrait of {ANCHOR_AMINA_NIGHT} swaying from total physical exhaustion in the predawn darkness, eyelids heavy as lead, still gripping the edges of her open Bible",
                "zoom_out",
                "fadeblack",
                [
                    {
                        "speaker": "narrator",
                        "text": "À la soixante-dixième heure, une fatigue cataclysmique submerge son corps à bout de forces.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s07",
                "L'effondrement sur la Bible",
                f"Poignant quiet vertical shot of {ANCHOR_AMINA_NIGHT} collapsed unconscious on the bare floor of her bedroom, her forehead resting peacefully upon the open pages of her Bible bathed in soft silver-gold moonlight",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Amina s'évanouit d'épuisement à même le sol, le front posé sur sa Bible ouverte.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s08",
                "La victoire déjà scellée",
                "Glowing close-up of an open Bible illuminated by warm golden light radiating softly into deep midnight-blue shadows, sense of completed invisible triumph",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Son corps cède... mais dans l'invisible, l'ennemi est déjà à genoux. La victoire est scellée.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 9 — Chapitre 9 : Le Piège de Minuit
    # =========================================================================
    "ep-009": {
        "episode_id": "ep-009",
        "episode_number": 9,
        "title": "Le Piège de Minuit — La Tempête et la Garde à Vue",
        "short_title": "EP. 9 • LE PIÈGE DE MINUIT",
        "hook": "Maman Hélène jetée en cellule policière sur de fausses accusations !",
        "cliffhanger": "Minuit moins dix sous le déluge : Amina marche droit vers la villa.",
        "cta": BOOK_CTA,
        "mood": "spiritual_warfare",
        "bpm": 120,
        "scenes": [
            _scene(
                "s01",
                "Le réveil souverain",
                f"Striking dramatic shot of {ANCHOR_AMINA_NIGHT} slowly lifting her forehead from her open Bible, eyes shining with serene superhuman clarity as a fresh spiritual strength fills her frame",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Quand Amina émerge de son évanouissement, un calme souverain habite son regard : le silence qui précède l'orage décisif.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "Coups violents à la porte",
                "Urgent nighttime courtyard scene in Yopougon, a distressed 42-year-old Ivorian neighbor woman pounding frantically on a wooden door clutching a crumpled official summons paper as distant lightning flashes",
                "push_in_dramatic",
                "smoothleft",
                [
                    {
                        "speaker": "char_voisine",
                        "text": "Amina ! Ouvre vite ! Des policiers viennent d'emmener ta mère au poste central !",
                        "pause_after": 0.3,
                    }
                ],
            ),
            _scene(
                "s03",
                "Les fausses accusations",
                f"Dramatic two-shot at the doorway bathed in cold storm lightning and warm house bulb, {ANCHOR_AMINA_NIGHT} reading the crumpled paper in cold fury while the trembling neighbor weeps",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "char_voisine",
                        "text": "Des avocats payés par un homme riche l'accusent de faux baux ! Vu son état, elle risque la prison ferme !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s04",
                "L'ultimatum de 23 heures",
                "Tense nocturnal close-up of a rain-speckled smartphone lighting up in Amina's steady hand showing late night hour 23:35, harsh cold blue light reflecting across her resolute eyes",
                "zoom_in",
                "fadeblack",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Il est vingt-trois heures. Si tu veux ta mère libre avant minuit, viens seule à ma résidence. C'est ta toute dernière chance.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s05",
                "L'orage tropical sur Abidjan",
                "Cinematic torrential tropical thunderstorm pounding Yopougon streets at night, jagged electric lightning bolts tearing across pitch-black sky, muddy alleys turning into rushing rivers reflecting golden streetlights",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Vingt-trois heures trente-cinq. Un orage tropical d'une violence inouïe s'abat sur Abidjan.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "L'imperméable sombre",
                f"Resolute vertical portrait of {ANCHOR_AMINA_NIGHT} buttoning her dark raincoat at the open threshold, not a single tear on her face, illuminated by lightning and warm doorway amber",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "char_voisine",
                        "text": "Où vas-tu par ce temps, Amina ?! C'est suicidaire !",
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "char_amina",
                        "text": "Cette nuit, tout s'arrête. Celui qui est en moi est plus grand que celui qui m'attend là-bas.",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s07",
                "Dans la gueule du loup",
                f"Epic heroic wide shot of {ANCHOR_AMINA_NIGHT} striding fearlessly down a flooded Abidjan boulevard under pouring rain and blinding lightning flashes, silhouette glowing like a warrior walking into destiny",
                "pan_right",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Sans un regard en arrière, Amina s'élance sous les trombes d'eau droit vers la résidence de Stéphane Koffi.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "Minuit moins dix devant la forteresse",
                "Ominous low-angle view of Koffi's towering luxury mansion gates illuminated by lightning and rain as a lone resolute young woman in a dark raincoat approaches the entrance",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Minuit moins dix. Le choc final entre le pouvoir de l'argent et l'autorité de l'autel va éclater.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 10 — Chapitre 10 : Le Choc des Rois
    # =========================================================================
    "ep-010": {
        "episode_id": "ep-010",
        "episode_number": 10,
        "title": "Le Choc des Rois — La Chute du Prédateur",
        "short_title": "EP. 10 • LE CHOC DES ROIS",
        "hook": "Amina trempée franchit le seuil : l'autorité spirituelle envahit la villa.",
        "cliffhanger": "Koffi hurle de terreur et s'effondre terrassé contre sa table de marbre !",
        "cta": BOOK_CTA,
        "mood": "spiritual_warfare",
        "bpm": 95,
        "scenes": [
            _scene(
                "s01",
                "Minuit moins dix dans le salon",
                f"Grand shadowed luxury mansion salon with rain-lashed floor-to-ceiling glass windows flashing with lightning, {ANCHOR_KOFFI} seated tensely in a leather armchair with trembling hands staring at an antique wall clock",
                "zoom_in",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Minuit moins dix. Dans son immense salon, les mains de Monsieur Koffi tremblent sous une migraine que rien ne peut calmer.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "L'entrée d'Amina",
                f"Iconic heroic vertical shot of heavy armored villa doors swinging open onto the storm, {ANCHOR_AMINA_NIGHT} stepping inside drenched in rain, water streaming from her face while her eyes burn with calm celestial fire",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Tu es venue... J'ai cru que tu n'oserais pas. Ta mère passe la nuit en cellule et tu...",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_amina",
                        "text": "Je ne suis pas venue pour négocier, Monsieur Koffi.",
                        "pause_after": 0.35,
                    },
                ],
            ),
            _scene(
                "s03",
                "L'autorité qui remplit la pièce",
                f"Majestic low-angle portrait of {ANCHOR_AMINA_NIGHT} stepping forward fearlessly across the polished marble floor, radiant warm golden rim light emanating behind her against the cold midnight-blue mansion",
                "tilt_up",
                "smoothleft",
                [
                    {
                        "speaker": "narrator",
                        "text": "Il attendait une adolescente à genoux. Il fait face à l'autorité redoutable de soixante-douze heures de prière persistante.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s04",
                "Le poids invisible s'abat",
                f"Shocking dramatic shot of {ANCHOR_KOFFI} staggering backward in sheer terror, eyes wide with panic, raising both hands to his head as if battered by overwhelming invisible blows",
                "zoom_in",
                "fadeblack",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Qu'est-ce... qu'est-ce qui m'arrive ?! Arrête ! Je ne peux plus respirer !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s05",
                "L'effondrement des forteresses",
                "Awe-inspiring cinematic shot inside the storm-lit mansion as dazzling golden light breaks through dark rolling shadows above the shattered room atmosphere, symbolic collapse of dark spiritual power",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Dans le monde invisible, l'ultime rempart des ténèbres s'écroule sous les coups répétés d'hupopiazo. L'ennemi lâche définitivement prise !",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "Le décret souverain d'Amina",
                f"Commanding close-up of {ANCHOR_AMINA_NIGHT} standing unshaken in the center of the grand salon, speaking like a sovereign decree with luminous warm golden lighting on her face",
                "push_in_dramatic",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Vous avez voulu détruire ma famille et briser ma mère. Mais le juste qui refuse de se taire renverse les trônes de l'injustice !",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s07",
                "La chute du prédateur",
                f"Dramatic high-angle shot of {ANCHOR_KOFFI} collapsing heavily against his black marble table and crashing to the floor, utterly broken, gasping for breath in defeat",
                "pan_left",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "Terrassé sans qu'aucune main humaine ne l'ait touché, le géant d'Abidjan s'effondre contre son propre marbre.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s08",
                "La nuit touche à sa fin",
                f"Triumphant serene silhouette of {ANCHOR_AMINA_NIGHT} turning calmly toward the open villa doors as the storm outside begins to break into soft golden pre-dawn light",
                "pan_right",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Amina se retourne calmement vers la sortie. La nuit est vaincue. La victoire est totale.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },

    # =========================================================================
    # EPISODE 11 — Chapitre 11 : L'Aube Nouvelle (Grand Final)
    # =========================================================================
    "ep-011": {
        "episode_id": "ep-011",
        "episode_number": 11,
        "title": "L'Aube Nouvelle — Le Triomphe de l'Autel",
        "short_title": "EP. 11 • L'AUBE NOUVELLE",
        "hook": "L'aube dorée se lève sur Yopougon : Maman Hélène est libre !",
        "cliffhanger": "Quand le juste refuse de se taire, les trônes d'injustice s'effondrent.",
        "cta": BOOK_CTA,
        "mood": "victory_dawn",
        "bpm": 115,
        "scenes": [
            _scene(
                "s01",
                "L'aube dorée sur Abidjan",
                "Breathtaking golden sunrise breaking through parting storm clouds over Abidjan and Yopougon rooftops, rain-washed streets shimmering with warm amber morning sunlight, sense of renewal and divine peace",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Les premières lueurs de l'aube percent les nuages sur Abidjan. La tempête est passée, lavant Yopougon de son cauchemar.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s02",
                "La capitulation de Koffi",
                f"Quiet morning light streaming through tall curtains into a luxury salon where a humbled shaken {ANCHOR_KOFFI} sits on the floor dialing an emergency phone call with trembling fingers",
                "zoom_out",
                "dissolve",
                [
                    {
                        "speaker": "char_koffi",
                        "text": "Annulez toutes les charges immédiatement. Libérez cette femme tout de suite... et ne prononcez plus jamais son nom.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s03",
                "Les retrouvailles devant le commissariat",
                f"Deeply joyous emotional embrace outside an Abidjan police station bathed in radiant golden morning sun: {ANCHOR_HELENE} stepping out free into the warm protective arms of {ANCHOR_AMINA_UNIFORM}, tears of gratitude glowing",
                "zoom_in",
                "smoothleft",
                [
                    {
                        "speaker": "char_helene",
                        "text": "Ma fille... qu'est-ce qui s'est passé ? Ils m'ont relâchée sans condition !",
                        "pause_after": 0.25,
                    },
                    {
                        "speaker": "char_amina",
                        "text": "La paix a triomphé, Maman. Dieu a combattu pour nous.",
                        "pause_after": 0.4,
                    },
                ],
            ),
            _scene(
                "s04",
                "L'expulsion déchirée",
                "Warm sunlit Yopougon family courtyard where the formerly arrogant 52-year-old African landlord stands humbly with bowed head tearing up the eviction notice in front of a relieved smiling family",
                "pan_right",
                "dissolve",
                [
                    {
                        "speaker": "char_proprietaire",
                        "text": "Je vous demande pardon... J'annule tout. Cette maison reste votre foyer.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s05",
                "Le pardon de Sarah",
                f"Heartwarming golden-hour courtyard scene of {ANCHOR_SARAH} weeping softly as she hugs {ANCHOR_AMINA_UNIFORM} in sincere repentance and awe at her friend's unshakable faith",
                "pan_left",
                "fade",
                [
                    {
                        "speaker": "char_sarah",
                        "text": "Pardonne-moi, Amina... J'ai eu peur des hommes, mais ton Dieu est plus fort qu'eux tous.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s06",
                "Les mains sur la Bible ouverte",
                f"Serene luminous close-up inside Amina's humble sunlit bedroom as {ANCHOR_AMINA_UNIFORM} rests both hands gently upon her open Bible where the whole battle began, floating golden dust motes in morning sunbeams",
                "push_in_dramatic",
                "dissolve",
                [
                    {
                        "speaker": "narrator",
                        "text": "De retour sur son autel de prière, Amina contemple la promesse accomplie : la prière persistante prive l'ennemi de tout repos.",
                        "pause_after": 0.35,
                    }
                ],
            ),
            _scene(
                "s07",
                "Yopougon vivante et libre",
                f"Radiant triumphant medium portrait of {ANCHOR_AMINA_UNIFORM} walking peacefully through vibrant sunlit Yopougon streets with head held high, surrounded by warm golden light and serene joy",
                "zoom_out",
                "fade",
                [
                    {
                        "speaker": "char_amina",
                        "text": "Ne laissez jamais l'ennemi respirer. Priez par l'Esprit, refusez la capitulation, et la lumière triomphera.",
                        "pause_after": 0.4,
                    }
                ],
            ),
            _scene(
                "s08",
                "Le triomphe de l'autel",
                "Majestic cinematic sunset-and-sunrise golden skyline over Abidjan lagoon and Yopougon glowing with celestial gold and deep royal blue harmony, inspiring grand finale atmosphere",
                "tilt_up",
                "fade",
                [
                    {
                        "speaker": "narrator",
                        "text": "Découvrez l'intégralité du roman Amina, l'Autel de Yopougon, par Karl Digré. Commandez votre exemplaire dès aujourd'hui.",
                        "pause_after": 0.5,
                    }
                ],
            ),
        ],
    },
}


def get_all_episode_ids() -> List[str]:
    """Return sorted canonical episode IDs (ep-001 .. ep-011)."""
    return sorted(STORYBOARDS.keys())


def get_storyboard(episode_id: str) -> Dict[str, Any]:
    """Return canonical storyboard dict for a given episode ID."""
    ep = episode_id.strip().lower()
    if ep not in STORYBOARDS:
        valid = ", ".join(get_all_episode_ids())
        raise KeyError(f"Unknown episode_id '{episode_id}'. Valid IDs: {valid}")
    return STORYBOARDS[ep]


if __name__ == "__main__":
    for ep_id in get_all_episode_ids():
        sb = STORYBOARDS[ep_id]
        n_scenes = len(sb["scenes"])
        n_lines = sum(len(s["dialogue"]) for s in sb["scenes"])
        n_words = sum(
            len(d["text"].split())
            for s in sb["scenes"]
            for d in s["dialogue"]
        )
        print(
            f"{ep_id}: {n_scenes} scenes | {n_lines} lines | {n_words} words | "
            f"mood={sb['mood']} ({sb['bpm']} BPM) | {sb['title']}"
        )
