#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
import socket
import os
import sys
import json
import subprocess
import shutil
import pty
import select

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

def get_current_db_dir():
    """
    1. Vérifie si le dossier database existe déjà dans /mnt/usbkey.
    2. Sinon, monte directement /dev/sda1 (ou la première partition usb trouvée) sur /mnt/usbkey.
    3. Met à jour et retourne le chemin valide.
    """
    config_db = CONFIG.get("DATABASE")
    if config_db and os.path.isdir(config_db):
        return config_db

    # S'assure que le point de montage existe
    os.makedirs("/mnt/usbkey", exist_ok=True)

    # Si le dossier database est déjà physiquement accessible là, c'est bon
    target_db = "/mnt/usbkey/database"
    if os.path.isdir(target_db):
        CONFIG["DATABASE"] = target_db
        return target_db

    # Sinon, on monte la clé automatiquement (ex: sda1)
    try:
        output = subprocess.check_output(["lsblk", "-rno", "NAME,TYPE"], text=True)
        for line in output.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == "part":
                dev_name = f"/dev/{parts[0]}"
                res = subprocess.run(["sudo", "mount", dev_name, "/mnt/usbkey"], capture_output=True)
                if res.returncode == 0:
                    break
    except Exception:
        pass

    # Vérification finale après tentative de montage
    if os.path.isdir(target_db):
        CONFIG["DATABASE"] = target_db
        return target_db

    return config_db

# Utilisation dynamique sécurisée
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


# --- GESTION DU TERMINAL VIRTUEL (PTY) ---
master_fd = None
slave_fd = None
child_pid = None

def start_shell():
    global master_fd, slave_fd, child_pid
    try:
        master_fd, slave_fd = pty.openpty()
        child_pid = os.fork()
        if child_pid == 0:
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(master_fd)
            os.close(slave_fd)
            os.execve("/bin/bash", ["bash"], os.environ)
        else:
            os.close(slave_fd)
    except Exception as e:
        print(f"[Terminal] Impossible de démarrer le pty (normal sous Windows en dev) : {e}")

start_shell()


# --- FONCTIONS UTILITAIRES ---

def get_all_local_ips():
    interfaces_found = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        main_ip = s.getsockname()[0]
        s.close()
        if main_ip and main_ip != "127.0.0.1":
            interfaces_found.append(("main", main_ip))
    except Exception:
        pass

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

    unique_ips = {}
    for ifname, ip in interfaces_found:
        if ip not in unique_ips or unique_ips[ip] == "main":
            unique_ips[ip] = ifname

    return [(ifname, ip) for ip, ifname in unique_ips.items()]

def generate_qr_codes():
    try:
        import qrcode
    except ImportError:
        return

    output_dir = CONFIG.get("QR_CODE_DIR", os.path.join(BASE_DIR, 'static'))
    port = CONFIG.get("PORT", 8000)
    protocol = CONFIG.get("PROTOCOL", "http")

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            return

    def create_qr_if_changed(url, filename):
        full_path = os.path.join(output_dir, filename)
        memo_path = full_path + ".txt"
        
        if os.path.exists(full_path) and os.path.exists(memo_path):
            with open(memo_path, 'r', encoding='utf-8') as f:
                if f.read().strip() == url:
                    return

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

    networks = get_all_local_ips()
    if not networks:
        return

    for ifname, ip in networks:
        url = f"{protocol}://{ip}:{port}"
        is_wifi = "wlan" in ifname or "wl" in ifname
        filename = CONFIG["QR_CODE_WIFI_FILE"] if is_wifi else CONFIG["QR_CODE_LAN_FILE"]
        create_qr_if_changed(url, filename)

def save_last_track_dir(name):
    if name is not None:
        name = name.strip()
        if name.lower() == "none" or not name:
            return
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
                os.sync()
            except AttributeError:
                pass

def load_last_track_dir():
    current_db = get_current_db_dir()
    if os.path.exists(LAST_TRACK_DIRNAME):
        try:
            with open(LAST_TRACK_DIRNAME, 'r', encoding='utf-8') as f:
                last_track_path = f.read().strip()
            
            if last_track_path and last_track_path.lower() != "none":
                if os.path.isabs(last_track_path) and current_db:
                    if last_track_path.startswith(current_db):
                        last_track_path = os.path.relpath(last_track_path, current_db)
                
                if current_db and os.path.isdir(current_db):
                    full_dirname = os.path.join(current_db, last_track_path)
                    if os.path.isdir(full_dirname):
                        return last_track_path
        except Exception:
            pass
    return None


AVAILABLE_INSTRUMENTS = []

def update_available_instruments(loc):
    global AVAILABLE_INSTRUMENTS
    current_db = get_current_db_dir()
    if not loc or not current_db or not os.path.isdir(current_db):
        AVAILABLE_INSTRUMENTS = []
        return

    full_path = os.path.join(current_db, loc)
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
app = Flask(__name__, template_folder=WEB_DIR, static_folder=None)

if trackLocation:
    update_available_instruments(trackLocation)


