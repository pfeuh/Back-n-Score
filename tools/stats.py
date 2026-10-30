import os
import json
import csv
import sys
from pathlib import Path

# Ajout du dossier parent au path pour pouvoir importer instruments.py
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir / "../scripts"))

try:
    from instruments import INSTRUMENTS, VIRTUAL_INSTRUMENTS, getFirstVoice
except ImportError:
    INSTRUMENTS = {}
    VIRTUAL_INSTRUMENTS = {}
    def getFirstVoice(name):
        return name

def extract_to_csv(root_dir, output_csv):
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"Erreur : Le dossier '{root_dir}' n'existe pas ou la clé USB n'est pas connectée.")
        return

    # Chargement dynamique des types de MP3 depuis le fichier JSON externe
    json_path = current_dir / "../server_data/mp3_types.json"
    mp3_types = ['backtrack.mp3', 'melody.mp3', 'slowed-down.mp3']
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, list) and content:
                    mp3_types = content
        except Exception as e:
            print(f"Avertissement : Impossible de charger {json_path} ({e}), utilisation des valeurs par défaut.")
    else:
        print(f"Avertissement : Fichier {json_path} introuvable, utilisation des valeurs par défaut.")

    # Recherche de tous les dossiers de morceaux
    track_folders = []
    for path in root_path.rglob('*'):
        if path.is_dir() and ((path / 'trackname.txt').exists() or path.name.startswith('Track_')):
            if path not in track_folders:
                track_folders.append(path)

    instruments_list = ['DO', 'SIb', 'MIb', 'FA', 'SOL']
    results = []

    print(f"Analyse en cours de {len(track_folders)} dossiers de morceaux sur la base...")

    for track_dir in track_folders:
        # Nom du morceau
        trackname_file = track_dir / 'trackname.txt'
        nom_morceau = track_dir.name
        if trackname_file.exists():
            try:
                with open(trackname_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        nom_morceau = content
            except Exception as e:
                print(f"Avertissement : Impossible de lire {trackname_file} ({e})")

        files = [f for f in track_dir.iterdir() if f.is_file()]
        file_names = [f.name for f in files]
        file_stems = [f.stem for f in files]

        # Présence des MP3
        mp3_presence = {}
        for mp3 in mp3_types:
            mp3_presence[mp3] = "X" if mp3 in file_names else "."

        # Présence des instruments par tonalité
        inst_presence = {}
        for inst_ton in instruments_list:
            found = False
            target_ton = inst_ton
            for stem in file_stems:
                clean_name = getFirstVoice(stem)
                meta = INSTRUMENTS.get(clean_name) or VIRTUAL_INSTRUMENTS.get(clean_name)
                if meta and meta[0] == target_ton:
                    found = True
                    break
            inst_presence[inst_ton] = "X" if found else "."

        # Présence du projet MuseScore (.mscz)
        has_mscz = "X" if any(fn.endswith('.mscz') for fn in file_names) else "."

        # Chemin complet
        chemin_complet = str(track_dir.resolve())

        results.append({
            'nom': nom_morceau,
            'mp3': mp3_presence,
            'inst': inst_presence,
            'mscz': has_mscz,
            'chemin': chemin_complet
        })

    # Tri alphabétique simple
    results.sort(key=lambda x: x['nom'])

    # Écriture du fichier CSV pivot (correction du bug de la liste imbriquée)
    header = ['Track name'] + mp3_types + instruments_list + ['musescore', 'Path']
    
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(header)
        for r in results:
            row = [r['nom']] + \
                  [r['mp3'][m] for m in mp3_types] + \
                  [r['inst'][i] for i in instruments_list] + \
                  [r['mscz']] + \
                  [r['chemin']]
            writer.writerow(row)

    print(f"Extraction terminée ! Fichier CSV généré : {Path(output_csv).resolve()}")

if __name__ == '__main__':
    default_path = "/mnt/Data1/Documents/backNScoreData/database/people/pierreFaller"
    #~ default_path = "/mnt/Data1/Documents/backNScoreData/database/"
    default_output = "../server_data/stats.csv"
    
    racine = sys.argv[1] if len(sys.argv) > 1 else default_path
    output = sys.argv[2] if len(sys.argv) > 2 else default_output
    extract_to_csv(racine, output)
    
    default_excel_output = "../server_data/stats.xlsx"
    from stats2csv import format_csv_to_excel
    format_csv_to_excel(output, default_excel_output)
    
    default_html_output = "../server_data/stats.html"
    from stats2html import generate_html_from_csv
    generate_html_from_csv(output, default_html_output)