#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file, send_from_directory
import socket
import os
import sys
import json
import subprocess
import shutil

# --- CONFIGURATION DES REPERTOIRES DE BASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
DATA_DIR = os.path.join(BASE_DIR, 'server_data')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Fichier de configuration externe (NE PAS ÉCRASER LORS DES MISES À JOUR)
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Valeurs par défaut alignées sur ton fichier de config enrichi
DEFAULT_CONFIG = {
    "DATABASE": os.path.abspath(os.path.join(BASE_DIR, '..', 'backNScoreData', 'database')),
    "LAST_TRACK_FILE": "lastTrackname.txt",
    "PLAYER_IP": "127.0.0.1",
    "PLAYER_PORT": 9999,
    "SERVER_HOST": "0.0.0.0",
    "PORT": 8000,
    "DEBUG_MODE": False,
    "QR_CODE_DIR": os.path.join(BASE_DIR, 'static'),
    "QR_CODE_WIFI_FILE": "qrcode_wifi.png",
    "QR_CODE_LAN_FILE": "qrcode_lan.png",
    "PROTOCOL": "http"
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

# Utilisation de CONFIG["DATABASE"] pour correspondre à ton JSON
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

def get_all_local_ips():
    """
    Récupère de manière robuste toutes les adresses IP IPv4 locales actives.
    Exclut l'interface loopback (127.0.0.1).
    Retourne une liste de tuples : [('nom_interface', 'ip'), ...]
    """
    interfaces_found = []
    
    # Étape 1 : On tente la méthode de la socket connectée (très fiable pour l'IP principale)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        main_ip = s.getsockname()[0]
        s.close()
        if main_ip and main_ip != "127.0.0.1":
            interfaces_found.append(("main", main_ip))
    except Exception:
        pass

    # Étape 2 : On scanne via la commande système 'ip' pour choper les autres interfaces (comme le point d'accès wlan0)
    try:
        output = subprocess.check_output(["ip", "-o", "-4", "addr", "show"]).decode()
        for line in output.split('\n'):
            parts = line.split()
            if len(parts) >= 4:
                ifname = parts[1]
                ip = parts[3].split('/')[0]
                if ip != "127.0.0.1" and not ifname.startswith("lo") and "docker" not in ifname:
                    interfaces_found.append((ifname, ip))
    except Exception:
        pass

    # Nettoyage et dédoublonnage par adresse IP
    unique_ips = {}
    for ifname, ip in interfaces_found:
        # On garde le vrai nom d'interface (ex: wlan0) si on l'a plutôt que "main"
        if ip not in unique_ips or unique_ips[ip] == "main":
            unique_ips[ip] = ifname

    return [(ifname, ip) for ip, ifname in unique_ips.items()]

def generate_qr_codes():
    """Génère intelligemment les QR codes selon les interfaces réseau disponibles"""
    try:
        import qrcode
    except ImportError:
        print("Erreur : La bibliothèque 'qrcode' est introuvable. Exécute 'pip install qrcode[pil]'.")
        return

    output_dir = CONFIG.get("QR_CODE_DIR", os.path.join(BASE_DIR, 'static'))
    port = CONFIG.get("PORT", 8000)
    protocol = CONFIG.get("PROTOCOL", "http")

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"Impossible de créer le répertoire des QR Codes : {e}")
            return

    def create_qr_if_changed(url, filename):
        full_path = os.path.join(output_dir, filename)
        memo_path = full_path + ".txt"
        
        # Anti-doublon carte SD
        if os.path.exists(full_path) and os.path.exists(memo_path):
            with open(memo_path, 'r', encoding='utf-8') as f:
                if f.read().strip() == url:
                    print(f"[Réseau] QR Code {filename} déjà à jour pour {url}.")
                    return

        # Écriture
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(full_path)
        
        with open(memo_path, 'w', encoding='utf-8') as f:
            f.write(url)
        try:
            os.sync()
        except AttributeError:
            pass
        print(f"[Réseau] QR Code {filename} MIS À JOUR -> {url}")

    # Récupération des réseaux actifs
    networks = get_all_local_ips()
    
    if not networks:
        print("[Réseau] Aucune IP locale trouvée. Pas de QR code.")
        return

    # CAS 1 : Une seule IP disponible (ton PC de dev, ou la Pi en mode solo)
    if len(networks) == 1:
        ifname, ip = networks[0]
        url = f"{protocol}://{ip}:{port}"
        print(f"[Réseau] Mode IP unique détecté ({ifname} : {ip}). Duplication du QR code pour compatibilité.")
        create_qr_if_changed(url, CONFIG["QR_CODE_WIFI_FILE"])
        create_qr_if_changed(url, CONFIG["QR_CODE_LAN_FILE"])
        return

    # CAS 2 : Multi-réseau (Ta Raspberry Pi avec wlan0 + eth0 actifs)
    for ifname, ip in networks:
        url = f"{protocol}://{ip}:{port}"
        # Cible le Wi-Fi (wlan, wl, ou le point d'accès)
        if "wlan" in ifname or "wl" in ifname:
            create_qr_if_changed(url, CONFIG["QR_CODE_WIFI_FILE"])
        # Cible le filaire (eth, enp, ext)
        else:
            create_qr_if_changed(url, CONFIG["QR_CODE_LAN_FILE"])

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

