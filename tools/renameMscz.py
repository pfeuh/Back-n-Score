#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Chemin par défaut de la database
DEFAULT_DB_DIR = "/mnt/Data1/Documents/backNScoreData/database"

def run_rename_moulinette(db_dir=DEFAULT_DB_DIR):
    print("=" * 60)
    print("Lancement de la moulinette de renommage (.mscz -> score.mscz)")
    print(f"Database : {db_dir}")
    print("Mode : Actif (renommage direct avec vérification des doublons .mscz)")
    print("=" * 60 + "\n")

    if not os.path.exists(db_dir):
        print(f"[ERREUR] Le dossier database est introuvable : {db_dir}")
        return

    stats_processed = 0
    stats_renamed = 0
    stats_already_ok = 0
    stats_errors = 0

    # Balayage récursif de la database
    for root, dirs, files in os.walk(db_dir):
        # On ne traite que les dossiers contenant un fichier trackname.txt
        if "trackname.txt" in files:
            # Recherche de tous les fichiers .mscz dans ce dossier uniquement
            mscz_files = [f for f in files if f.lower().endswith(".mscz")]

            if len(mscz_files) > 1:
                folder_name = os.path.basename(root)
                print(f"Dossier cible : {folder_name}")
                print(f"  -> Chemin : {root}")
                print(f"  [ERREUR CRITIQUE] Plusieurs fichiers .mscz trouvés dans ce dossier ({mscz_files}). Arrêt immédiat.")
                sys.exit(1)
            elif len(mscz_files) == 0:
                folder_name = os.path.basename(root)
                print(f"Dossier cible : {folder_name}")
                print(f"  -> Chemin : {root}")
                print("  [INFO] Aucun fichier .mscz trouvé dans ce dossier.")
                print("-" * 40)
            else:
                file = mscz_files[0]
                
                if file == "score.mscz":
                    stats_already_ok += 1
                else:
                    folder_name = os.path.basename(root)
                    print(f"Dossier cible : {folder_name}")
                    print(f"  -> Chemin : {root}")
                    stats_processed += 1
                    old_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(root, "score.mscz")
                    print(f"  -> Renommer : '{file}' -> 'score.mscz'")

                    if os.path.exists(new_file_path):
                        print("  [AVERTISSEMENT] Un fichier 'score.mscz' existe déjà. Renommage ignoré.")
                    else:
                        try:
                            os.rename(old_file_path, new_file_path)
                            print("  [SUCCÈS] Fichier renommé en score.mscz.")
                            stats_renamed += 1
                        except Exception as e:
                            print(f"  [ERREUR] Impossible de renommer le fichier : {e}")
                            stats_errors += 1

                    print("-" * 40)

    # Rapport final
    print("\n" + "=" * 60)
    print("Rapport final :")
    print(f"  - Fichiers renommés en score.mscz : {stats_renamed}")
    print(f"  - Fichiers déjà nommés score.mscz (silencieux) : {stats_already_ok}")
    print(f"  - Erreurs rencontrées : {stats_errors}")
    print("=" * 60)

if __name__ == "__main__":
    run_rename_moulinette()