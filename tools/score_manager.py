# -*- coding: utf-8 -*-
import os
import time

# État global partagé
current_sync = {
    "location": None,
    "timestamp": 0,
    "pages_count": 0
}

def resolve_score_path(db_dir, location, inst, page, is_obsolete):
    """ Logique de 'Rabat' : cherche le fichier exact ou un remplaçant """
    base_path = os.path.join(db_dir, location)
    
    if is_obsolete:
        ext = f"_p{page}.jpg"
        target = os.path.join(base_path, f"{inst}{ext}")
        debug_label = "131"
    else:
        ext = ".pdf"
        target = os.path.join(base_path, f"{inst}{ext}")
        debug_label = "MODERNE"

    if not os.path.exists(target):
        try:
            replacements = [f for f in os.listdir(base_path) if f.endswith(ext)]
            if replacements:
                target = os.path.join(base_path, replacements[0])
                print(f"DEBUG {debug_label}: Rabat sur {replacements[0]}")
                return target
        except:
            pass
        return None
    
    return target

def update_sync_state(db_dir, location):
    """ Met à jour l'état global et compte les pages """
    current_sync["location"] = location
    current_sync["timestamp"] = time.time()
    
    try:
        path = os.path.join(db_dir, location)
        # On compte les images pour la version obsolete
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png'))]
        current_sync["pages_count"] = len(files) if len(files) > 0 else 1
    except:
        current_sync["pages_count"] = 1
    
    return current_sync["pages_count"]