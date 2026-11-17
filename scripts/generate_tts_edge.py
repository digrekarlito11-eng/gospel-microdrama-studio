#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Génération Automatique des Voix (Edge-TTS Gratuit)
Ce script génère les pistes vocales de chaque personnage en français naturel
avec les intonations et voix définies dans bible/characters.json.
"""

import os
import json
import asyncio
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
EPISODE_DIR = os.path.join(STUDIO_ROOT, "episodes", "ep-001")
AUDIO_DIR = os.path.join(EPISODE_DIR, "audio")
BIBLE_PATH = os.path.join(STUDIO_ROOT, "bible", "characters.json")

os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE_LINES = [
    # (id, character_id, text)
    ("line_01", "char_helene", "À Yopougon, quand la nuit tombe, deux prédateurs ont déjà fixé son prix..."),
    ("line_02", "char_helene", "Amina, 17 ans. Fille de prière. Elle pensait juste rentrer chez elle..."),
    ("line_03", "char_acolyte", "Même un regard elle ne te donne pas Zagba ! Elle marche comme si notre sol allait salir ses chaussures !"),
    ("line_04", "char_zagba", "Elle fait la difficile parce que personne n'a posé le bon prix. Retiens bien : avant la fin de ce mois, cette fille marche à mes côtés. C'est un pari !"),
    ("line_05", "char_acolyte", "C'est la fille de la croyante du marché, mon frère !"),
    ("line_06", "char_zagba", "Tout s'achète ou se brise. Tout."),
    ("line_07", "char_koffi", "Vous êtes certain qu'elle rentre directement chez elle tous les soirs ?"),
    ("line_08", "char_chauffeur", "Oui Monsieur le Directeur. Lycée, marché pour aider sa mère, puis maison. Une rigueur absolue."),
    ("line_09", "char_koffi", "Une rigueur absolue... Plus le fruit est haut sur l'arbre, plus la chute est spectaculaire. Trouvez ses faiblesses d'ici vendredi."),
    ("line_10", "char_amina", "Maman, comment te sens-tu ce soir ?"),
    ("line_11", "char_helene", "La grâce de Dieu me maintient debout ma fille. Va te reposer."),
    ("line_12", "char_helene", "Mais sous la porte de sa chambre, une mystérieuse enveloppe kraft..."),
    ("line_13", "char_koffi", "Tu n'as nulle part où te cacher. Bientôt, tu seras à moi.")
]

async def generate_line(voice: str, pitch: str, rate: str, text: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(output_path)

async def main():
    print("🎙️ Chargement de la bible des personnages...")
    with open(BIBLE_PATH, "r", encoding="utf-8") as f:
        bible = json.load(f)
    
    char_map = {c["id"]: c["voice_profile"] for c in bible["characters"]}

    generated_files = []
    print(f"🎬 Génération de {len(VOICE_LINES)} répliques pour l'épisode 1...")

    for line_id, char_id, text in VOICE_LINES:
        profile = char_map.get(char_id, {
            "voice_id": "fr-FR-DeniseNeural",
            "pitch": "+0Hz",
            "rate": "+0%"
        })
        out_file = os.path.join(AUDIO_DIR, f"{line_id}.mp3")
        print(f"  ▶ [{char_id}] ({profile['voice_id']}): \"{text[:45]}...\"")
        try:
            await generate_line(
                voice=profile["voice_id"],
                pitch=profile["pitch"],
                rate=profile["rate"],
                text=text,
                output_path=out_file
            )
            generated_files.append(out_file)
        except Exception as e:
            print(f"    ⚠️ Erreur génération ({e}), création d'un fallback synthétique...")
            # Fallback using ffmpeg tone or silence
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "3", "-q:a", "9", "-acodec", "libmp3lame", out_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            generated_files.append(out_file)

    # Concat all lines into voiceover.mp3
    concat_list = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in generated_files:
            f.write(f"file '{os.path.basename(p)}'\n")

    master_voice = os.path.join(AUDIO_DIR, "voiceover.mp3")
    print("🎛️ Assemblage de la piste master voix...")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", master_voice
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Voix générées avec succès : {master_voice}")

if __name__ == "__main__":
    asyncio.run(main())
