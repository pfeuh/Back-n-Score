on a déjà bien avancé sur le projet. on en est au choix de l'instrument par un musicien. détail très important. le périphérique du musicien détecte et envoie son type au serveur vieux android 4 ou perihérique moderne (tablette actuelle, ordinateur etc...) une partition est un fichier pdf sauf pour android 4, là le serveur le transforme en une série d'images correspondant chacune à une page du pdf.

python3 -m http.server 8000

import sys
import os

# importer les modules du dossier au dessus
# On récupère le chemin du dossier où se trouve le script de test
dossier_actuel = os.path.dirname(__file__)
# On calcule le chemin du dossier parent (..)
dossier_parent = os.path.abspath(os.path.join(dossier_actuel, ".."))
# On l'ajoute au chemin de recherche
if dossier_parent not in sys.path:
    sys.path.insert(0, dossier_parent)
# Maintenant tu peux importer tes modules du dossier parent
import mon_module_principal

tree -L 3 -I 'database|test_database|secu|__pycache__|doc|Partitions Joyeux Vignerons'

pfeuh@pfeuh-ESPRIMO-P910:/mnt/Data1/Documents/backNScore$ tree -L 3 -I 'database|test_database|secu|__pycache__|doc|Partitions Joyeux Vignerons'
.
├── buildTree.py
├── config.json
├── defaultConfig.json
├── loadJson.py
├── sandbox
│   └── getScore.py
├── scripts
│   ├── getScoreName.py
│   ├── instruments.py
│   └── trackPdfToJpg.py
├── server_data
│   ├── db_tracks.json
│   ├── meta_instruments.json
│   ├── ui_classy.json
│   └── ui_popular.json
├── server.py
├── spy.py
├── static
│   ├── css
│   │   └── index.css
│   ├── img
│   │   └── splash.jpg
│   └── js
│       ├── pdf.min.js
│       └── pdf.worker.min.js
├── temp
│   ├── track_tree.json
│   └── tree.json
├── templates
│   ├── chef.htm
│   ├── index.htm
│   ├── kompare.txt
│   └── pupitre.htm
├── tools
│   ├── checkDatabase.py
│   ├── cleanDatabaseStructure.py
│   ├── cleanImportedMaDatabase.py
│   ├── createTrackTreeInstrumentTree.py
│   ├── exportMa2Bns.py
│   ├── generateJpg.py
│   ├── instrumentGui.py
│   ├── MA2BackNScore.py
│   ├── MA.py
│   ├── readme.txt
│   ├── test_pupitre.htm
│   ├── test_server.py
│   ├── test_track_tree.htm
│   ├── testtracktreeskeleton.htm
│   ├── updateDatabase.py
│   ├── utest_getSCoreName.py
│   └── utest.py
└── web
    ├── index.html
    └── pupitre.html


On en était où pour le projet backNScore ?
    
liste des taches

examiner la config du serveur, addresse database etc...
tester les pedales de changement de page
la création des images ne voit pas les changements dans les jpg
quand on a plusieurs page côte à côte elles doivent se toucher au lieu d'avoir de grandes bordures noires entre elles.
audioplayer mode autostart
audioplayer delay autostart
audioplayer message "pas de fichier audio pour ce morceau"
rajouter set list SACEM







