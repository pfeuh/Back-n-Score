#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pdf2image import convert_from_path
# On garde les mêmes paramètres : 150 DPI, JPEG qualité 80

import os

import glob

def trackPdfToJpg(pdf_path, bw_flag=False):
    """Gère la conversion d'un PDF en série de JPG si nécessaire (Stratégie Delta)."""
    base_path = os.path.splitext(pdf_path)[0]
    first_page_jpg = f"{base_path}_p1.jpg"
    
    # Stratégie Delta : mtime(pdf) > mtime(jpg) ?
    is_obsolete = (not os.path.exists(first_page_jpg) or 
                   os.path.getmtime(pdf_path) > os.path.getmtime(first_page_jpg))
    
    if is_obsolete:
        print(f"  [>] Conversion : {os.path.basename(pdf_path)}")
        try:
            # 1. Nettoyage des anciens JPG (fantômes) avant conversion
            for old_jpg in glob.glob(f"{base_path}_p*.jpg"):
                try: os.remove(old_jpg)
                except: pass

            # 2. Conversion
            images = convert_from_path(pdf_path, dpi=150, fmt="jpeg")
            
            # 3. Sauvegarde des pages
            for i, image in enumerate(images):
                output_name = f"{base_path}_p{i+1}.jpg"
                
                # Conversion en niveaux de gris si demandé
                if bw_flag:
                    image = image.convert('L')
                
                image.save(output_name, "JPEG", quality=80, optimize=True)
            
            return True 
        except Exception as e:
            print(f"  [!] Erreur conversion {pdf_path}: {e}")
            
    return False