# --- ROUTES ---

@app.route('/get_available_instruments')
def route_get_instruments():
    global AVAILABLE_INSTRUMENTS, trackLocation
    current_db = get_current_db_dir()
    if not trackLocation or not current_db or not os.path.isdir(current_db):
        trackLocation = load_last_track_dir()
    
    if trackLocation:
        update_available_instruments(trackLocation)
    else:
        AVAILABLE_INSTRUMENTS = []
    return jsonify(AVAILABLE_INSTRUMENTS)

@app.route('/')
def home(): 
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/audio')
def audio(): 
    return send_from_directory(WEB_DIR, 'audio.html')

@app.route('/keyboard')
def keyboard(): 
    return send_from_directory(WEB_DIR, 'keyboard.html')

@app.route('/selector')
def selector(): 
    return send_from_directory(WEB_DIR, 'selector.html')

@app.route('/pupitre')
def pupitre(): 
    return send_from_directory(WEB_DIR, 'pupitre.html')

@app.route('/remote')
def remote(): 
    return send_from_directory(WEB_DIR, 'remote.html')

@app.route('/admin')
def admin(): 
    return send_from_directory(WEB_DIR, 'admin.html')

@app.route('/qrcode')
def qrcode_page(): 
    output_dir = CONFIG.get("QR_CODE_DIR", os.path.join(BASE_DIR, 'static'))
    networks = get_all_local_ips()
    active_networks = []
    
    for ifname, ip in networks:
        is_wifi = "wlan" in ifname or "wl" in ifname
        card_type = "wifi" if is_wifi else "lan"
        title = "Réseau Wi-Fi" if is_wifi else "Réseau Filaire"
        filename = CONFIG["QR_CODE_WIFI_FILE"] if is_wifi else CONFIG["QR_CODE_LAN_FILE"]
        
        url = f"http://{ip}:{CONFIG.get('PORT', 8000)}"
        memo_path = os.path.join(output_dir, filename + ".txt")
        if os.path.exists(memo_path):
            try:
                with open(memo_path, 'r', encoding='utf-8') as f:
                    url = f.read().strip()
            except Exception:
                pass
                
        if not any(n['type'] == card_type for n in active_networks):
            active_networks.append({
                "title": title,
                "type": card_type,
                "filename": filename,
                "url": url
            })
            
    return render_template('qrcode.html', networks=active_networks)

@app.route('/training')
def training(): 
    return send_from_directory(WEB_DIR, 'training.html')

