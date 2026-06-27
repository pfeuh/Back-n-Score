#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re  # On importe le module pour le nettoyage des chiffres

tous_les_morceaux = []
instruments_trouves = set()

def createJsonTrackTree(bns_database, tree_name, skeleton_name, page_name, instruments_name, temp_name):
    # on créée à la fois le track tree et la liste des instruments.
    for root, dirs, files in os.walk(bns_database):
        # RÈGLE D'OR : Pas de trackname, pas de morceau.
        if "trackname.txt" in files:
            try:
                with open(os.path.join(root, "trackname.txt"), "r", encoding="utf-8") as f_text:
                    titre = f_text.read().strip()
            except Exception:
                continue
                
            if not titre: continue 

            rel_path = os.path.relpath(root, bns_database)
            parts = rel_path.split(os.sep)
            parents = parts[:-1] 

            # --- LE SCAN DES INSTRUMENTS (NETTOYÉ) ---
            for f in files:
                if f.lower().endswith(".pdf"):
                    nom_fichier = os.path.splitext(f)[0]
                    
                    # NETTOYAGE : 
                    # On enlève les chiffres de fin SEULEMENT s'il y en a 2 ou plus (ex: 02, 03)
                    # On garde le chiffre seul (ex: trompette2)
                    nom_propre = re.sub(r'\d{2,}$', '', nom_fichier)
                    
                    if nom_propre:
                        instruments_trouves.add(nom_propre)

            tous_les_morceaux.append({
                "title": titre,
                "location": rel_path,
                #~ "parents": parents
            })

    # Sauvegarde du track tree, human readable
    with open(temp_name, "w", encoding="utf-8") as f_json:
        json.dump(tous_les_morceaux, f_json, indent=4, ensure_ascii=False)

    # Sauvegarde du track tree, compacté
    with open(tree_name, "w", encoding="utf-8") as f_json:
        json.dump(tous_les_morceaux, f_json, separators=(",", ":"), ensure_ascii=False)

    # Sauvegarde de la liste des instruments (enlever les doublons et trier)
    with open(instruments_name, "w", encoding="utf-8") as f_inst:
        json.dump(sorted(list(instruments_trouves)), f_inst, indent=0, ensure_ascii=False)
        
    # inclusion du tree dans la page client.htm
    #~ text = open(skeleton_name).read(-1)
    #~ print(text)
    #~ text = text.replace("#TREE#", open(tree_name).read(-1))
    #~ print(text)
    #~ open(page_name, "w", encoding="utf-8").write(text)
    
    text = open(skeleton_name).read(-1)
    tree_json = open(tree_name, encoding="utf-8").read()
    text = text.replace("#TREE#", tree_json)
    open(page_name, "w", encoding="utf-8").write(text)

    print(f"Génération faite : {len(tous_les_morceaux)} morceaux et {len(instruments_trouves)} instruments trouvés.")
    
if __name__ == '__main__':

    BNS_DATABASE = "/mnt/Data1/Documents/backNScore/database"
    TREE_NAME = "track_tree.json"
    SKELETON_NAME = "testtracktreeskeleton.htm"
    PAGE_NAME = "test_track_tree.htm"
    INSTRUMENTS_NAME = "instrument.json"
    TEMP_NAME = "../temp/track_tree.json"

    createJsonTrackTree(BNS_DATABASE, TREE_NAME, SKELETON_NAME, PAGE_NAME, INSTRUMENTS_NAME, TEMP_NAME)

    
    