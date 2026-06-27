# -*- coding: utf-8 -*-
import socket
import json
import logging
from flask import request

# On fait taire Werkzeug ici aussi pour être cohérent
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def get_cid():
    """ Retourne l'ID unique basé sur l'IP en format Hexa 4 digits (ex: 010A) """
    parts = request.remote_addr.split('.')
    if len(parts) == 4:
        # Calcul de la valeur entière (0 à 65535)
        valeur = int(parts[2]) * 256 + int(parts[3])
        # Formatage : 04 (4 digits avec zéros de remplissage), x (hexadécimal minuscule)
        # Utilise :04X si tu préfères les majuscules (ex: 0A1F)
        return f"{valeur:04X}"
    return "0000"

def is_obsolete():
    """ Détection des vieux Android ou IP spécifique (.131) """
    ua = request.headers.get('User-Agent', '')
    is_obs = any(v in ua for v in ["Android 4.", "Android 5.", "Android 6."])
    is_ip = "131" in request.remote_addr
    return is_obs or is_ip

def spy_raw(message):
    """ Envoie une chaîne brute vers l'espion """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode('utf-8'), ("127.0.0.1", 9999))
    except:
        pass

def spy_log(label, data):
    """ Envoie le JSON vers le terminal espion """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps({"label": label, "data": data}, ensure_ascii=False)
        sock.sendto(message.encode('utf-8'), ("127.0.0.1", 9999))
    except:
        pass