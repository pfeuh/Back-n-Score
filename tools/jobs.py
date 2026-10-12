#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import os

def getTracks(root_search_path):
    if not os.path.isdir(root_search_path):
        print("%s not found!"%root_search_path)
        sys.exit(1)
    return [str(p.parent) for p in Path(root_search_path).rglob("trackname.txt")]
    
def getTracksWithoutScore(root_search_path):
    return [p for p in getTracks(root_search_path) if not "score.mscz" in os.listdir(p)]
    
def getTracksWithDifferentScore(root_search_path):
    results = []
    for p in getTracks(root_search_path):
        for fname in os.listdir(p):
            if os.path.basename(fname).endswith(".mscz"):
                if os.path.basename(fname) != "score.mscz":
                    results.append((p, fname))
    return results
    
def getTracksScores(root_search_path):
    results = []
    for p in getTracks(root_search_path):
        fnames = []
        for fname in os.listdir(p):
            if os.path.basename(fname).endswith(".mscz"):
                fnames .append(fname)
        for x, fname in enumerate(fnames):
            if fname == "score.mscz":
                fnames.remove("score.mscz")
                fnames = ["OK"] + fnames
                
        results.append("%-100s %s"%(p, str(fnames)))
    return results
    
def getTracksSmallScores(root_search_path):
    results = []
    for p in getTracks(root_search_path):
        fnames = []
        for fname in os.listdir(p):
            if os.path.basename(fname).endswith(".mscz"):
                fnames.append(fname)
        for x, fname in enumerate(fnames):
            if fname == "score.mscz":
                score_path = os.path.join(p, fname)
                # Vérification si le fichier existe et si sa taille est inférieure à 80 ko (80 * 1024 octets)
                if os.path.exists(score_path) and os.path.getsize(score_path) < 80 * 1024:
                    results.append("%-100s %s"%(p, str(fnames)))
                
    return results
    
def getTracksInstruments(root_search_path, instruments):
    instruments = [i + ".pdf" for i in instruments]
    results = []
    for p in getTracks(root_search_path):
        for titlefname in os.listdir(p):
            if titlefname == "trackname.txt":
                with open(os.path.join(p, titlefname), "r") as f:
                    song_name = f.read().strip()
                for fname in os.listdir(p):
                    if fname in instruments:
                        chemin_relatif = p.split("database/")[1]
                        
                        results.append({"title": song_name, "location": chemin_relatif})
                        break
    
    # Tri d'abord sur le chemin, puis sur le titre (les deux en insensible à la casse)
    results.sort(key=lambda x: (x["location"].casefold(), x["title"].casefold()))
    return results
    
if __name__ == "__main__":
    
    import json

    def dict2json(mylist, filepath):
        """Enregistre une liste de dictionnaires au format JSON sur le disque."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(mylist, f, ensure_ascii=False, indent=4)

    DATABASE = "/mnt/Data1/Documents/backNScoreData/database"
    PFEUHBASE = "/mnt/Data1/Documents/backNScoreData/database/people/pierreFaller"
    
    #~ for item in getTracks(DATABASE):
        #~ print(item)
        
    #~ for item in getTracksWithoutScore(DATABASE):
        #~ print(item)

    tracks = getTracksInstruments(DATABASE, ("SOL", "flute_alto"))
    dict2json(tracks, "../server_data/custom/alto_flute.json")
