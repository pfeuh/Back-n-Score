#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import fcntl
import struct
import qrcode
import os

def get_ip_address(ifname):
    """
    Récupère l'adresse IP d'une interface réseau spécifique (ex: 'wlan0').
    Utilise une méthode système (ioctl) très fiable sous Linux/Raspberry Pi.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except OSError:
        # Retourne None si l'interface n'est pas trouvée ou n'a pas d'IP
        return None

def main():
    # ---- CONFIGURATION ----
    interface = "wlan0"
    # Le dossier où sera enregistrée l'image (à adapter selon ton serveur)
    output_dir = "/var/www/html" 
    filename = "qrcode.png"
    # -----------------------

    # 1. Récupération de l'IP du Point d'Accès
    ip_address = get_ip_address(interface)
    
    if not ip_address:
        print(f"Erreur : Impossible de trouver l'adresse IP pour l'interface {interface}")
        return

    url = f"http://{ip_address}"
    print(f"Interface {interface} détectée. IP : {ip_address}")
    print(f"URL à encoder : {url}")

    # 2. Configuration du QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 3. Génération et sauvegarde de l'image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Sécurité : créer le dossier s'il n'existe pas encore
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    full_path = os.path.join(output_dir, filename)
    img.save(full_path)
    print(f"Succès : QR Code généré avec succès dans {full_path}")

if __name__ == "__main__":
    main()