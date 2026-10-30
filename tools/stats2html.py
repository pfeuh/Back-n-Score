import csv
from pathlib import Path
import html

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def generate_header_images(header, output_dir):
    """Génère des images PNG verticales pour chaque en-tête via Pillow."""
    img_dir = Path(output_dir) / "assets" / "headers"
    img_dir.mkdir(parents=True, exist_ok=True)
    
    header_images = {}
    
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "arialbd.ttf",
        "arial.ttf"
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                font = ImageFont.truetype(fp, 13)
                break
            except:
                pass
    if font is None and PIL_AVAILABLE:
        font = ImageFont.load_default()

    for i, col in enumerate(header):
        if i == 0 or i == len(header) - 1:
            continue
            
        filename = f"col_{i}.png"
        file_path = img_dir / filename
        header_images[i] = f"assets/headers/{filename}"
        
        if not PIL_AVAILABLE:
            continue
            
        dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), col, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        pad = 4
        # On contraint la largeur de l'image à 16px max pour s'ajuster parfaitement aux cellules
        img_w = 16
        img_h = w + pad * 2
        
        text_img = Image.new('RGBA', (w + pad*2, h + pad*2), (51, 51, 51, 255))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((pad - bbox[0], pad - bbox[1]), col, fill=(255, 255, 255, 255), font=font)
        
        rotated = text_img.rotate(90, expand=True)
        # Redimensionnement propre à 16px de large si nécessaire
        if rotated.width != 16:
            rotated = rotated.resize((16, img_h), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        rotated.save(file_path)

    return header_images

def generate_html_from_csv(input_csv, output_html):
    csv_path = Path(input_csv)
    if not csv_path.exists():
        print(f"Erreur : Le fichier CSV '{input_csv}' est introuvable. Lance d'abord extractor.py.")
        return

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

    if not rows:
        print("Erreur : Le fichier CSV est vide.")
        return

    header = rows[0]
    data = rows[1:]

    output_path = Path(output_html)
    output_dir = output_path.parent
    
    header_imgs = {}
    if PIL_AVAILABLE:
        header_imgs = generate_header_images(header, output_dir)

    html_content = [
        "<!DOCTYPE html>",
        "<html lang='fr'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "  <title>Back'n Score</title>",
        "  <style>",
        "    :root {",
        "      --bg: #121212;",
        "      --card: #1e1e1e;",
        "      --accent: #3b82f6;",
        "      --text: #e0e0e0;",
        "      --border: #333333;",
        "      --green: #22c55e;",
        "    }",
        "    body { font-family: 'Droid Sans', Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding-top: 95px; }",
        "",
        "    .fixed-header-bar {",
        "      position: fixed;",
        "      top: 0;",
        "      left: 0;",
        "      right: 0;",
        "      background-color: #333333;",
        "      border-bottom: 2px solid var(--border);",
        "      z-index: 100;",
        "      overflow: hidden;",
        "    }",
        "",
        "    .table-container {",
        "      overflow-x: auto;",
        "      background: var(--card);",
        "      border-top: 1px solid var(--border);",
        "    }",
        "",
        "    table {",
        "      border-collapse: separate;",
        "      border-spacing: 0;",
        "      table-layout: fixed;",
        "      width: 100%;",
        "      white-space: nowrap;",
        "    }",
        "    th, td {",
        "      padding: 4px 0;",
        "      border-bottom: 1px solid var(--border);",
        "      border-right: 1px solid var(--border);",
        "      text-align: center;",
        "      box-sizing: border-box;",
        "    }",
        "",
        "    th {",
        "      background-color: #333333;",
        "      color: #ffffff;",
        "      vertical-align: bottom;",
        "      height: 95px;",
        "      padding-bottom: 4px;",
        "    }",
        "    th span { color: #ffffff; font-size: 0.85em; }",
        "    th img { display: block; margin: 0 auto; width: 16px; }",
        "",
        "    /* Strictement 16px pour les colonnes de statut dans l'en-tête et le corps */",
        "    .col-status {",
        "      width: 16px !important;",
        "      min-width: 16px !important;",
        "      max-width: 16px !important;",
        "      text-align: center;",
        "    }",
        "    ",
        "    .col-title {",
        "      text-align: left;",
        "      font-weight: bold;",
        "      padding-left: 4px;",
        "      position: -webkit-sticky;",
        "      position: sticky;",
        "      left: 0;",
        "      background-color: var(--card);",
        "      color: var(--text);",
        "      z-index: 10;",
        "      width: 160px !important;",
        "      min-width: 160px !important;",
        "      max-width: 160px !important;",
        "      overflow: hidden;",
        "    }",
        "    th.col-title {",
        "      background-color: #333333 !important;",
        "      z-index: 50;",
        "      vertical-align: middle;",
        "    }",
        "",
        "    .col-path { text-align: left; padding-left: 4px; font-size: 0.8em; width: 250px !important; min-width: 250px !important; vertical-align: middle; }",
        "    th.col-path { vertical-align: middle; }",
        "    ",
        "    .mark-x { color: var(--green); font-weight: bold; }",
        "    .mark-dot { color: #555; }",
        "    a { color: var(--accent); text-decoration: none; }",
        "    tr:hover td { background: rgba(255,255,255,0.03); }",
        "    tr:hover .col-title { background: #222; }",
        "  </style>",
        "</head>",
        "<body>",
        ""
    ]

    # --- EN-TÊTE FIXE ---
    html_content.append("  <div id='fixedHeader' class='fixed-header-bar'>")
    html_content.append("    <table>")
    html_content.append("      <thead>")
    html_content.append("        <tr>")
    for i, col in enumerate(header):
        col_esc = html.escape(col)
        if i == 0:
            html_content.append(f"          <th class='col-title'><span>{col_esc}</span></th>")
        elif i == len(header) - 1:
            html_content.append(f"          <th class='col-path'><span>{col_esc}</span></th>")
        else:
            if i in header_imgs:
                html_content.append(f"          <th class='col-status'><img src='{header_imgs[i]}' alt='{col_esc}'></th>")
            else:
                html_content.append(f"          <th class='col-status'><span>{col_esc}</span></th>")
    html_content.extend([
        "        </tr>",
        "      </thead>",
        "    </table>",
        "  </div>"
    ])

    # --- CORPS DU TABLEAU ---
    html_content.append("  <div id='mainContainer' class='table-container'>")
    html_content.append("    <table>")
    html_content.append("      <tbody>")

    for row in data:
        html_content.append("        <tr>")
        for i, val in enumerate(row):
            val_str = val.strip()
            val_esc = html.escape(val_str)
            
            if i == 0:
                html_content.append(f"          <td class='col-title'>{val_esc}</td>")
            elif i == len(header) - 1:
                clean_path = val_str
                if clean_path.startswith("file://"):
                    clean_path = clean_path[7:]
                if "database/" in clean_path:
                    clean_path = clean_path.split("database/")[-1]
                elif "backNScoreData/" in clean_path:
                    clean_path = clean_path.split("backNScoreData/")[-1]
                
                clean_path_esc = html.escape(clean_path)
                html_content.append(f"          <td class='col-path'><a href='{val_esc}'>{clean_path_esc}</a></td>")
            else:
                if val_str.upper() == 'X':
                    cell_html = "<span class='mark-x'>X</span>"
                else:
                    cell_html = "<span class='mark-dot'>•</span>"
                html_content.append(f"          <td class='col-status'>{cell_html}</td>")
        html_content.append("        </tr>")

    html_content.extend([
        "      </tbody>",
        "    </table>",
        "  </div>",
        "",
        "  <!-- Synchronisation du scroll horizontal -->",
        "  <script>",
        "    var mainC = document.getElementById('mainContainer');",
        "    var headF = document.getElementById('fixedHeader');",
        "    mainC.onscroll = function() {",
        "      headF.scrollLeft = mainC.scrollLeft;",
        "    };",
        "  </script>",
        "</body>",
        "</html>"
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(html_content))

    print(f"Page Web réalignée (16px stricts) générée : {output_path.resolve()}")

if __name__ == '__main__':
    default_input = "../server_data/stats.csv"
    default_output = "../server_data/stats.html"
    
    import sys
    input_csv = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_html = sys.argv[2] if len(sys.argv) > 2 else default_output
    generate_html_from_csv(input_csv, output_html)