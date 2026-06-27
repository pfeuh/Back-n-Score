#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pdf2image import convert_from_path

# Configuration
DATABASE_ROOT = './DATABASE'
IMAGE_FORMAT = 'JPEG'
DPI = 150 # Qualité suffisante pour tablette sans être trop lourd

def process_directory(path, dry_run = False):
    # Vérifie si le fichier trackname.txt existe dans le répertoire actuel
    if not os.path.exists(os.path.join(path, 'trackname.txt')):
        return

    if not dry_run:
        sys.stdout.write(f"{path}\n    ")
    else:
        sys.stdout.write(f"DRY_RUN {path}\n    ")
    
    # Liste tous les fichiers du répertoire
    files = os.listdir(path)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(path, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        
        try:
            # Conversion du PDF en liste d'images PIL
            # On utilise thread_count pour accélérer si le CPU a plusieurs coeurs
            pages = convert_from_path(pdf_path, dpi=DPI)

            for i, page in enumerate(pages):
                # Gestion du nommage : filename.jpeg pour la p1, filename02.jpeg pour la suite
                if i == 0:
                    output_name = f"{base_name}.jpeg"
                else:
                    output_name = f"{base_name}{i+1:02d}.jpeg"
                
                output_path = os.path.join(path, output_name)
                
                # Sauvegarde de l'image
                if not dry_run:
                    page.save(output_path, IMAGE_FORMAT)
                sys.stdout.write(output_name)
                sys.stdout.write(" ")
                
        except Exception as e:
            print(f"Erreur lors de la conversion de {pdf_file} : {e}")

    sys.stdout.write('\n')

def run_moulinette(database, dry_run=False):
    # Parcours récursif de DATABASE 
    for root, dirs, files in os.walk(database, dry_run):
        process_directory(root, dry_run)

if __name__ == "__main__":

    DATABASE = "/mnt/Data1/Documents/backNScore/database"
    DRY_RUN = False

    if os.path.exists(DATABASE):
        run_moulinette(DATABASE, DRY_RUN)
        print("\nTraitement terminé !")
    else:
        print(f"Erreur : Le répertoire {DATABASE} est introuvable.")
    