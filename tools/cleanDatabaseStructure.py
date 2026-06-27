#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"

def cleanDatabaseStructure():
    print(f"Nettoyage de la structure dans : {DATABASE_DIR}")
    deleted_count = 0

    # On utilise topdown=False pour traiter les dossiers enfants avant les parents
    for root, dirs, files in os.walk(DATABASE_DIR, topdown=False):
        if "trackname.txt" in files:
            # Vérification : est-ce que ce dossier contient des sous-dossiers 
            # qui sont eux-mêmes des tracks ?
            has_subtracks = False
            for d in dirs:
                sub_path = os.path.join(root, d)
                if os.path.exists(os.path.join(sub_path, "trackname.txt")):
                    has_subtracks = True
                    break
            
            if has_subtracks:
                file_to_remove = os.path.join(root, "trackname.txt")
                print(f" [!] Conflit détecté : {root}")
                print(f"     -> C'est un BOOK (contient des sous-morceaux).")
                print(f"     -> Suppression du trackname.txt parasite.")
                #~ os.remove(file_to_remove)
                deleted_count += 1

    print(f"\nNettoyage terminé. {deleted_count} fichier(s) parasite(s) supprimé(s).")

if __name__ == "__main__":
    
    cleanDatabaseStructure()
