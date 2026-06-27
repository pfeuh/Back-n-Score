#!/usr/bin/python
# -*- coding: utf-8 -*-

BUILD_TREE_VERSION = "1.0"

import os

def getTrackname(folder_path):
    txt_path = os.path.join(folder_path, "trackname.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            pass
    return os.path.basename(folder_path)

def buildTree(database, path):
    tree = {}
    if not os.path.exists(path):
        return tree

    items = sorted(os.listdir(path))

    # track (morceau de musique)
    if any(item.lower().endswith(".pdf") for item in items):
        return {
            "_type": "track",
            "titre": getTrackname(path),
            "chemin": os.path.relpath(path, database)
        }

    has_tracks = False

    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            res = buildTree(database, full_path)
            if res:
                if isinstance(res, dict) and res.get("_type") == "track":
                    tree[res["titre"]] = res
                    has_tracks = True
                else:
                    tree[item] = {"_type": "folder", "_children": res}

    # distinction étagère vs livre
    return {
        "_type": "folder",
        "_kind": "book" if has_tracks else "shelf",
        "_children": tree
    }

def printTree(tree, prefix=""):
    items = list(tree.items())
    
    for i, (key, value) in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "

        if isinstance(value, dict):
            if value.get("_type") == "file":
                print(prefix + connector + f"🎼 {key}")
            
            elif value.get("_type") == "folder":
                print(prefix + connector + f"📁 {key}")
                
                new_prefix = prefix + ("    " if is_last else "│   ")
                printTree(value["_children"], new_prefix)

if __name__ == '__main__':

    from sys import argv
    from loadJson import loadJson
    import json

    print("%s v.%s"%(argv[0], BUILD_TREE_VERSION) )

    """ U N I T A R Y    T E S T ***---"""

    config = loadJson("config.json")
    database = config["DATABASE"]
    tree = buildTree(database, database)
    with open("temp/tree.json", "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)

