import os
from pathlib import Path
import zipfile
import sys

def scan_mscz_folder(root_dir, pattern):
    root_path = Path(root_dir)
    # Recherche récursive de tous les fichiers .mscz
    mscz_files = list(root_path.glob("**/*.mscz"))
    
    print(f"Scan de {len(mscz_files)} fichiers .mscz...\n")
    
    found_count = 0
    for file_path in mscz_files:
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                # Trouve le fichier .mscx à l'intérieur du zip
                mscx_name = next((name for name in z.namelist() if name.endswith(".mscx")), None)
                if mscx_name:
                    content = z.read(mscx_name).decode("utf-8", errors="ignore")
                    
                    # On cherche la trace du 7M (dans les balises text ou les attributs d'accords)
                    # Ajuste le pattern si besoin selon la façon exacte dont c'est stocké dans le .mscx
                    if pattern in content:
                        print(f"[TROUVÉ] {file_path}")
                        found_count += 1
        except Exception as e:
            print(f"[ERREUR] Impossible de lire {file_path}: {e}")

    print(f"\nTerminé ! {found_count} fichiers contiennent encore du '7M'.")

if __name__ == "__main__":
    # Remplace par le dossier racine de ta base de données de partitions
    target_directory = "/mnt/Data1/Documents/backNScoreData/database" 
    pattern = "7M"
    if len(sys.argv) > 1:
        pattern = sys.argv[1]

    scan_mscz_folder(target_directory, pattern)