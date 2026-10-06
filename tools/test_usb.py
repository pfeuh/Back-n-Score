#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

def find_usb_database():
    """
    Cherche un dossier 'database' directement à la racine d'un périphérique monté 
    dans /media ou /mnt (ex: /media/pi/USB1/database ou /media/USB1/database).
    """
    mount_roots = ["/media", "/mnt"]
    
    for root_mount in mount_roots:
        if not os.path.exists(root_mount):
            continue
            
        try:
            # Parcours du premier niveau (ex: /media/pi ou /media/USB1)
            for item1 in os.listdir(root_mount):
                path1 = os.path.join(root_mount, item1)
                if not os.path.isdir(path1):
                    continue
                
                # Test direct si item1 est la clé (ex: /media/USB1/database)
                cand = os.path.join(path1, "database")
                if os.path.isdir(cand):
                    return cand
                
                # Sinon, parcours du second niveau (ex: /media/pi/USB1/database)
                try:
                    for item2 in os.listdir(path1):
                        path2 = os.path.join(path1, item2)
                        if os.path.isdir(path2):
                            cand2 = os.path.join(path2, "database")
                            if os.path.isdir(cand2):
                                return cand2
                except PermissionError:
                    pass
                    
        except PermissionError:
            pass
            
    return None

if __name__ == "__main__":
    print("=== Test de détection de la clé USB (Database à la racine) ===")
    print("Branche ou débranche ta clé pour voir le comportement en direct (Ctrl+C pour quitter).\n")
    
    last_found = None
    try:
        while True:
            current_db = find_usb_database()
            if current_db:
                if current_db != last_found:
                    print(f"[TROUVÉ] Base détectée avec succès : {current_db}")
                    last_found = current_db
            else:
                if last_found is not None:
                    print("[PERDU] La clé a été débranchée ou n'est plus détectée.")
                    last_found = None
                else:
                    print("[ATTENTE] Recherche de la clé...", end="\r")
            
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nArrêt du test.")