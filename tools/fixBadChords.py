import os
from pathlib import Path
import zipfile
import shutil

def fix_mscz_files(target_dir, temp_dir):
    target_path = Path(target_dir)
    temp_path = Path(temp_dir)
    
    mscz_files = list(target_path.glob("**/*.mscz"))
    print(f"Scan et traitement de {len(mscz_files)} fichiers .mscz (remplacement par 'M7', sans .bak)...")
    
    fixed_count = 0
    for file_path in mscz_files:
        try:
            # Dossier de travail temporaire dédié
            file_temp = temp_path / "migration_mscz"
            if file_temp.exists():
                shutil.rmtree(file_temp)
            file_temp.mkdir(parents=True, exist_ok=True)
            
            # 1. Extraction du .mscz (ZIP)
            with zipfile.ZipFile(file_path, "r") as z:
                z.extractall(file_temp)
                
            # Recherche du fichier .mscx interne
            mscx_files = list(file_temp.glob("*.mscx"))
            if not mscx_files:
                continue
            mscx_path = mscx_files[0]
            
            # 2. Lecture et vérification du contenu
            content = mscx_path.read_text(encoding="utf-8")
            
            if "7M" in content:
                # Remplacement direct de '7M' par 'M7' (sans .bak)
                new_content = content.replace("7M", "M7")
                mscx_path.write_text(new_content, encoding="utf-8")
                
                # 3. Recompression propre au format .mscz
                with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as z_out:
                    for item in file_temp.glob("**/*"):
                        if item.is_file():
                            arcname = item.relative_to(file_temp)
                            z_out.write(item, arcname)
                            
                print(f"[CORRIGÉ -> M7] {file_path}")
                fixed_count += 1
                
        except Exception as e:
            print(f"[ERREUR] Sur {file_path}: {e}")
            
    print(f"\nMigration terminée ! {fixed_count} fichiers convertis en 'M7'.")

if __name__ == "__main__":
    target_directory = "/mnt/Data1/Documents/backNScoreData/database"
    temp_directory = "../temp"
    fix_mscz_files(target_directory, temp_directory)