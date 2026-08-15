#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from instruments import (INSTRUMENTS, VIRTUAL_INSTRUMENTS, TONALITES, MODE_POPULAR, MODE_CLASSIQUE, GROUP_BASSE, GROUP_POMPE)
from PyPDF2 import PdfReader

_LAST_ERROR = ""
TRACKNAME_FNAME = "trackname.txt"

def getScoreNameError():
    global _LAST_ERROR
    return _LAST_ERROR

def _set_error(msg):
    global _LAST_ERROR
    _LAST_ERROR = msg

def _mode2text(mode):
    if mode == MODE_POPULAR:
        return "POPULAR"
    elif mode == MODE_CLASSIQUE:
        return "CLASSIQUE"
    else:
        return f"{mode}{type(mode)}"

def _getPdfNames(track_path):
    files = []
    for f in os.listdir(track_path):
        if os.path.isfile(os.path.join(track_path, f)) and f.endswith('.pdf'):
            name_no_ext = os.path.splitext(f)[0]
            files.append(name_no_ext)
    return files

def getNbPages(track_path, score_name):
    pdf_name = os.path.join(track_path, f"{score_name}.pdf")
    if os.path.isfile(pdf_name):
        try:
            reader = PdfReader(pdf_name)
            return len(reader.pages)
        except:
            _set_error(f"{pdf_name} est corrompu")
            return 0
    else:
        _set_error(f"impossible de compter les pages, {pdf_name} non trouvé")
        return 0

def getScoreNameLite(track_path, instrument, voice=1, mode=MODE_POPULAR, solo=False, easy=False, page=1, is_obsolete=False):
    _set_error("")
    scores = _getPdfNames(track_path)
    for score in scores:
        if instrument == score:
            return score
    _set_error(f"Pas de partition {instrument} pour {os.path.basename(track_path)} dans le mode {_mode2text(mode)}")
    return None

def getScoreName(track_path, instrument, voice=1, mode=MODE_POPULAR, solo=False, easy=False, page=1, is_obsolete=False):
    _set_error("")
    
    # 1. Vérifications préliminaires
    if not os.path.exists(track_path):
        _set_error(f"Le dossier '{track_path}' est inconnu.")
        return None

    trackname_file = os.path.join(track_path, TRACKNAME_FNAME)
    if os.path.exists(trackname_file):
        with open(trackname_file, "r", encoding="utf-8") as fp:
            track_name = fp.read(-1).strip()
    else:
        track_name = os.path.basename(track_path)

    original_instrument = instrument

    # Gestion du suffixe 'solo'
    if instrument.endswith('solo') and not solo:
        solo = True
        instrument = instrument[:-4]

    # Extraction sécurisée du numéro de voix si l'instrument fourni finit par un chiffre (ex: clarinette2)
    requested_voice = voice
    clean_inst = instrument
    match = re.search(r'^(.*?)(\d+)$', instrument)
    if match:
        base_name = match.group(1)
        try:
            ext_v = int(match.group(2))
            clean_inst = base_name
            if voice == 1:
                requested_voice = ext_v
        except ValueError:
            pass

    # Validation souple de l'instrument (tolérance sur les noms composés non présents dans les dictionnaires)
    def is_valid_inst(inst):
        return (inst in INSTRUMENTS or 
                inst in TONALITES or 
                inst in VIRTUAL_INSTRUMENTS or 
                f"{inst}solo" in INSTRUMENTS or 
                f"{inst}solo" in VIRTUAL_INSTRUMENTS or
                "horn" in inst or "baryton" in inst)

    if not is_valid_inst(original_instrument) and not is_valid_inst(clean_inst):
        _set_error(f"L'instrument '{original_instrument}' est inconnu.")
        return None

    # Récupération de tous les fichiers PDF du dossier (sans extension)
    instruments_on_disk = [os.path.splitext(f)[0] for f in os.listdir(track_path) if f.lower().endswith('.pdf')]
    if not instruments_on_disk:
        _set_error(f"Aucune partition trouvée pour {track_name}")
        return None

    # 2. Construction de la hiérarchie des noms de base recherchés
    base_variants = []
    if original_instrument not in base_variants:
        base_variants.append(original_instrument)
    if easy and solo: base_variants.append(f"easy{clean_inst}solo")
    if easy:         base_variants.append(f"easy{clean_inst}")
    if solo:         base_variants.append(f"{clean_inst}solo")
    base_variants.append(clean_inst)

    # 3. Recherche de la base correspondante sur le disque
    found_base = None
    for base in base_variants:
        target_v = f"{base}{requested_voice}" if requested_voice > 1 else base
        if target_v in instruments_on_disk:
            return target_v
        
        if base in instruments_on_disk:
            found_base = base
            break
            
        matches = [f for f in instruments_on_disk if f == base or (f.startswith(base) and f[len(base):].isdigit())]
        if matches:
            found_base = base
            break

    # 4. Repli stratégique si rien n'a été trouvé via les variantes directes
    if found_base is None:
        if mode == MODE_POPULAR:
            found_base = findPopularInstrument(track_path, clean_inst, instruments_on_disk, track_name)
        elif mode == MODE_CLASSIQUE:
            found_base = findClassicInstrument(track_path, clean_inst, instruments_on_disk, track_name)
            
    if found_base is None:
        return None

    # Si le repli a retourné un nom exact présent sur le disque (ex: "DO", "SIb", "trombone")
    if found_base in instruments_on_disk:
        if requested_voice == 1 or found_base in TONALITES or found_base == "grille" or found_base.startswith("grille_") or found_base == "paroles":
            return found_base

    # 5. Résolution finale de la voix (Descente de requested_voice vers 1)
    for v in range(int(requested_voice), 0, -1):
        candidate = f"{found_base}{v}" if v > 1 else found_base
        if candidate in instruments_on_disk:
            return candidate
        candidate_v1 = f"{found_base}1"
        if v == 1 and candidate_v1 in instruments_on_disk:
            return candidate_v1

    # Dernier recours : premier candidat disponible commençant par la base trouvée
    candidates = sorted([f for f in instruments_on_disk if f == found_base or (f.startswith(found_base) and f[len(found_base):].isdigit())],
                        key=lambda x: int(x[len(found_base):]) if x[len(found_base):].isdigit() else 1)
    if candidates:
        return candidates[0]
        
    if found_base in instruments_on_disk:
        return found_base

    _set_error(f"Incohérence de nommage pour {clean_inst}")
    return None

