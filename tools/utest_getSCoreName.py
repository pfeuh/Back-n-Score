#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_path = os.path.join(parent_dir, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
    
from getScoreName import getScoreName, getScoreNameError
from instruments import INSTRUMENTS, VIRTUAL_INSTRUMENTS, TONALITES, MODE_POPULAR, MODE_CLASSIQUE

VERBOSE = "-v" in sys.argv
if VERBOSE:
    print("mode VERBOSE actif")

def run_database_integrity_test(DB_PATH):
    success_count = 0
    fail_count = 0
    
    for root, dirs, files in os.walk(DB_PATH):
        pdf_files = [f for f in files if f.endswith(".pdf")]
        if not pdf_files:
            continue

        t_file = os.path.join(root, "trackname.txt")
        pretty_name = "Sans nom"
        if os.path.exists(t_file):
            with open(t_file, "r", encoding="utf-8") as fp:
                pretty_name = fp.read().strip()

        for f in pdf_files:
            target_file = os.path.splitext(f)[0]
            
            is_easy = target_file.startswith("easy")
            is_solo = "solo" in target_file
            
            clean = target_file.replace("easy", "").replace("solo", "")
            
            # Extraction propre de la voix
            voice = 1
            last_chars = ""
            for char in reversed(clean):
                if char.isdigit():
                    last_chars = char + last_chars
                else:
                    break
            
            if last_chars:
                voice = int(last_chars)
                inst_root = clean[:-len(last_chars)]
            else:
                inst_root = clean

            result = getScoreName(root, inst_root, voice=voice, solo=is_solo, easy=is_easy)

            if result ==target_file:
                success_count += 1
            else:
                fail_count += 1
                print(f"\n❌ {pretty_name}")
                print(f"    Chemin : {root}/{f}")
                print(f"    Erreur : {getScoreNameError() or 'Incohérence de nommage'}")
                print(f"    (Simulé avec : inst='{inst_root}', voice={voice}, solo={is_solo}, easy={is_easy})")

    if fail_count == 0:
        print(f"✨ Parfait ! {success_count} fichiers vérifiés avec succès.")
    else:
        print(f"\n--- BILAN : {success_count} OK / {fail_count} ERREURS ---")

def run_mode_popular_test(DB_PATH):
    """Test des substitutions sur Hal Leonard en mode Popular"""
    success_count = 0
    fail_count = 0
    
    scenarios = [
        ("040_bossaNova/aManAndAWoman", "flute", "DO"),
        ("040_bossaNova/aManAndAWoman", "trompette", "SIb"),
        ("040_bossaNova/aManAndAWoman", "sax_alto", "MIb"),
        ("040_bossaNova/dindi", "trombone", "trombone"),
        ("040_bossaNova/dindi", "flute", "flute"),
        ("040_bossaNova/dindi", "clarinette", "SIb"),
        ("bachFavoriteClassics/arioso", "clarinette", "clarinette"),
        ("choro/amenoReseda", "contrebasse", "DO"),
    ]

    print(f"\n--- TEST MODE POPULAR (Substitutions Hal Leonard) ---")

    for subpath, inst, expected in scenarios:
        root = os.path.join(DB_PATH, subpath)
        result = getScoreName(root, inst, voice=1, mode=MODE_POPULAR)

        if result == expected:
            success_count += 1
            if VERBOSE: print(f"✅ {inst.ljust(15)} -> {expected}")
        else:
            fail_count += 1
            print(f"❌ {inst.ljust(15)} -> Reçu: {result} | Attendu: {expected}")

    print(f"Bilan Popular : {success_count} OK / {fail_count} ERREURS")

def run_mode_classique_test(DB_PATH):
    """Test des voix et trombones sur Happy Clarinets 2 en mode Classique"""
    success_count = 0
    fail_count = 0
    
    # On cible spécifiquement le dossier happyClarinets2
    root = os.path.join(DB_PATH, "happyClarinets2")
    
    scenarios = [
        ("trombone", 1, False, "trombone"),            # Trombone UT
        ("trombone_sib", 2, False, "trombone_sib2"),   # Trombone SIb Voix 2
        ("cor_fa", 2, False, "cor_fa2"),               # Cor en Fa Voix 2
        ("clarinette", 1, True, "clarinettesolo1"),    # Solo 1
        ("clarinette", 3, False, "clarinette3"),       # Voix 3
    ]

    print(f"\n--- TEST MODE CLASSIQUE (Joyeux Vignerons) ---")

    for inst, voice, solo, expected in scenarios:
        result = getScoreName(root, inst, voice=voice, solo=solo, mode=MODE_CLASSIQUE)

        if result == expected:
            success_count += 1
            if VERBOSE: print(f"✅ {inst.ljust(15)} (v{voice}) -> {expected}")
        else:
            fail_count += 1
            print(f"❌ {inst.ljust(15)} (v{voice}) -> Reçu: {result} | Attendu: {expected}")

    print(f"Bilan Classique : {success_count} OK / {fail_count} ERREURS")

if __name__ == "__main__":

    DB_PATH = "../../backNScoreData/database"
    
    # 1. Test global d'intégrité
    DB_PATH_PF = os.path.join(DB_PATH, "pierreFaller/")
    run_database_integrity_test(DB_PATH)

    # 2. Test Hal Leonard en mode Popular
    DB_PATH_HAL = os.path.join(DB_PATH, "halLeonard")
    run_mode_popular_test(DB_PATH_HAL)
    
    # 3. Test Joyeux Vignerons en mode Classique
    DB_PATH_JV = os.path.join(DB_PATH, "bands/joyeuxVignerons")
    run_mode_classique_test(DB_PATH_JV)