@app.route('/admin/terminal')
def terminal_page():
    user_agent = request.headers.get('User-Agent', '')
    if 'Android 3' in user_agent or 'Android 4' in user_agent or 'Android/3' in user_agent or 'Android/4' in user_agent:
        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head><meta charset="UTF-8"><title>Terminal Incompatible</title></head>
        <body style="background:#000;color:#ff5252;text-align:center;padding-top:50px;">
            <h2>Appareil non compatible</h2>
            <p>Le terminal nécessite un navigateur moderne.</p>
        </body>
        </html>
        """, 200
    return send_from_directory(WEB_DIR, 'terminal.html')

@app.route('/admin/terminal/exec', methods=['POST'])
def terminal_exec():
    global master_fd
    if master_fd is None:
        return jsonify({'output': "\r\nErreur : Le terminal pty n'est pas disponible.\r\n"})
    
    data = request.json or {}
    cmd = data.get('command', '') + '\n'
    try:
        os.write(master_fd, cmd.encode('utf-8'))
    except Exception as e:
        return jsonify({'output': f"\r\nErreur d'écriture : {e}\r\n"})
    
    output = ""
    while True:
        r, w, e = select.select([master_fd], [], [], 0.1)
        if not r:
            break
        try:
            data_read = os.read(master_fd, 1024)
            if not data_read:
                break
            output += data_read.decode('utf-8', errors='ignore')
        except OSError:
            break
    return jsonify({'output': output})

@app.route('/static/<path:path>')
def send_static(path): 
    return send_from_directory(os.path.join(BASE_DIR, 'static'), path)

@app.route('/server_data/<path:path>')
def send_json_data(path): 
    return send_from_directory(DATA_DIR, path)

@app.route('/get_score_info')
def get_score_info():
    global trackLocation
    
    current_db = get_current_db_dir()
    if not current_db or not os.path.isdir(current_db):
        return jsonify({"status": "error", "message": "Clé USB absente"}), 400

    loc = request.args.get('loc')
    if not loc or loc.strip() == "" or loc.lower() == "none":
        loc = trackLocation or load_last_track_dir()

    instrument = request.args.get('instrument')
    voice = request.args.get('voice', 1, type=int)
    mode = request.args.get('mode', str(MODE_POPULAR))
    solo = request.args.get('solo', 'false') == '1'
    easy = request.args.get('easy', 'false') == '1'
    
    if loc:
        track_path = os.path.join(current_db, loc)
        trackLocation = loc
        save_last_track_dir(loc)
    else:
        return jsonify({"status": "error", "message": "Aucun morceau sélectionné"}), 400
        
    if not os.path.isdir(track_path):
        return jsonify({"status": "error", "message": "Dossier du morceau introuvable"}), 400

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
        return jsonify({"status": "error", "message": getScoreNameError() or "Erreur score"}), 200
    else:
        nb_pages = getNbPages(track_path, score_name)
        if nb_pages != 0:
            return jsonify({"status": "success", "score": score_name, "nb_pages": nb_pages}), 200
        else:
            return jsonify({"status": "error", "message": getScoreNameError() or "Erreur pages"}), 200

@app.route('/get_score')
def get_score():
    location = request.args.get('location')
    inst = request.args.get('inst')
    page = request.args.get('page', '1')
    
    current_db = get_current_db_dir()
    if not current_db or not os.path.isdir(current_db):
        return "Clé USB absente", 404

    path = score_manager.resolve_score_path(current_db, location, inst, page, is_obsolete())
    if path and os.path.exists(path):
        return send_file(path)
    return "Aucun fichier trouvé", 404

@app.route('/audio_command', methods=['POST', 'OPTIONS'])
def audio_command():
    if request.method == 'OPTIONS':
        return 'ok', 200
    cmd = request.data
    udp_socket.sendto(cmd, PLAYER_ADDR)
    return "ok", 200

@app.route('/sync_check')
def sync_check():
    global trackLocation, old_trackLocation
    current_db = get_current_db_dir()
    if not trackLocation or not current_db or not os.path.isdir(current_db):
        trackLocation = load_last_track_dir()
    if old_trackLocation != trackLocation:
        save_last_track_dir(trackLocation)
        old_trackLocation = trackLocation
    return f"{trackLocation if trackLocation else ''}", 200, {'Content-Type': 'text/plain'}

@app.route('/update_track', methods=['POST'])
def update_track():
    global trackLocation
    current_db = get_current_db_dir()
    if not current_db or not os.path.isdir(current_db):
        return jsonify({"status": "error", "message": "Clé USB absente"}), 400
    data = request.json
    if data and 'location' in data:
        trackLocation = data['location']
        update_available_instruments(trackLocation)
        save_last_track_dir(trackLocation)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/scores/<path:filename>')
def serve_scores(filename):
    current_db = get_current_db_dir()
    if not current_db or not os.path.isdir(current_db):
        return "Clé USB absente", 404
    return send_from_directory(current_db, filename)

@app.route('/api/admin/refresh', methods=['POST'])
def admin_refresh():
    try:
        current_db = get_current_db_dir()
        if not current_db or not os.path.isdir(current_db):
            return jsonify({"success": False, "message": "Clé USB absente."}), 404
        script_path = os.path.join(BASE_DIR, 'tools', 'updateDatabase.py')
        if not os.path.exists(script_path):
            return jsonify({"success": False, "message": "Script introuvable."}), 404

        subprocess.run(['python3', script_path], capture_output=True, text=True, cwd=BASE_DIR, check=True)
        return jsonify({"success": True, "message": "Base synchronisée."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/admin/save_mp3_types', methods=['POST'])
def save_mp3_types():
    try:
        priorities = request.json
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(os.path.join(DATA_DIR, 'mp3_types.json'), 'w', encoding='utf-8') as f:
            json.dump(priorities, f, indent=4, ensure_ascii=False)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/admin/crud', methods=['POST'])
def admin_crud():
    current_db = get_current_db_dir()
    if not current_db or not os.path.isdir(current_db):
        return jsonify({"status": "error", "message": "Clé USB absente."}), 400

    data = request.json
    if not data or 'action' not in data or 'location' not in data:
        return jsonify({"status": "error", "message": "Paramètres manquants."}), 400

    action = data['action']
    location = data['location'].strip('/')
    target_path = os.path.join(current_db, location)

    if action == 'create':
        title = data.get('title')
        try:
            os.makedirs(target_path, exist_ok=True)
            with open(os.path.join(target_path, 'trackname.txt'), 'w', encoding='utf-8') as f:
                f.write(title)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    elif action == 'update':
        if 'new_location' in data:
            new_location = data['new_location'].strip('/')
            destination_path = os.path.join(current_db, new_location)
            try:
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                if os.path.normpath(target_path) != os.path.normpath(destination_path):
                    shutil.move(target_path, destination_path)
                return jsonify({"status": "success"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        elif 'new_title' in data:
            try:
                with open(os.path.join(target_path, 'trackname.txt'), 'w', encoding='utf-8') as f:
                    f.write(data['new_title'])
                return jsonify({"success": "success"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

    elif action == 'delete':
        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "Action inconnue."}), 400


if __name__ == '__main__':
    host = CONFIG.get("SERVER_HOST", "0.0.0.0")
    port = CONFIG.get("PORT", 8000)
    debug = CONFIG.get("DEBUG_MODE", False)
    
    generate_qr_codes()
    
    print(f"Démarrage du serveur Back'n Score (Hôte: {host}:{port})")
    app.run(host=host, port=port, debug=debug)