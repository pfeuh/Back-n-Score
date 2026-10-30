import csv
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

def format_csv_to_excel(input_csv, output_excel):
    csv_path = Path(input_csv)
    if not csv_path.exists():
        print(f"Erreur : Le fichier CSV '{input_csv}' est introuvable. Lance d'abord extractor.py.")
        return

    # Lecture du CSV pivot
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

    if not rows:
        print("Erreur : Le fichier CSV est vide.")
        return

    header = rows[0]
    data = rows[1:]

    # Création du classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Synthèse Base"

    # Injection des données
    ws.append(header)
    for row in data:
        ws.append(row)

    # --- MISE EN FORME ---
    # 1. Figer les volets (ligne 1 fixe)
    ws.freeze_panes = 'A2'

    # 2. En-têtes verticaux (rotation 90°)
    ws.row_dimensions[1].height = 130
    for col_num in range(1, len(header) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.alignment = Alignment(textRotation=90, horizontal='center', vertical='center')

    # 3. Largeurs de colonnes et centrage des indicateurs
    ws.column_dimensions['A'].width = 35  # Nom du morceau
    
    # Colonnes intermédiaires (X / .) : largeur 3 et centré
    for col_num in range(2, len(header)):
        col_letter = get_column_letter(col_num)
        ws.column_dimensions[col_letter].width = 3
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col_num).alignment = Alignment(horizontal='center', vertical='center')

    # Dernière colonne (Chemin complet)
    last_col_letter = get_column_letter(len(header))
    ws.column_dimensions[last_col_letter].width = 45

    # Sauvegarde du fichier Excel
    wb.save(output_excel)
    print(f"Mise en forme Excel terminée ! Fichier généré : {Path(output_excel).resolve()}")

if __name__ == '__main__':
    default_input = "../server_data/stats.csv"
    default_output = "../server_data/stats.xlsx"
    
    import sys
    input_csv = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_xlsx = sys.argv[2] if len(sys.argv) > 2 else default_output
    format_csv_to_excel(input_csv, output_xlsx)