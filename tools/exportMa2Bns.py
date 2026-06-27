#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import unicodedata
from PyPDF2 import PdfWriter

# --- TES FONCTIONS (STRICTES) ---

def remove_accents(input_str):
    """Remove accents from text."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([char for char in nfkd_form if not unicodedata.combining(char)])

def clean_text(text: str) -> str:
    """Nettoie un texte des caractères typographiques et spéciaux."""
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFC", text)
    replacements = {
        "’": "'", "‘": "'", "‛": "'",
        "–": "-", "—": "-", "−": "-",
        "“": '"', "”": '"', "«": '"', "»": '"',
        "\u00A0": " ", "\u202F": " ", "\u200B": "", "\uFEFF": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = ''.join(ch for ch in text if ch.isprintable())
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

def toCamelCase(text):
    """Convert a string to camelCase."""
    SPACE = ' '
    EMPTY_STRING = ''
    text = remove_accents(text).lower()
    text = str(text).replace(SPACE+SPACE, SPACE)
    temp = EMPTY_STRING
    space_flag = False
    text = text.replace("ß","ss")
    for car in text:
        if car in (" /-!,?:+*'’"):
            space_flag = True
        elif car in "().":
            pass
        else:
            if space_flag:
                temp += car.upper()
            else:
                temp += car.lower()
            space_flag = False
    return temp

# --- LOGIQUE DE MIGRATION ---

def merge_pdfs(input_files, output_path):
    writer = PdfWriter()
    try:
        for pdf in sorted(input_files):
            writer.append(pdf)
        with open(output_path, "wb") as f:
            writer.write(f)
        return True
    except Exception as e:
        print(f"      [!] Erreur fusion : {e}")
        return False

def migrate_book(book_path, dest_path):
    tracklist_file = os.path.join(book_path, "tracklist.txt")
    if not os.path.exists(tracklist_file): return

    print(f"\n>>> Migration du livre : {os.path.basename(book_path)}")
    
    with open(tracklist_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('#'): continue
        
        # 1. Nettoyage et génération du slug
        proper_title = line.split('#')[0].strip()
        cleaned_title = clean_text(proper_title) # On nettoie la typo avant
        slug = toCamelCase(cleaned_title)        # On génère le camelCase
        
        track_dir = os.path.join(dest_path, slug)
        os.makedirs(track_dir, exist_ok=True)

        with open(os.path.join(track_dir, "trackname.txt"), "w", encoding="utf-8") as f:
            f.write(proper_title)

        print(f"  + {proper_title} -> {slug}")

        # 2. SCORES (Partitions)
        score_root = os.path.join(book_path, "score")
        if os.path.exists(score_root):
            for inst in os.listdir(score_root):
                inst_dir = os.path.join(score_root, inst)
                if not os.path.isdir(inst_dir): continue
                
                # Collecte des fichiers PDF commençant par le slug
                pages = []
                for f in os.listdir(inst_dir):
                    f_lower = f.lower()
                    if f_lower.startswith(slug.lower()) and f_lower.endswith(".pdf"):
                        rest = f_lower[len(slug):-4]
                        if rest == "" or rest.isdigit():
                            pages.append(os.path.join(inst_dir, f))
                
                if pages:
                    merge_pdfs(pages, os.path.join(track_dir, f"{inst}.pdf"))

        # 3. MP3 (Audio)
        mp3_root = os.path.join(book_path, "mp3")
        if os.path.exists(mp3_root):
            for mp3_type in os.listdir(mp3_root):
                type_dir = os.path.join(mp3_root, mp3_type)
                if not os.path.isdir(type_dir): continue
                src_mp3 = os.path.join(type_dir, f"{slug}.mp3")
                if os.path.exists(src_mp3):
                    shutil.copy2(src_mp3, os.path.join(track_dir, f"{mp3_type}.mp3"))

def run_migration(source_db, target_db):
    for root, dirs, files in os.walk(source_db):
        if "tracklist.txt" in files:
            rel_path = os.path.relpath(root, source_db)
            if rel_path == ".":
                dest_book_path = target_db
            else:
                # On utilise toCamelCase pour les dossiers aussi
                parts = [toCamelCase(clean_text(p)) for p in rel_path.split(os.sep)]
                dest_book_path = os.path.join(target_db, *parts)
            
            migrate_book(root, dest_book_path)

if __name__ == "__main__":
    SOURCE_DB = "/mnt/Data1/Documents/www/free/shared/repertoires/home"
    TARGET_DB = "../test_database"
    run_migration(SOURCE_DB, TARGET_DB)
    print("\n[FIN] Migration terminée.")