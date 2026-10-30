#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path

# Tentative d'import pour la manipulation des PDF
try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        PdfMerger = None

def separated2global_core(source, target, target_filename, instrument, mp3_types):
    """
    Parcourt le dossier source, extrait et concatène uniquement les PDF correspondant
    strictement à l'instrument choisi (nom_de_l_instrument.pdf) par ordre alphabétique,
    et classe les MP3 correspondants dans des sous-dossiers par type.
    """
    source_path = Path(source)
    target_path = Path(target)

    # 1. Création du dossier de sortie global s'il n'existe pas
    target_path.mkdir(parents=True, exist_ok=True)

    pdf_files_to_merge = []
    mp3_extracted_count = 0

    print(f"--- Début du traitement ---")
    print(f"Source : {source_path}")
    print(f"Cible : {target_path}")
    print(f"Instrument cible : {instrument}")
    print(f"Types MP3 retenus : {mp3_types}")

    # 2. Parcours récursif du dossier source à la recherche de 'trackname.txt'
    for root, dirs, files in os.walk(source_path):
        root_p = Path(root)
        
        if "trackname.txt" in files:
            # Lecture du nom du morceau
            trackname_file = root_p / "trackname.txt"
            try:
                with open(trackname_file, "r", encoding="utf-8") as tf:
                    track_title = tf.read().strip()
            except Exception as e:
                print(f"Erreur de lecture pour {trackname_file}: {e}")
                continue

            if not track_title:
                continue

            print(f"\nMorceau trouvé : '{track_title}' dans {root_p.name}")

            # --- Traitement des MP3 ---
            for file in files:
                if file.lower().endswith(".mp3"):
                    mp3_type_name = Path(file).stem  # Ex: "backtrack", "melody", ou le nom de l'instrument

                    is_general_type = mp3_type_name in mp3_types
                    is_target_instrument = (mp3_type_name == instrument)

                    if is_general_type or is_target_instrument:
                        src_mp3 = root_p / file
                        
                        # Création d'un sous-dossier dédié pour ce type de MP3 (ex: target/backtrack/)
                        sub_mp3_dir = target_path / mp3_type_name
                        sub_mp3_dir.mkdir(parents=True, exist_ok=True)

                        # Nom du fichier MP3 dans son dossier (on peut garder juste track_title.mp3 ou track_title_type.mp3)
                        # Gardons juste le titre du morceau puisque le dossier indique déjà la catégorie, ou optionnellement le type.
                        new_mp3_name = f"{track_title}.mp3"
                        new_mp3_name = "".join(c for c in new_mp3_name if c.isalnum() or c in (' ', '_', '-', '.')).strip()
                        
                        dest_mp3 = sub_mp3_dir / new_mp3_name
                        
                        try:
                            shutil.copy2(src_mp3, dest_mp3)
                            print(f"  [MP3 Copié] {file} -> {mp3_type_name}/{new_mp3_name}")
                            mp3_extracted_count += 1
                        except Exception as e:
                            print(f"  [Erreur MP3] Impossible de copier {file}: {e}")

            # --- Collecte des PDF ---
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_name_stem = Path(file).stem
                    if pdf_name_stem == instrument:
                        pdf_files_to_merge.append(root_p / file)

    # 3. Concaténation des PDF par ordre alphabétique (case insensitive)
    if pdf_files_to_merge:
        if PdfMerger is None:
            print("\n[AVERTISSEMENT] La bibliothèque 'pypdf' ou 'PyPDF2' n'est pas installée. Impossible de fusionner les PDF.")
            print("Installe-la avec la commande : pip install pypdf")
        else:
            pdf_files_to_merge.sort(key=lambda p: p.name.lower())

            output_pdf_name = f"{target_filename}_{instrument}.pdf"
            output_pdf_path = target_path / output_pdf_name

            merger = PdfMerger()
            try:
                for pdf_file in pdf_files_to_merge:
                    merger.append(str(pdf_file))
                    print(f"  [PDF Ajouté] {pdf_file.name}")

                merger.write(str(output_pdf_path))
                merger.close()
                print(f"\n[Succès] PDF global généré : {output_pdf_path}")
            except Exception as e:
                print(f"\n[Erreur PDF] Erreur lors de la fusion des PDF : {e}")
                if merger:
                    merger.close()
    else:
        print(f"\n[Info] Aucun fichier PDF correspondant à l'instrument '{instrument}' n'a été trouvé à fusionner.")

    print(f"\n--- Traitement terminé. {mp3_extracted_count} MP3 traités. ---")