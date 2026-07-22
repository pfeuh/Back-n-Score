#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Cette moulinette rafraichit les données du serveur
quand on a changé quelque chose dans la base de données:
1. ajout/déplacement/suppression de dossiers
2. renomage de dossier/fichiers
3. etc...
"""

import os
import json
import sys
from pathlib import Path
import time

VERBOSE = "-v" in sys.argv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_path = os.path.join(parent_dir, "scripts")
print(scripts_path)
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from instruments import INSTRUMENTS, VIRTUAL_INSTRUMENTS, GROUP_BASSE, GROUP_POMPE, TONALITES, FAMILIES, isKnownInstrument, getFirstVoice, isValidInstrument
from trackPdfToJpg import trackPdfToJpg

# Configuration des chemins de base
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Valeurs par défaut si le fichier config.json est introuvable
DEFAULT_CONFIG = {
    "DATABASE": "/mnt/Data1/Documents/backNScoreData/database",
    "INDEX_FILE": "server_data/db_tracks.json"
}

def load_config():
    """Charge la config partagée (PC ou Pi) pour récupérer le bon dossier DATABASE"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lecture config.json, utilisation des valeurs par défaut : {e}")
    return DEFAULT_CONFIG

# Chargement dynamique de la configuration
CONFIG = load_config()

# On utilise le dossier configuré dans le JSON local de la machine !
DATABASE_DIR = CONFIG.get("DATABASE", DEFAULT_CONFIG["DATABASE"])
OUTPUT_DIR = BASE_DIR / "server_data"

def sortTracks(tracks):
    """Trie la liste par dossier parent, puis par titre."""
    tracks.sort(key=lambda x: (os.path.dirname(x['location']), x['title']))
    return tracks

def checkTrack(instrument_name, track_path):
    root_name = getFirstVoice(instrument_name)
    if not isValidInstrument(root_name):
        raise Exception(f"Instrument ou Tonalité inconnu '{instrument_name}' dans {track_path}")

def generate_track_tree():
    """Scanne la base de données et génère le catalogue plat. Retourne aussi les erreurs collectées."""
    print(f"Scan de la database située dans : {DATABASE_DIR}...")
    tracks = []
    converted_count = 0
    errors = []  # Contiendra les messages des fichiers en anomalie
    
    if not os.path.exists(DATABASE_DIR):
        err_msg = f"Le dossier DATABASE '{DATABASE_DIR}' n'existe pas !"
        print(f"ERREUR : {err_msg}")
        return tracks, converted_count, [err_msg]
        
    for root, dirs, files in os.walk(DATABASE_DIR):
        if "trackname.txt" in files:
            relative_path = os.path.relpath(root, DATABASE_DIR)
            
            # Vérification des PDF (Sanité avec gestion des voix)
            for f in files:
                if f.endswith(".pdf"):
                    if VERBOSE:
                        print(f)
                    instr_key = f[:-4]
                    
                    try:
                        # 1. Sanité
                        checkTrack(instr_key, relative_path)
                        
                        # 2. Moulinette Delta
                        pdf_full_path = os.path.join(root, f)
                        if trackPdfToJpg(pdf_full_path):
                            converted_count += 1
                            
                    except Exception as err:
                        # Enregistrement de l'erreur pour la remonter au client HTTP
                        errors.append(f"{relative_path}/{f} -> {str(err)}")
            
            # Lecture du titre
            try:
                with open(os.path.join(root, "trackname.txt"), "r", encoding="utf-8") as f:
                    title = f.read().strip()
                tracks.append({"title": title, "location": relative_path})
            except Exception as e:
                errors.append(f"{relative_path}/trackname.txt -> Erreur lecture titre: {str(e)}")
                
    sortTracks(tracks)
                
    return tracks, converted_count, errors

def generate_ui_trees():
    popular = {
        "MELODISTES": {t: [] for t in TONALITES if t != "NP"},
        "VOIX": [],
        "SECTION BASSE": list(GROUP_BASSE),
        "SECTION POMPE": list(GROUP_POMPE),
        "PERCUSSIONS": []
    }
    
    classy = {fam: [] for fam in FAMILIES}

    for key, data in INSTRUMENTS.items():
        tonality, clef, octave, family = data
        
        if family in ["VOIX_HOMME", "VOIX_FEMME", "VOIX", "TEXTE"]:
            popular["VOIX"].append(key)
        elif family == "PERCUSSIONS":
            popular["PERCUSSIONS"].append(key)
        elif tonality in popular["MELODISTES"]:
            if key not in GROUP_BASSE and key not in GROUP_POMPE:
                if "grille" not in key:
                    popular["MELODISTES"][tonality].append(key)

        if family in classy:
            classy[family].append(key)

    for tona, list_instr in popular["MELODISTES"].items():
        list_instr.sort()
        if tona in VIRTUAL_INSTRUMENTS:
            list_instr.insert(0, tona)
        
        grille_name = "grille" if tona == "DO" else f"grille_{tona.lower()}"
        if grille_name in INSTRUMENTS:
            list_instr.append(grille_name)

    popular["VOIX"].sort()
    popular["SECTION BASSE"].sort()
    popular["SECTION POMPE"].sort()
    popular["PERCUSSIONS"].sort()

    popular = {k: v for k, v in popular.items() if len(v) > 0}
    classy = {k: v for k, v in classy.items() if len(v) > 0}

    return popular, classy

def run():
    """Fonction principale. Renvoie un dictionnaire de bilan avec les erreurs pour l'API."""
    start_time = time.time()
    OUTPUT_DIR.mkdir(exist_ok=True)

    tracks, total_converted, errors = generate_track_tree()
    
    with open(OUTPUT_DIR / "db_tracks.json", "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=4, ensure_ascii=False)

    pop_tree, class_tree = generate_ui_trees()
    with open(OUTPUT_DIR / "ui_popular.json", "w", encoding="utf-8") as f:
        json.dump(pop_tree, f, indent=4, ensure_ascii=False)
    with open(OUTPUT_DIR / "ui_classy.json", "w", encoding="utf-8") as f:
        json.dump(class_tree, f, indent=4, ensure_ascii=False)

    meta = {**INSTRUMENTS, **VIRTUAL_INSTRUMENTS}
    with open(OUTPUT_DIR / "meta_instruments.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    # Dictionnaire de bilan renvoyé à l'appelant Python (votre route Flask /api/admin/refresh)
    return {
        "status": "success" if not errors else "warning",
        "tracks_count": len(tracks),
        "converted_count": total_converted,
        "duration": f"{minutes}m {seconds}s",
        "errors": errors
    }

if __name__ == "__main__":
    res = run()
    print(f"\nIndexation terminée. Status: {res['status']}. Morceaux: {res['tracks_count']}. Erreurs: {len(res['errors'])}")