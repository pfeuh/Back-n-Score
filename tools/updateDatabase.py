#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Cette moulinette rafraichit les données du serveur
quand on a changé quelque chose dans la base de données:
1. ajout/déplacement/suppression de dossiers
2. renomage de dossier/fichiers
3. etc...
4. Audit strict et extraction des types de MP3 (Étape 1 Audio)
5. Nettoyage automatique et optimisé des fichiers de sauvegarde MuseScore (.mscz~)
"""

import os
import json
import sys
import re
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

def clean_and_validate_mp3(filename, relative_path):
    """
    Vérifie les règles de conformité audio.
    Lève une exception descriptive si le fichier viole une règle.
    Renvoie la racine fonctionnelle du type de MP3 si valide.
    """
    mp3_name = filename[:-4]  # Enlève l'extension .mp3

    # 1. Détection des pistes de section obsolètes (chiffres ou mots-clés de structure)
    if re.search(r'\d', mp3_name):
        raise Exception(f"Fichier de section obsolète (contient des chiffres). À supprimer, utilise les locators.")
        
    interdit_keywords = ["bridge", "interlude", "end", "intro", "chorus"]
    if any(kw in mp3_name.lower() for kw in interdit_keywords):
        raise Exception(f"Fichier de section obsolète (repère structurel '{mp3_name}'). À supprimer, utilise les locators.")

    # 2. Validation stricte des racines autorisées et extraction pour l'admin
    if mp3_name.startswith("backtrack"):
        return "backtrack"
    elif mp3_name.startswith("demo"):
        return "demo"
    elif mp3_name.startswith("melody"):
        return "melody"
    elif mp3_name.startswith("no"):
        # Format attendu : noPiano, noBass, noPianoWaltz, etc. (no + Majuscule)
        if len(mp3_name) > 2 and mp3_name[2].isupper():
            # Extraction du type fonctionnel (ex: "noPianoWaltz" -> "noPiano")
            match = re.match(r'^(no[A-Z][a-z]+)', mp3_name)
            if match:
                return match.group(1)
            return mp3_name
        else:
            raise Exception(f"Nommage 'no[Instrument]' incorrect ('{mp3_name}'). Une majuscule est requise après 'no' (ex: noBass).")
            
    # Toutes les typos (y compris ùelody) échouent proprement ici :
    raise Exception(f"Nomenclature inconnue ou hors-norme ('{mp3_name}'). Utilise le camelCase (ex: backtrack, demo, melody, noPiano).")

def generate_track_tree():
    """Scanne la base de données en une seule passe : linter, extraction des types MP3 et purge des backups MuseScore."""
    print(f"Scan et nettoyage de la database située dans : {DATABASE_DIR}...")
    tracks = []
    converted_count = 0
    mscz_deleted_count = 0
    
    # Dictionnaires d'erreurs catégorisées
    categorized_errors = {
        "AUDIO": [],
        "INSTRUMENTS": [],
        "STRUCTURE": []
    }
    
    mp3_types = set()
    
    if not os.path.exists(DATABASE_DIR):
        err_msg = f"Le dossier DATABASE '{DATABASE_DIR}' n'existe pas !"
        print(f"ERREUR : {err_msg}")
        return tracks, converted_count, {"STRUCTURE": [err_msg]}, [], 0
        
    for root, dirs, files in os.walk(DATABASE_DIR):
        # 1. Nettoyage à la volée des .mscz~ rencontrés n'importe où dans la base
        for f in files:
            if f.endswith("mscz~") or f.endswith(".mscz~"):
                full_path = os.path.join(root, f)
                try:
                    os.remove(full_path)
                    mscz_deleted_count += 1
                    if VERBOSE:
                        print(f"Supprimé en ligne : {full_path}")
                except Exception as e:
                    print(f"Impossible de supprimer le fichier backup {full_path} : {e}")

        # 2. Indexation des dossiers valides (contenant trackname.txt)
        if "trackname.txt" in files:
            relative_path = os.path.relpath(root, DATABASE_DIR)
            
            # Balayage des fichiers pour l'indexation
            for f in files:
                # --- TRAITEMENT DES PARTITIONS PDF ---
                if f.endswith(".pdf"):
                    if VERBOSE:
                        print(f)
                    instr_key = f[:-4]
                    
                    try:
                        checkTrack(instr_key, relative_path)
                        pdf_full_path = os.path.join(root, f)
                        if trackPdfToJpg(pdf_full_path):
                            converted_count += 1
                            
                    except Exception as err:
                        categorized_errors["INSTRUMENTS"].append(f"{relative_path}/{f} -> {str(err)}")
                
                # --- TRAITEMENT DES AUDIO MP3 ---
                elif f.endswith(".mp3"):
                    try:
                        functional_root = clean_and_validate_mp3(f, relative_path)
                        mp3_types.add(functional_root)
                    except Exception as err:
                        categorized_errors["AUDIO"].append(f"{relative_path}/{f} -> {str(err)}")
            
            # --- LECTURE DU TITRE ---
            try:
                with open(os.path.join(root, "trackname.txt"), "r", encoding="utf-8") as f:
                    title = f.read().strip()
                tracks.append({"title": title, "location": relative_path})
            except Exception as e:
                categorized_errors["STRUCTURE"].append(f"{relative_path}/trackname.txt -> Erreur lecture titre: {str(e)}")
                
    sortTracks(tracks)
                
    return tracks, converted_count, categorized_errors, sorted(list(mp3_types)), mscz_deleted_count

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

def write_errors_report(categorized_errors):
    """Écrit le rapport complet des anomalies dans server_data/database_errors.txt"""
    report_path = OUTPUT_DIR / "database_errors.txt"
    total_errors = sum(len(v) for v in categorized_errors.values())
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=====================================================================\n")
        f.write(f" RAPPORT D'ANOMALIES DATABASE - BACK'N SCORE ({time.strftime('%d/%m/%Y %H:%M:%S')})\n")
        f.write(f" Total d'anomalies à corriger : {total_errors}\n")
        f.write("=====================================================================\n\n")
        
        for category, err_list in categorized_errors.items():
            f.write(f"=== ERREURS DE {category} ({len(err_list)}) ===\n")
            if err_list:
                for err in err_list:
                    f.write(f"- {err}\n")
            else:
                f.write("(Aucune erreur détectée dans cette catégorie)\n")
            f.write("\n")
            
    return total_errors

def run():
    """Fonction principale. Renvoie un dictionnaire de bilan avec les erreurs pour l'API."""
    start_time = time.time()
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Récupération des données avec boucle unique (Linter + Nettoyage mscz~ inclus)
    tracks, total_converted, categorized_errors, mp3_types, mscz_deleted = generate_track_tree()
    
    # Sauvegarde du catalogue de morceaux
    with open(OUTPUT_DIR / "db_tracks.json", "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=4, ensure_ascii=False)

    # Sauvegarde des types fonctionnels de MP3 pour la page Admin
    with open(OUTPUT_DIR / "mp3_types.json", "w", encoding="utf-8") as f:
        json.dump(mp3_types, f, indent=4, ensure_ascii=False)

    # Génération et écriture du rapport d'erreurs global
    total_errors_count = write_errors_report(categorized_errors)

    # Récupération des structures UI
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

    # Aplatir la liste des erreurs pour la rétrocompatibilité de l'API Flask
    all_errors_flat = []
    for k, v in categorized_errors.items():
        all_errors_flat.extend(v)

    return {
        "status": "success" if total_errors_count == 0 else "warning",
        "tracks_count": len(tracks),
        "converted_count": total_converted,
        "mp3_types_count": len(mp3_types),
        "mscz_deleted_count": mscz_deleted,
        "duration": f"{minutes}m {seconds}s",
        "errors": all_errors_flat
    }

if __name__ == "__main__":
    res = run()
    total_errors = len(res['errors'])
    print(f"\nIndexation terminée. Status: {res['status']}.")
    print(f"Morceaux valides: {res['tracks_count']} | Types MP3 extraits: {res['mp3_types_count']}")
    print(f"Sauvegardes MuseScore (.mscz~) supprimées (à la volée): {res['mscz_deleted_count']}")
    print(f"Anomalies bloquées (voir database_errors.txt): {total_errors}")