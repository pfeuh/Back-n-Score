#!/usr/bin/python
# -*- coding: utf-8 -*-

def getScore(instrument, location):
    folder = os.path.join(ROOT_DIR, unquote(p).lstrip('/'))
    if not os.path.exists(folder):
        abort(404)

    files = os.listdir(folder)

    # --- ÉTAPE 1 : L'instrument direct ---
    # Si toto.pdf existe, on l'envoie et c'est terminé.
    if f"{instrument}.pdf" in files:
        return os.path.join(folder, f"{instrument}.pdf")

    # --- ÉTAPE 2 : Les RÈGLES ---
    # Si toto est une clef de REGLES...
    regles = SUBS_DATA.get("REGLES", {})
    if instrument in regles:
        # On cherche le premier item de la liste qui a un fichier item.pdf
        for substitut in regles[instrument]:
            if f"{substitut}.pdf" in files:
                return os.path.join(folder, f"{substitut}.pdf")

    # --- ÉTAPE 3 : Les FAMILLES ---
    # Si toto est dans les items d'une famille...
    familles = SUBS_DATA.get("FAMILLES", {})
    for nom_famille, membres in familles.items():
        if instrument in membres:
            # On essaie de substituer par le premier item de la famille qui a un fichier .pdf
            for membre in membres:
                # Optionnel : on peut ignorer 'instrument' lui-même puisqu'on sait déjà qu'il n'existe pas
                if f"{membre}.pdf" in files:
                    return os.path.join(folder, f"{membre}.pdf")

    # --- ÉTAPE 4 : FIN ---
    # Si on n'a toujours rien trouvé, on ne trouvera plus rien.
    abort(404)

# ----------------------------
# TREE (UNCHANGED - implicit via templates)
# ----------------------------
def get_track_name(folder_path):
    txt_path = os.path.join(folder_path, "trackname.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            pass
    return os.path.basename(folder_path)

if __name__ == '__main__':

    """ U N I T A R Y    T E S T ***---"""

    from loadJson import loadJson 

    config = loadJson("config.json")
    
    print(config)


