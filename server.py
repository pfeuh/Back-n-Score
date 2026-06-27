#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file, send_from_directory
import socket
import os
import sys
import json

# --- CONFIGURATION DES REPERTOIRES DE BASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
DATA_DIR = os.path.join(BASE_DIR, 'server_data')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Fichier de configuration externe (NE PAS ÉCRASER LORS DES MISES À JOUR)
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Valeurs par défaut alignées sur ton fichier de config
DEFAULT_CONFIG = {
    "DATABASE": os.path.abspath(os.path.join(BASE_DIR, '..', 'backNScoreData', 'database')),
    "LAST_TRACK_FILE": "lastTrackname.txt",
    "PLAYER_IP": "127.0.0.1",
    "PLAYER_PORT": 9999,
    "SERVER_HOST": "0.0.0.0",
    "PORT": 8000,
    "DEBUG_MODE": False
}

def load_config():
    """Charge la config locale ou crée une config par défaut si absente"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    config.setdefault(key, value)
                return config
        except Exception as e:
            print(f"Erreur de lecture de {CONFIG_FILE}, utilisation des valeurs par défaut. Erreur: {e}")
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"Nouveau fichier de configuration créé : {CONFIG_FILE}")
    except Exception as e:
        print(f"Impossible de créer le fichier de configuration : {e}")
        
    return DEFAULT_CONFIG

# Chargement de la configuration
CONFIG = load_config()

# Correction ici : Utilisation de CONFIG["DATABASE"] pour correspondre à ton JSON
DB_DIR = CONFIG["DATABASE"]
LAST_TRACK_DIRNAME = os.path.join(SCRIPTS_DIR, CONFIG["LAST_TRACK_FILE"])

# Ajout du dossier SCRIPT pour les imports du projet
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# --- IMPORTS DES MODULES LOCAUX ---
from network_utils import get_cid, is_obsolete
from instruments import MODE_POPULAR, MODE_CLASSIQUE
from getScoreName import getScoreName, getScoreNameError, getScoreNameLite, getNbPages
import score_manager

# --- CONFIGURATION RÉSEAU ---
PLAYER_ADDR = (CONFIG.get("PLAYER_IP", "127.0.0.1"), CONFIG.get("PLAYER_PORT", 9999))
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# --- FONCTIONS UTILITAIRES ---

def save_last_track_dir(name):
    """Écrit sur la SD UNIQUEMENT si la valeur a changé pour préserver la carte"""
    if name is not None:
        name = name.strip()
        current_saved = ""
        
        if os.path.exists(LAST_TRACK_DIRNAME):
            try:
                with open(LAST_TRACK_DIRNAME, 'r', encoding='utf-8') as f:
                    current_saved = f.read().strip()
            except Exception:
                pass
        
        if name != current_saved:
            with open(LAST_TRACK_DIRNAME, 'w', encoding='utf-8') as f:
                f.write(name)
            try:
                os.sync()  # Force l'écriture physique immédiate sur la SD / Disque
            except AttributeError:
                pass

def load_last_track_dir():
    if os.path.exists(LAST_TRACK_DIRNAME):
        try:
            with open(LAST_TRACK_DIRNAME, 'r', encoding='utf-8') as f:
                last_track_path = f.read().strip()
            full_dirname = os.path.join(DB_DIR, last_track_path)
            if os.path.isdir(full_dirname):
                return last_track_path
            else:
                print("not a valid dir!", full_dirname)
        except Exception as e:
            print("Erreur de lecture du fichier track:", e)
    return None


AVAILABLE_INSTRUMENTS = []

def update_available_instruments(loc):
    """Scan le dossier et met à jour la liste globale"""
    global AVAILABLE_INSTRUMENTS
    if not loc:
        AVAILABLE_INSTRUMENTS = []
        return

    full_path = os.path.join(DB_DIR, loc)
    if os.path.isdir(full_path):
        inst_list = []
        for f in os.listdir(full_path):
            if f.endswith('.pdf'):
                name = os.path.splitext(f)[0]
                inst_list.append(name)
        AVAILABLE_INSTRUMENTS = sorted(inst_list)
    else:
        AVAILABLE_INSTRUMENTS = []

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


# --- INITIALISATION DE L'APP ---

trackLocation = load_last_track_dir()
old_trackLocation = trackLocation
app = Flask(__name__, static_folder=None)

if trackLocation:
    update_available_instruments(trackLocation)


# --- ROUTES ---

@app.route('/get_available_instruments')
def route_get_instruments():
    global AVAILABLE_INSTRUMENTS
    print(AVAILABLE_INSTRUMENTS)
    return jsonify(AVAILABLE_INSTRUMENTS)

@app.route('/')
def home(): 
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/audio')
def audio(): 
    return send_from_directory(WEB_DIR, 'audio.html')

@app.route('/selector')
def selector(): 
    return send_from_directory(WEB_DIR, 'selector.html')

@app.route('/pupitre')
def pupitre(): 
    return send_from_directory(WEB_DIR, 'pupitre.html')

@app.route('/training')
def training(): 
    return send_from_directory(WEB_DIR, 'training.html')

@app.route('/static/<path:path>')
def send_static(path): 
    return send_from_directory(os.path.join(BASE_DIR, 'static'), path)

@app.route('/server_data/<path:path>')
def send_json_data(path): 
    return send_from_directory(DATA_DIR, path)

@app.route('/get_score_info')
def score_info():
    global trackLocation
    loc = request.args.get('loc')
    instrument = request.args.get('instrument')
    voice = request.args.get('voice', 1, type=int)
    mode = request.args.get('mode', str(MODE_POPULAR))
    solo = request.args.get('solo', 'false') == '1'
    easy = request.args.get('easy', 'false') == '1'
    
    if loc:
        track_path = os.path.join(DB_DIR, loc)
        trackLocation = loc
        save_last_track_dir(loc)
    else:
        return jsonify({"status": "error", "message": "Location manquante"}), 400
        
    score_name = getScoreName(
        track_path=track_path,
        instrument=instrument,
        voice=voice,
        mode=int(mode),
        solo=solo,
        easy=easy,
        page=1,
        is_obsolete=True
    )

    if score_name is None:
        return jsonify({"status": "error", "message": getScoreNameError() or "Même pas de message d'erreur pour le score!"}), 200
    else:
        nb_pages = getNbPages(track_path, score_name)
        print(score_name, nb_pages)
        if nb_pages != 0:
            return jsonify({"status": "success", "score": score_name, "nb_pages": nb_pages}), 200
        else:
            return jsonify({"status": "error", "message": getScoreNameError() or "Même pas de message d'erreur pour le nombre de pages!"}), 200

@app.route('/get_score')
def get_score():
    location = request.args.get('location')
    inst = request.args.get('inst')
    page = request.args.get('page', '1')
    
    path = score_manager.resolve_score_path(DB_DIR, location, inst, page, is_obsolete())
    
    if path and os.path.exists(path):
        return send_file(path)
    return "Aucun fichier trouvé", 404

@app.route('/audio_command', methods=['POST'])
def audio_command():
    print(f"{get_cid()}?")
    cmd = request.data
    udp_socket.sendto(cmd, PLAYER_ADDR)
    return "ok", 200

@app.route('/sync_check')
def sync_check():
    print(f"{get_cid()}?")
    global trackLocation, old_trackLocation
    if old_trackLocation != trackLocation:
        save_last_track_dir(trackLocation)
        old_trackLocation = trackLocation
    return f"{trackLocation}", 200, {'Content-Type': 'text/plain'}

@app.route('/update_track', methods=['POST'])
def update_track():
    global trackLocation
    data = request.json
    if data and 'location' in data:
        trackLocation = data['location']
        update_available_instruments(trackLocation)
        save_last_track_dir(trackLocation)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/scores/<path:filename>')
def serve_scores(filename):
    return send_from_directory(DB_DIR, filename)


if __name__ == '__main__':
    host = CONFIG.get("SERVER_HOST", "0.0.0.0")
    port = CONFIG.get("PORT", 8000)
    debug = CONFIG.get("DEBUG_MODE", False)
    
    print(f"Démarrage du serveur Back'n Score (Hôte: {host}:{port})")
    app.run(host=host, port=port, debug=debug)