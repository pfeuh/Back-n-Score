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

# Correction : On utilise le dossier configuré dans le JSON local de la machine !
DATABASE_DIR = CONFIG.get("DATABASE", DEFAULT_CONFIG["DATABASE"])
OUTPUT_DIR = BASE_DIR / "server_data"

def sortTracks(tracks):
    """Trie la liste par dossier parent, puis par titre."""
    tracks.sort(key=lambda x: (os.path.dirname(x['location']), x['title']))
    return tracks

def checkTrack(instrument_name, track_path):
    root_name = getFirstVoice(instrument_name)
    if not isValidInstrument(root_name):
        raise Exception(f"ERROR Instrument ou Tonalité inconnu '{instrument_name}' dans {track_path}")

def generate_track_tree():
    """Scanne la base de données et génère le catalogue plat."""
    print(f"Scan de la database située dans : {DATABASE_DIR}...")
    tracks = []
    converted_count = 0  # Notre compteur
    
    if not os.path.exists(DATABASE_DIR):
        print(f"ERREUR : Le dossier DATABASE '{DATABASE_DIR}' n'existe pas !")
        return tracks, converted_count
        
    for root, dirs, files in os.walk(DATABASE_DIR):
        if "trackname.txt" in files:
            relative_path = os.path.relpath(root, DATABASE_DIR)
            
            # Vérification des PDF (Sanité avec gestion des voix)
            for f in files:
                if f.endswith(".pdf"):
                    if VERBOSE:
                        print(f)
                    # On retire les 4 derniers caractères (.pdf) sans toucher à la casse
                    instr_key = f[:-4]
                    
                    # 1. Sanité
                    checkTrack(instr_key, relative_path)
            
                    # 2. Moulinette Delta
                    pdf_full_path = os.path.join(root, f)
                    if trackPdfToJpg(pdf_full_path):
                        converted_count += 1
                    
            # Lecture du titre
            try:
                with open(os.path.join(root, "trackname.txt"), "r", encoding="utf-8") as f:
                    title = f.read().strip()
                tracks.append({"title": title, "location": relative_path})
            except Exception as e:
                print(f"Erreur lecture titre dans {relative_path}: {e}")
                
    sortTracks(tracks)
                
    return tracks, converted_count

def generate_ui_trees():
    popular = {
        "MELODISTES": {t: [] for t in TONALITES if t != "NP"},
        "VOIX": [], # On crée une section dédiée pour le chant
        "SECTION BASSE": list(GROUP_BASSE),
        "SECTION POMPE": list(GROUP_POMPE),
        "PERCUSSIONS": []
    }
    
    # Classy reste basé sur tes FAMILIES (ne change pas)
    classy = {fam: [] for fam in FAMILIES}

    for key, data in INSTRUMENTS.items():
        tonality, clef, octave, family = data
        
        # --- LOGIQUE POPULAR ---
        # 1. Gestion des Voix (Section à part)
        if family in ["VOIX_HOMME", "VOIX_FEMME", "VOIX", "TEXTE"]:
            popular["VOIX"].append(key)
            
        # 2. Gestion des Percussions (uniquement les non-mélodiques)
        elif family == "PERCUSSIONS":
            popular["PERCUSSIONS"].append(key)
            
        # 3. Gestion des Mélodistes (inclut maintenant PERCUSSIONS_MELODIQUES)
        elif tonality in popular["MELODISTES"]:
            if key not in GROUP_BASSE and key not in GROUP_POMPE:
                if "grille" not in key:
                    popular["MELODISTES"][tonality].append(key)

        # --- LOGIQUE CLASSY (Immuable) ---
        if family in classy:
            classy[family].append(key)

    # --- POST-TRAITEMENT POPULAR ---
    for tona, list_instr in popular["MELODISTES"].items():
        list_instr.sort() # Alphabet
        if tona in VIRTUAL_INSTRUMENTS:
            list_instr.insert(0, tona) # Tonalité en tête
        
        # Ajout de la grille à la fin
        grille_name = "grille" if tona == "DO" else f"grille_{tona.lower()}"
        if grille_name in INSTRUMENTS:
            list_instr.append(grille_name)

    # Tri des autres sections
    popular["VOIX"].sort()
    popular["SECTION BASSE"].sort()
    popular["SECTION POMPE"].sort()
    popular["PERCUSSIONS"].sort()

    # Nettoyage
    popular = {k: v for k, v in popular.items() if len(v) > 0}
    classy = {k: v for k, v in classy.items() if len(v) > 0}

    return popular, classy

def run():
    start_time = time.time() # Top départ
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Génération et sauvegarde
    tracks, total_converted = generate_track_tree()
    
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

    # --- RAPPORT DE FIN ---
    end_time = time.time()
    duration = end_time - start_time
    
    # Conversion en minutes/secondes pour la lisibilité
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    print("\n" + "="*40)
    print("RAPPORT DE LA MOULINETTE")
    print("="*40)
    print(f"Morceaux indexés      : {len(tracks)}")
    print(f"PDF convertis (Delta) : {total_converted}")
    print(f"Durée totale          : {minutes}m {seconds}s")
    if total_converted > 0:
        avg = duration / total_converted
        print(f"Vitesse moyenne       : {avg:.2f} sec / PDF")
    print("="*40)

if __name__ == "__main__":
    run()