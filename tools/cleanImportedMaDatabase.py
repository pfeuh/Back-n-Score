#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-

import os
import re
import subprocess

def extraire_groupe(nom_fichier):
    """
    Sépare strictement les 2 derniers chiffres (page) du reste (pupitre).
    Exemple : "trompette203" -> ("trompette2", "03")
    Exemple : "trompette02"  -> ("trompette", "02")
    Exemple : "trompette2"   -> ("trompette2", "01")
    """
    # On cherche exactement 2 chiffres ou plus à la fin du nom
    # On utilise (\d{2,})$ pour capturer la fin
    # Et ^(.+?) pour capturer TOUT ce qui précède avant ces deux chiffres
    match = re.search(r"^(.+)(\d{2})$", nom_fichier)
    
    if match:
        pupitre = match.group(1)
        page = match.group(2)
        return pupitre, page
    else:
        # Si on n'a pas 2 chiffres à la fin, le nom entier est le pupitre
        return nom_fichier, "01"

def fusionnerPages(chemin_dossier, dry_run_flag):
    files = [f for f in os.listdir(chemin_dossier) if f.lower().endswith(".pdf")]
    if not files:
        return

    # Groupage par pupitre
    groupes = {}
    for f in files:
        nom_sans_ext = os.path.splitext(f)[0]
        pupitre, page = extraire_groupe(nom_sans_ext)
        
        if pupitre not in groupes:
            groupes[pupitre] = []
        groupes[pupitre].append({'file': f, 'page': page})

    for pupitre, infos in groupes.items():
        # On ne fusionne que s'il y a plusieurs fichiers pour le même pupitre
        if len(infos) > 1:
            # Tri par numéro de page
            infos.sort(key=lambda x: x['page'])
            fichiers_tries = [x['file'] for x in infos]
            
            cible = os.path.join(chemin_dossier, f"{pupitre}.pdf")
            sources = [os.path.join(chemin_dossier, f) for f in fichiers_tries]

            print(f"\n[+] ACTION : Fusion de '{pupitre}' ({len(fichiers_tries)} fichiers)")
            print(f"    Ordre : {fichiers_tries}")
            
            if not dry_run_flag:
                try:
                    temp_output = cible + ".tmp"
                    # Appel à pdfunite (doit être installé : sudo apt install poppler-utils)
                    subprocess.run(["pdfunite"] + sources + [temp_output], check=True)
                    
                    # Remplacement par le fichier fusionné
                    os.replace(temp_output, cible)
                    
                    # Suppression des sources sauf le fichier final s'il existait déjà
                    for f_info in infos:
                        path_orig = os.path.join(chemin_dossier, f_info['file'])
                        if path_orig != cible:
                            os.remove(path_orig)
                            print(f"    Supprimé : {f_info['file']}")
                    
                    print(f"    Succès : {pupitre}.pdf créé et nettoyé.")
                except Exception as e:
                    print(f"    ERREUR CRITIQUE sur {pupitre} : {e}")

def pfdPages2Book(BNS_DATABASE, dry_run_flag=True):
    if dry_run_flag:
        print("MODE : SIMULATION (Aucune modification réelle)\n")

    for root, dirs, files in os.walk(BNS_DATABASE):
        if "trackname.txt" in files:
            fusionnerPages(root, dry_run_flag)

    if dry_run_flag:
        print("\n[FIN DE SIMULATION]")
        print("Vérifie bien que 'trompette' et 'trompette2' sont bien séparés ci-dessus.")
        print("Si c'est OK, passe dry_run_flag = False pour appliquer.")
    else:
        print("\n=== OPÉRATION TERMINÉE ===")

def cleanTitles(chemin_complet, dry_run_flag=True):
    try:
        with open(chemin_complet, "r", encoding="utf-8") as f:
            lignes = f.readlines()
        
        if not lignes:
            return

        # 1. On ne prend que la première ligne (élimine les tags en ligne 2)
        premiere_ligne = lignes[0].strip()
        
        # 2. On coupe au premier '#' (élimine les tags sur la même ligne)
        titre_final = premiere_ligne.split("#")[0].strip()
        
        # On vérifie si une modification est nécessaire
        # (soit parce qu'il y avait plusieurs lignes, soit parce qu'il y avait un #)
        if len(lignes) > 1 or premiere_ligne != titre_final:
            print(f"[MODIF] Fichier : {os.path.basename(os.path.dirname(chemin_complet))}")
            print(f"    Ancien : {' / '.join([l.strip() for l in lignes])}")
            print(f"    Nouveau : '{titre_final}'")
            
            if not dry_run_flag:
                with open(chemin_complet, "w", encoding="utf-8") as f:
                    f.write(titre_final)
                    
    except Exception as e:
        print(f"[ERREUR] {chemin_complet} : {e}")

def cleanTracknames(bns_database, dry_run_flag=True):
    print("=== NETTOYAGE GLOBAL DES TITRES (Ligne 2 + Tags #) ===")
    compteur = 0
    for root, dirs, files in os.walk(bns_database):
        if "trackname.txt" in files:
            compteur += 1
            cleanTitles(os.path.join(root, "trackname.txt"), dry_run_flag)

    if dry_run_flag:
        print(f"\n--- Fin de simulation ({compteur} fichiers vus). Passe dry_run_flag = False pour appliquer. ---")
    else:
        print(f"\n--- Nettoyage terminé sur {compteur} fichiers ! ---")
        
if __name__ == '__main__':

    BNS_DATABASE  = "../database"

    # etape 1 reconstituer les partitions scindées en pages
    #~ pfdPages2Book(BNS_DATABASE, dry_run_flag=False)
    
    # étape 2 netoyer les fichiers titres (trackname.tx) qui peuvent contenir des tags et autre info
    cleanTracknames(BNS_DATABASE, dry_run_flag=False)
    
    
    
    