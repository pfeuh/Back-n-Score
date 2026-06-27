#!/usr/bin/python
# -*- coding: utf-8 -*-

VERBOSE = False

import os
#~ import updateDatabase

def checkTrack(instrument_name, track_path):return

def generate_track_tree(database):
    """Scanne la base de données et génère le catalogue plat."""
    print("Scan de la database...")
    tracks = []
    converted_count = 0  # Notre compteur
    
    for root, dirs, files in os.walk(database):
        if "trackname.txt" in files:
            relative_path = os.path.relpath(root, database)
            
            # Vérification des PDF (Sanité avec gestion des voix)
            for f in files:
                if f.endswith(".pdf"):
                    if VERBOSE:
                        print(f)
                    # On retire les 4 derniers caractères (.pdf) sans toucher à la casse
                    instr_key = f[:-4]
                    
                    # 1. Sanité
                    checkTrack(instr_key, relative_path)
            
                    # 2. Moulinette Delta (notre ajout)
                    #~ pdf_full_path = os.path.join(root, f)
                    #~ if trackPdfToJpg(pdf_full_path):
                        #~ converted_count += 1
                    
            # Lecture du titre
            try:
                with open(os.path.join(root, "trackname.txt"), "r", encoding="utf-8") as f:
                    title = f.read().strip()
                tracks.append({"title": title, "location": relative_path})
            except Exception as e:
                print(f"Erreur lecture titre dans {relative_path}: {e}")
                
    return tracks, converted_count

def sortTracks(tracks):
    tracks.sort(key=lambda x: (os.path.dirname(x['location']), x['title']))
    return tracks

if __name__ == "__main__":
    
    DATABASE = "../database"
    
    tracks, converted_count = generate_track_tree(DATABASE)
    
    sortTracks(tracks)
    for item in tracks:
        print(item)
    
    
    
    
    
    