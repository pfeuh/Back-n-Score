#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse

# Chemins par défaut
DEFAULT_DB_DIR = "/mnt/Data1/Documents/backNScoreData/database"
DEFAULT_SCORES_DIR = "/mnt/Data1/Documents/scores/musescore/Partitions"

def run_moulinette(db_dir=DEFAULT_DB_DIR, scores_dir=DEFAULT_SCORES_DIR, dry_run=False):
    print("=" * 60)
    print("Lancement de la moulinette MuseScore")
    print(f"Database : {db_dir}")
    print(f"Partitions source : {scores_dir}")
    sim_status = "OUI (aucun déplacement)" if dry_run else "NON (déplacement actif)"
    print(f"Mode simulation (Dry-run) : {sim_status}")
    print("=" * 60 + "\n")

    if not os.path.exists(db_dir):
        print(f"[ERREUR] Le dossier database est introuvable : {db_dir}")
        return

    if not os.path.exists(scores_dir):
        print(f"[ERREUR] Le dossier des partitions sources est introuvable : {scores_dir}")
        return

    # Étape 1 : Indexation récursive de tous les fichiers .mscz dans le dossier Partitions
    print("Indexation des fichiers .mscz dans le dossier source...")
    scores_index = {}
    for root, dirs, files in os.walk(scores_dir):
        for file in files:
            if file.lower().endswith(".mscz"):
                # On stocke le nom du fichier en minuscule pour une recherche insensible à la casse si besoin, 
                # ou directement tel quel. Ici on garde le nom exact comme clé.
                scores_index[file] = os.path.join(root, file)
    print(f"-> {len(scores_index)} fichier(s) .mscz trouvé(s).\n")

    stats_found = 0
    stats_moved = 0
    stats_missing = 0
    stats_skipped = 0

    # Étape 2 : Balayage récursif de la database
    for root, dirs, files in os.walk(db_dir):
        if "trackname.txt" in files:
            folder_name = os.path.basename(root)
            target_filename = f"{folder_name}.mscz"
            dest_file_path = os.path.join(root, target_filename)

            print(f"Dossier cible : {folder_name}")
            print(f"  -> Chemin : {root}")

            # Recherche dans notre index récursif
            source_file_path = scores_index.get(target_filename)

            if source_file_path and os.path.exists(source_file_path):
                stats_found += 1
                
                # Vérifie si le fichier est déjà présent dans le dossier de la database
                if os.path.exists(dest_file_path):
                    print("  [INFO] Le fichier existe déjà dans le dossier. Ignoré.")
                    stats_skipped += 1
                else:
                    if dry_run:
                        print(f"  [SIMULATION] Déplacement de '{source_file_path}' vers ce dossier.")
                    else:
                        try:
                            shutil.move(source_file_path, dest_file_path)
                            print("  [SUCCÈS] Fichier déplacé avec succès.")
                            stats_moved += 1
                        except Exception as e:
                            print(f"  [ERREUR] Impossible de déplacer le fichier : {e}")
            else:
                print(f"  [MANQUANT] Fichier '{target_filename}' introuvable dans l'arborescence Partitions.")
                stats_missing += 1
            print("-" * 40)

    # Rapport final
    print("\n" + "=" * 60)
    print("Rapport final :")
    print(f"  - Dossiers avec 'trackname.txt' traités : {stats_found + stats_missing}")
    print(f"  - Fichiers trouvés et déplacés : {stats_moved}")
    print(f"  - Fichiers déjà présents sur place (ignorés) : {stats_skipped}")
    print(f"  - Fichiers introuvables : {stats_missing}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moulinette de déplacement des partitions MuseScore vers la database.")
    parser.add_argument("--dry-run", action="store_true", help="Exécute le script en mode simulation (rapport sans modifier les fichiers).")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_DIR, help="Chemin vers le dossier database.")
    parser.add_argument("--scores", type=str, default=DEFAULT_SCORES_DIR, help="Chemin vers le dossier des partitions source.")
    
    args = parser.parse_args()
    
    run_moulinette(db_dir=args.db, scores_dir=args.scores, dry_run=args.dry_run)