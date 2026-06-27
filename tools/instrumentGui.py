#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import stat

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_path = os.path.join(parent_dir, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from instruments import INSTRUMENTS, TONALITES, VIRTUAL_INSTRUMENTS
from getScoreName import getScoreName, MODE_POPULAR, MODE_CLASSIQUE, getScoreNameError, GROUP_BASSE, GROUP_POMPE

DATABASE = "../database"

class BackNScoreApp:
    def __init__(self, root, db_root):
        self.root = root
        self.db_root = db_root
        self.tracks = self.scan_database()
        self.details_window = None  # Garde-fou pour n'avoir qu'une popup
        
        # --- OPTIONS DU MENU ---
        instrs_noms = list(INSTRUMENTS.keys())
        tonas_noms = [t for t in TONALITES if t != "NP"]
        tous_les_choix = set(instrs_noms) | set(tonas_noms)
        pour_supprimer = {"trombone_virtual", "NP"} 
        self.options = sorted(list(tous_les_choix - pour_supprimer))
        
        # --- UI ---
        left = tk.Frame(root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)
        
        self.mode_var = tk.StringVar(value="POPULAR")
        tk.Label(left, text="Mode de recherche:", font=('Helvetica', 10, 'bold')).pack(anchor="w")
        tk.Radiobutton(left, text="Classique", variable=self.mode_var, value="CLASSIQUE").pack(anchor="w")
        tk.Radiobutton(left, text="Populaire", variable=self.mode_var, value="POPULAR").pack(anchor="w")
        
        tk.Label(left, text="\nInstrument ou Tona:", font=('Helvetica', 10, 'bold')).pack(anchor="w")
        self.choice_var = tk.StringVar(value="SIb")
        self.menu = ttk.Combobox(left, textvariable=self.choice_var, values=self.options, state="readonly")
        self.menu.pack(pady=5, fill=tk.X)
        
        tk.Label(left, text="\nVoix:", font=('Helvetica', 10, 'bold')).pack(anchor="w")
        self.voice_var = tk.IntVar(value=1)
        tk.Spinbox(left, from_=1, to=4, textvariable=self.voice_var).pack(pady=5, fill=tk.X)
        
        tk.Button(left, text="SCANNER", command=self.update_table, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold')).pack(pady=20, fill=tk.X)
        
        self.tree = ttk.Treeview(root, columns=("T", "Ton", "F"), show='headings')
        # Double-clic pour les détails (plus stable que le clic simple)
        self.tree.bind("<Double-1>", self.show_details)

        self.tree.heading("T", text="Titre"); self.tree.heading("Ton", text="Ton"); self.tree.heading("F", text="Fichier PDF")
        self.tree.column("T", width=250); self.tree.column("Ton", width=50, anchor="center"); self.tree.column("F", width=200)
        self.tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.update_table()

    def scan_database(self):
        found = []
        if not os.path.exists(self.db_root): return found
        for root_dir, dirs, files in os.walk(self.db_root):
            if "trackname.txt" in files:
                try:
                    with open(os.path.join(root_dir, "trackname.txt"), 'r', encoding='utf-8') as f:
                        title = f.read().strip()
                    rel_path = os.path.relpath(root_dir, self.db_root)
                    found.append({"title": title, "location": rel_path})
                except: pass
        return found

    def update_table(self):
        self.root.config(cursor="watch")
        self.root.update()
        for i in self.tree.get_children(): self.tree.delete(i)
        selected_mode = MODE_CLASSIQUE if self.mode_var.get() == "CLASSIQUE" else MODE_POPULAR
        for t in self.tracks:
            path = os.path.join(self.db_root, t['location'])
            res = getScoreName(path, self.choice_var.get(), voice=self.voice_var.get(), mode=selected_mode)
            self.tree.insert("", "end", values=(t['title'], "-", res if res else "---"))
        self.root.config(cursor="")
        for widget in self.root.winfo_children():
            widget.config(cursor="")
        self.root.update()
        self.root.update_idletasks()
        self.root.event_generate('<Motion>', warp=False)

    def show_details(self, event):
        selection = self.tree.selection()
        if not selection: return
        
        # Sécurité : Si une fenêtre est déjà ouverte, on la ferme avant d'ouvrir la nouvelle
        if self.details_window is not None and self.details_window.winfo_exists():
            self.details_window.destroy()

        titre = self.tree.item(selection[0], "values")[0]
        track_info = next((t for t in self.tracks if t['title'] == titre), None)
        if not track_info: return

        full_path = os.path.join(self.db_root, track_info['location'])
        
        # --- PRÉPARATION DES DONNÉES ---
        header = f"{'Droits':<11} | {'Taille':<9} | {'Création':<15} | {'Modif':<15} | {'Nom'}"
        lines = [f"Répertoire : [DB]/{track_info['location']}\n", header]
        lines.append("-" * 90)

        try:
            with os.scandir(full_path) as it:
                for entry in sorted(it, key=lambda e: e.name.lower()):
                    st = entry.stat()
                    perm = stat.filemode(st.st_mode)
                    size = f"{st.st_size / 1024:.1f} Ko"
                    dt_c = datetime.fromtimestamp(st.st_ctime).strftime('%d/%m/%y %H:%M')
                    dt_m = datetime.fromtimestamp(st.st_mtime).strftime('%d/%m/%y %H:%M')
                    name = f"[{entry.name}]" if entry.is_dir() else entry.name
                    lines.append(f"{perm:<11} | {size:>9} | {dt_c:<15} | {dt_m:<15} | {name}")
        except Exception as e:
            lines.append(f"Erreur : {e}")

        # --- CRÉATION DE LA POPUP (UNIQUE) ---
        self.details_window = tk.Toplevel(self.root)
        self.details_window.title(f"Inspection Matrix : {titre}")
        self.details_window.geometry("950x450")
        
        frame = tk.Frame(self.details_window, bg="#1e1e1e")
        frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(frame, font=("Courier", 10), padx=15, pady=15, 
                            bg="#1e1e1e", fg="#33ff33", yscrollcommand=scroll.set)
        text_area.insert(tk.END, "\n".join(lines))
        text_area.config(state=tk.DISABLED)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=text_area.yview)

if __name__ == "__main__":

    root = tk.Tk()
    root.title("Back'n Score - Visualiseur")
    root.geometry("900x500")
    app = BackNScoreApp(root, "../database")
    root.mainloop()
