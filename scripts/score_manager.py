# -*- coding: utf-8 -*-
import os
import time

# État global partagé
current_sync = {
    "location": None,
    "timestamp": 0,
    "pages_count": 0
}

def getInstrumentNameNbPages(db_dir, loc, instrument, voice, mode, solo, easy, ):
    # cherche le fichier exact ou un remplaçant
    base_path = os.path.join(db_dir, loc)
    getScoreName(track_path, instrument, voice=1, mode=MODE_POPULAR, solo=False, easy=False, page=1, is_obsolete=True)
    
    
    
    
    ext = f"_p{page}.jpg"
    target = os.path.join(base_path, f"{inst}{ext}")

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
