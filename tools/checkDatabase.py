#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def check_database(root_path, instruments):
    print(f"=== Diagnostic de la base : {root_path} ===\n")
    errors_found = 0

    for root, dirs, files in os.walk(root_path):
        rel_path = os.path.relpath(root, root_path)
        if rel_path == ".": continue

        is_track = "trackname.txt" in files
        
        if is_track:
            for f in files:
                name, ext = os.path.splitext(f)
                
                if ext == ".pdf":
                    # 1. Match direct (ex: trombone)
                    if name in instruments:
                        continue
                    
                    # 2. Pupitres supplémentaires (ex: trombone2)
                    # On vérifie si le dernier caractère est un chiffre de pupitre
                    # et si la racine (le nom sans le chiffre) est dans ton dico
                    elif len(name) > 1 and f[len(name)-1] in "23456789" and name[:-1] in instruments:
                        continue
                    
                    else:
                        print(f"[?] INSTRUMENT INCONNU : '{rel_path}/{f}'")
                        errors_found += 1
                
                elif f == "trackname.txt" or ext == ".mp3":
                    continue
                else:
                    print(f"[*] FICHIER INTRUS : '{rel_path}/{f}'")
                    errors_found += 1

    print(f"\n=== Diagnostic terminé : {errors_found} anomalies détectées. ===")

if __name__ == "__main__":

    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    scripts_path = os.path.join(parent_dir, "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)

    from instruments import INSTRUMENTS, VIRTUAL_INSTRUMENTS

    DATABASE_ROOT = "../test_database"
    instruments = list(INSTRUMENTS.keys()) + list(VIRTUAL_INSTRUMENTS.keys())
    
    print(f"DEBUG: Nombre d'instruments chargés : {len(instruments)}")
    print(f"DEBUG: 10 premiers instruments : {instruments[:10]}")
    
    check_database(DATABASE_ROOT, instruments)