@app.route('/admin')
def admin(): 
    return send_from_directory(WEB_DIR, 'admin.html')

@app.route('/qrcode')
def qrcode(): 
    return send_from_directory(WEB_DIR, 'qrcode.html')

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

@app.route('/api/admin/refresh', methods=['POST'])
def admin_refresh():
    try:
        # Résolution du chemin absolu du script basé sur l'emplacement actuel de l'application
        script_path = os.path.join(BASE_DIR, 'tools', 'updateDatabase.py')
        
        # Vérification préventive pour éviter les comportements indéterminés de subprocess
        if not os.path.exists(script_path):
            print(f"Erreur : Le script est introuvable au chemin {script_path}")
            return jsonify({"success": False, "message": "Le script de mise à jour est introuvable."}), 404

        result = subprocess.run(['python3', script_path], 
                                capture_output=True, 
                                text=True, 
                                cwd=BASE_DIR,
                                check=True)
        
        print("Script Python exécuté avec succès:", result.stdout)
        return jsonify({"success": True, "message": "Base de données synchronisée."}), 200

    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'exécution du script Python (code retour non-nul):", e.stderr)
        return jsonify({"success": False, "message": f"Erreur lors du scan du disque : {e.stderr or 'Erreur inconnue'}"}), 500
    except Exception as e:
        print("Exception générale levée dans Flask lors du refresh :", str(e))
        return jsonify({"success": False, "message": f"Erreur système interne : {str(e)}"}), 500

@app.route('/api/admin/crud', methods=['POST'])
def admin_crud():
    data = request.json
    if not data or 'action' not in data or 'location' not in data:
        return jsonify({"status": "error", "message": "Paramètres manquants."}), 400

    action = data['action']
    location = data['location'].strip('/')
    target_path = os.path.join(DB_DIR, location)

    # Fonction interne pour formater en CamelCase robuste pour les dossiers physiques
    def to_camel_case(s):
        import re
        s = s.translate(str.maketrans("ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝàáâãäåæçèéêëìíîïðñòóôõöøùúûüýÿ", 
                                      "AAAAAAECEEEEIIIIDNOOOOOOUUUUYaaaaaaaeceeeeiiiidnoooooouuuuyy"))
        words = re.findall(r'[a-zA-Z0-9]+', s)
        if not words: return ""
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])

    # --- 1. ACTION : CREATE ---
    if action == 'create':
        title = data.get('title')
        if not title:
            return jsonify({"status": "error", "message": "Titre propre manquant."}), 400
        try:
            os.makedirs(target_path, exist_ok=True)
            
            # Création du fichier trackname.txt encodé en UTF-8
            trackname_file = os.path.join(target_path, 'trackname.txt')
            with open(trackname_file, 'w', encoding='utf-8') as f:
                f.write(title)
                
            return jsonify({"status": "success", "message": "Dossier et fichier trackname créés."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # --- 2. ACTION : UPDATE ---
    elif action == 'update':
        if 'new_location' in data:
            # Cas A : Renommer ou déplacer physiquement n'importe quel dossier (étagère, livre ou dossier track)
            new_location = data['new_location'].strip('/')
            destination_path = os.path.join(DB_DIR, new_location)
            
            if not os.path.exists(target_path):
                return jsonify({"status": "error", "message": f"Le dossier d'origine n'existe pas ({location})."}), 400
                
            try:
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                if os.path.normpath(target_path) != os.path.normpath(destination_path):
                    shutil.move(target_path, destination_path)
                return jsonify({"status": "success", "message": "Dossier renommé/déplacé sur le disque avec succès.", "new_location": new_location}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
                
        elif 'new_title' in data:
            # Cas B : Modifier UNIQUEMENT le contenu textuel de trackname.txt (Le titre affiché de la chanson)
            new_title = data['new_title']
            if not os.path.exists(target_path):
                return jsonify({"status": "error", "message": f"Le dossier ciblé n'existe pas ({location})."}), 400
                
            try:
                trackname_file = os.path.join(target_path, 'trackname.txt')
                with open(trackname_file, 'w', encoding='utf-8') as f:
                    f.write(new_title)
                
                try:
                    os.sync()
                except AttributeError:
                    pass
                    
                return jsonify({"status": "success", "message": "Fichier trackname.txt mis à jour."}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "error", "message": "Sous-action update non reconnue (fournir new_location ou new_title)."}), 400

    # --- 3. ACTION : DELETE ---
    elif action == 'delete':
        if not os.path.exists(target_path):
            return jsonify({"status": "error", "message": "L'élément à supprimer n'existe pas."}), 400
            
        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            return jsonify({"status": "success", "message": "Supprimé avec succès."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    else:
        return jsonify({"status": "error", "message": f"Action '{action}' inconnue."}), 400


if __name__ == '__main__':
    host = CONFIG.get("SERVER_HOST", "0.0.0.0")
    port = CONFIG.get("PORT", 8000)
    debug = CONFIG.get("DEBUG_MODE", False)
    
    # Détection intelligente corrigée
    generate_qr_codes()
    
    print(f"Démarrage du serveur Back'n Score (Hôte: {host}:{port})")
    app.run(host=host, port=port, debug=debug)