def findPopularInstrument(track_path, target_instrument, instruments_on_disk, trackname):
    info = INSTRUMENTS.get(target_instrument) or VIRTUAL_INSTRUMENTS.get(target_instrument)
    if not info: return None
    t_tona, t_clef, t_oct, t_fam = info

    if target_instrument in GROUP_BASSE or t_oct == "-2":
        for m in GROUP_BASSE:
            if m in instruments_on_disk: return m
    elif target_instrument in GROUP_POMPE or t_fam == "CLAVIERS":
        for m in GROUP_POMPE:
            if m in instruments_on_disk: return m
    elif t_fam == "PERCUSSIONS":
        for name, (tona, clef, oct, fam) in INSTRUMENTS.items():
            if name in instruments_on_disk and fam == "PERCUSSIONS": return name
        if instruments_on_disk: return instruments_on_disk[0]

    if t_tona in instruments_on_disk: return t_tona
    for name, (tona, clef, oct, fam) in INSTRUMENTS.items():
        if name in instruments_on_disk and tona == t_tona and oct == t_oct: return name
    for name, (tona, clef, oct, fam) in INSTRUMENTS.items():
        if name in instruments_on_disk and tona == t_tona: return name

    if t_oct == "-2" or t_fam == "CLAVIERS" or target_instrument in GROUP_POMPE:
        nom_grille = f"grille_{t_tona}" if t_tona != "DO" else "grille"
        if nom_grille in instruments_on_disk: return nom_grille
        if "grille" in instruments_on_disk: return "grille"
    if t_fam == "VOIX" or target_instrument == "chant":
        if "paroles" in instruments_on_disk: return "paroles"

    _set_error(f"POP: Aucune partition (même de secours) {target_instrument} pour {trackname}.")
    return None

def findClassicInstrument(track_path, target_instrument, instruments_on_disk, trackname):
    info = INSTRUMENTS.get(target_instrument) or VIRTUAL_INSTRUMENTS.get(target_instrument)
    if not info: return None
    t_tona, t_clef, t_oct, t_fam = info

    if t_tona in instruments_on_disk: return t_tona
    if target_instrument in GROUP_BASSE or t_oct == "-2":
        for m in GROUP_BASSE:
            if m in instruments_on_disk:
                m_info = INSTRUMENTS.get(m)
                if m_info and m_info[0] == t_tona and m_info[2] == t_oct: return m

    for name, (tona, clef, oct, fam) in INSTRUMENTS.items():
        if name in instruments_on_disk:
            if tona == t_tona and clef == t_clef and oct == t_oct and fam == t_fam: return name

    _set_error(f"OLD: Aucune partition (même de secours) {target_instrument} pour {trackname}.")
    return None

if __name__ == "__main__":
    
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
        success_count = 0
        fail_count = 0
        VERBOSE = True
        
        scenarios = [
            ("books/halLeonard/040_bossaNova/aManAndAWoman", "flute", "DO"),
            ("books/halLeonard/040_bossaNova/aManAndAWoman", "trompette", "SIb"),
            ("books/halLeonard/040_bossaNova/aManAndAWoman", "sax_alto", "MIb"),
            ("books/halLeonard/040_bossaNova/dindi", "trombone", "trombone"),
            ("books/halLeonard/040_bossaNova/dindi", "flute", "flute"),
            ("books/halLeonard/040_bossaNova/dindi", "clarinette", "SIb"),
            ("books/halLeonard/bachFavoriteClassics/arioso", "clarinette", "clarinette"),
            ("books/halLeonard/choro/amenoReseda", "contrebasse", "DO"),
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
        
        root = os.path.join(DB_PATH, "grandfatherSClock")
        
        scenarios = [
            ("trombone", 1, False, "trombone"),            # Trombone UT
            ("trombone_sib", 2, False, "trombone_sib2"),   # Trombone SIb Voix 2
            ("cor_fa", 2, False, "cor_fa2"),               # Cor en Fa Voix 2
            ("horn_barytonsolo", 1, True, "horn_barytonsolo"),    # Solo 1
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

    VERBOSE = True

    DB_PATH = "../../backNScoreData/database"
    DB_PATH_PF = os.path.join(DB_PATH, "pierreFaller/")
    # run_database_integrity_test(DB_PATH)

    run_mode_popular_test(DB_PATH)
    
    # 3. Test Joyeux Vignerons en mode Classique
    DB_PATH_JV = os.path.join(DB_PATH, "bands/joyeuxVignerons")
    run_mode_classique_test(DB_PATH_JV)