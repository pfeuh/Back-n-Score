#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import sys

# La ligne exacte à ajouter
sudoers_line = "bns ALL=(ALL) NOPASSWD: /bin/mount /dev/sd[a-z][0-9] /mnt/usbkey, /bin/umount /mnt/usbkey\n"
sudoers_file = "/etc/sudoers"

def add_permission():
    # 1. Vérifie si la ligne existe déjà pour éviter les doublons
    try:
        check_cmd = ["sudo", "grep", "-q", "mnt/usbkey", sudoers_file]
        result = subprocess.run(check_cmd)
        if result.returncode == 0:
            print("La règle est déjà présente dans sudoers, rien à faire.")
            return True
    except Exception as e:
        print(f"Erreur lors de la vérification : {e}")
        return False

    # 2. Ajoute la ligne à la fin du fichier via sudo et sh (pour gérer le flux de redirection >>)
    cmd = f"echo '{sudoers_line.strip()}' | sudo tee -a {sudoers_file} > /dev/null"
    
    try:
        process = subprocess.run(cmd, shell=True, check=True)
        if process.returncode == 0:
            print("Succès : La règle a été ajoutée à sudoers !")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'écriture dans sudoers : {e}")
        
    return False

if __name__ == "__main__":
    add_permission()