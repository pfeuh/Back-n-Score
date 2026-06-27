#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from instruments import (INSTRUMENTS, VIRTUAL_INSTRUMENTS, TONALITES, MODE_POPULAR, MODE_CLASSIQUE, GROUP_BASSE, GROUP_POMPE)
from PyPDF2 import PdfReader # Ou PdfFileReader pour les très vieilles versions

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
    # os.listdir donne tout le contenu
    files = []
    for f in os.listdir(track_path):
        # On vérifie que c'est un fichier et qu'il finit par .pdf
        if os.path.isfile(os.path.join(track_path, f)) and f.endswith('.pdf'):
            # os.path.splitext sépare 'trompette' et '.pdf'
            name_no_ext = os.path.splitext(f)[0]
            files.append(name_no_ext)
    return files

def getNbPages(track_path, score_name):
    print((track_path, score_name))
    pdf_name = os.path.join(track_path, f"{score_name}.pdf")
    if os.path.isfile(pdf_name):
        try:
            reader = PdfReader(pdf_name)
            nb_pages = len(reader.pages)
            return nb_pages
        except:
            _set_error(f"{pdf_name} est corrompu")
            return 0
    else:
        _set_error(f"impossible de compter les pages, {pdf_name} non trouvé")
        return 0

def getScoreNameLite(track_path, instrument, voice=1, mode=MODE_POPULAR, solo=False, easy=False, page=1, is_obsolete=False):
    _set_error("")
    scores = _getPdfNames(track_path)
    print(scores)
    for score in scores:
        print(instrument, score)
        if instrument == score:
            return score
    _set_error(f"Pas de partition {instrument} pour {os.path.basename(track_path)} dans le mode {_mode2text(mode)}")
    return None

def getScoreName(track_path, instrument, voice=1, mode=MODE_POPULAR, solo=False, easy=False, page=1, is_obsolete=False):
    _set_error("")
    with open(os.path.join(track_path, TRACKNAME_FNAME), "r", encoding="utf-8") as fp:
        track_name = fp.read(-1).strip()
    
    # 1. Validation élargie
    if instrument not in INSTRUMENTS and instrument not in TONALITES and instrument not in VIRTUAL_INSTRUMENTS:
        _set_error(f"L'instrument '{instrument}' est inconnu.")
        return None
    
    if not os.path.exists(track_path):
        _set_error(f"Le dossier '{track_path}' est inconnu.")
        return None

    # On scanne les PDF comme source de vérité (noms sans extension)
    instruments_on_disk = [os.path.splitext(f)[0] for f in os.listdir(track_path) 
                           if f.lower().endswith('.pdf')]
    
    if not instruments_on_disk:
        _set_error(f"Aucune partition trouvée pour {track_name}")
        return None

    # 2. Construction de la cascade de variantes
    variantes = []
    if easy and solo: variantes.append(f"easy{instrument}solo")
    if easy:           variantes.append(f"easy{instrument}")
    if solo:           variantes.append(f"{instrument}solo")
    variantes.append(instrument)

    found = None
    for base in variantes:
        # Match exact ou début de nom pour les voix
        if base in instruments_on_disk or any(f.startswith(base) and f[len(base):].isdigit() for f in instruments_on_disk):
            found = base
            break

    # 3. Repli si rien trouvé sur le disque
    if found is None:
        if mode == MODE_POPULAR:
            found = findPopularInstrument(track_path, instrument, instruments_on_disk, track_name)
        elif mode == MODE_CLASSIQUE:
            found = findClassicInstrument(track_path, instrument, instruments_on_disk, track_name)

    # 4. Gestion finale des voix
    if found:
        final_base = found
        # Descente d'escalier pour les voix
        try:
            v_start = int(voice)
        except:
            v_start = 1
            
        for v in range(v_start, 1, -1):
            iname = f"{found}{v}"
            if iname in instruments_on_disk:
                final_base = iname
                break
        
        # Sécurité : si le nom trouvé (ou substitué) n'est pas tel quel sur le disque, 
        # on cherche la première voix disponible (ex: sax_alto2 seul présent)
        if final_base not in instruments_on_disk:
            candidates = sorted([f for f in instruments_on_disk if f.startswith(found) and f[len(found):].isdigit()])
            if candidates:
                final_base = candidates[0]
            else:
                # Si on arrive ici, c'est que l'instrument trouvé par substitution 
                # (ex: 'SIb') n'existe vraiment pas sur le disque.
                _set_error(f"Incohérence : {found} introuvable sur le disque.")
                return None

        return final_base # Retourne le nom de base sans extension

    return None

def findPopularInstrument(track_path, target_instrument, instruments_on_disk, trackname):
    # On s'assure d'avoir les infos même pour les virtuels
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