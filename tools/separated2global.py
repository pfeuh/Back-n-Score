#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from separated2global_core import separated2global_core

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_path = os.path.join(parent_dir, "scripts")
print(scripts_path)
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import des instruments depuis instruments.py
try:
    from instruments import INSTRUMENTS, VIRTUAL_INSTRUMENTS
except ImportError:
    INSTRUMENTS = {}
    VIRTUAL_INSTRUMENTS = {}

CONFIG_FILE = os.path.join(current_dir, "separated2global.json")
MP3_TYPES_FILE = os.path.join(current_dir, "mp3_types.json")

class Separated2GlobalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Separated2Global - Gestionnaire de partitions et MP3")
        self.root.geometry("750x760")
        self.root.minsize(700, 700)

        # Variables Tkinter
        self.input_dir_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.target_name_var = tk.StringVar()  # Nouveau champ pour le nom cible des PDF
        self.instrument_var = tk.StringVar()
        
        # Structures pour les cases à cocher personnalisées
        self.mp3_vars = {} 
        self.mp3_buttons = {}

        self.load_config()
        self.create_widgets()

    def load_config(self):
        """ Charge la configuration depuis config.json """
        self.saved_config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.saved_config = json.load(f)
                    self.input_dir_var.set(self.saved_config.get("input_dir", ""))
                    self.output_dir_var.set(self.saved_config.get("output_dir", ""))
                    self.target_name_var.set(self.saved_config.get("target_name", ""))
                    self.instrument_var.set(self.saved_config.get("selected_instrument", ""))
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration : {e}")

    def save_config(self):
        """ Sauvegarde complète dans config.json """
        mp3_states = {m_type: var.get() for m_type, var in self.mp3_vars.items()}
        config = {
            "input_dir": self.input_dir_var.get(),
            "output_dir": self.output_dir_var.get(),
            "target_name": self.target_name_var.get(),
            "selected_instrument": self.instrument_var.get(),
            "mp3_states": mp3_states
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration : {e}")

    def browse_input(self):
        dir_path = filedialog.askdirectory(title="Sélectionner le dossier d'entrée")
        if dir_path:
            self.input_dir_var.set(dir_path)
            # Pré-remplir automatiquement le nom cible si le champ est vide
            if not self.target_name_var.get():
                default_name = os.path.basename(dir_path)
                self.target_name_var.set(default_name)
            self.save_config()

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Sélectionner le dossier de sortie")
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.save_config()

    def toggle_custom_checkbox(self, m_type):
        """ Bascule l'état de la case personnalisée et met à jour son affichage visuel """
        current_val = self.mp3_vars[m_type].get()
        new_val = not current_val
        self.mp3_vars[m_type].set(new_val)
        
        symbol = "☒" if new_val else "☐"
        self.mp3_buttons[m_type].config(text=f" {symbol}  {m_type}")
        self.save_config()

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Dossiers
        self.root.rowconfigure(1, weight=0)  # Nom PDF Cible
        self.root.rowconfigure(2, weight=0)  # Instrument
        self.root.rowconfigure(3, weight=1)  # Types MP3
        self.root.rowconfigure(4, weight=0)  # Boutons

        # --- Cadre Chemins ---
        path_frame = ttk.LabelFrame(self.root, text="Dossiers", padding=10)
        path_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        path_frame.columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="Dossier d'entrée :").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(path_frame, textvariable=self.input_dir_var).grid(row=0, column=1, sticky="ew", padx=10, pady=6)
        ttk.Button(path_frame, text="Parcourir...", command=self.browse_input).grid(row=0, column=2, pady=6)

        ttk.Label(path_frame, text="Dossier de sortie :").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(path_frame, textvariable=self.output_dir_var).grid(row=1, column=1, sticky="ew", padx=10, pady=6)
        ttk.Button(path_frame, text="Parcourir...", command=self.browse_output).grid(row=1, column=2, pady=6)

        # --- Cadre Nom Cible PDF ---
        pdf_frame = ttk.LabelFrame(self.root, text="Nom de sortie pour les PDF", padding=10)
        pdf_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        pdf_frame.columnconfigure(1, weight=1)

        ttk.Label(pdf_frame, text="Nom du dossier/fichier cible :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        target_entry = ttk.Entry(pdf_frame, textvariable=self.target_name_var)
        target_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        target_entry.bind("<KeyRelease>", lambda e: self.save_config())

        # --- Cadre Instrument ---
        inst_frame = ttk.LabelFrame(self.root, text="Sélection de l'instrument", padding=10)
        inst_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        inst_frame.columnconfigure(1, weight=1)

        ttk.Label(inst_frame, text="Instrument cible :").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        all_instruments = sorted(list(INSTRUMENTS.keys()) + list(VIRTUAL_INSTRUMENTS.keys()))
        
        self.inst_combo = ttk.Combobox(inst_frame, textvariable=self.instrument_var, values=all_instruments, state="readonly")
        self.inst_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        if self.instrument_var.get() not in all_instruments and all_instruments:
            self.inst_combo.current(0)
        
        self.inst_combo.bind("<<ComboboxSelected>>", lambda e: self.save_config())

        # --- Cadre Types de MP3 ---
        mp3_frame = ttk.LabelFrame(self.root, text="Types de MP3 à extraire", padding=10)
        mp3_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=10)
        mp3_frame.columnconfigure(0, weight=1)
        mp3_frame.columnconfigure(1, weight=1)

        mp3_types = []
        if os.path.exists(MP3_TYPES_FILE):
            try:
                with open(MP3_TYPES_FILE, "r", encoding="utf-8") as f:
                    mp3_types = json.load(f)
            except Exception as e:
                print(f"Erreur lecture mp3_types.json : {e}")
        
        if not mp3_types:
            mp3_types = ["backtrack", "demo", "melody", "noBass", "noDrum", "noPiano", "noSecond", "noWind"]

        saved_mp3_states = self.saved_config.get("mp3_states", {})

        for idx, mp3_type in enumerate(mp3_types):
            initial_state = saved_mp3_states.get(mp3_type, True)
            var = tk.BooleanVar(value=initial_state)
            self.mp3_vars[mp3_type] = var

            symbol = "☒" if initial_state else "☐"
            
            btn = tk.Button(
                mp3_frame, 
                text=f" {symbol}  {mp3_type}", 
                anchor="w", 
                relief="flat", 
                bg="#f0f0f0", 
                activebackground="#e0e0e0",
                font=("Arial", 10),
                command=lambda t=mp3_type: self.toggle_custom_checkbox(t)
            )
            
            self.mp3_buttons[mp3_type] = btn
            row = idx // 2
            col = idx % 2
            btn.grid(row=row, column=col, sticky="ew", padx=20, pady=6)

        # --- Cadre Contrôles / Boutons ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=10)
        control_frame.columnconfigure(0, weight=1)

        btn_container = ttk.Frame(control_frame)
        btn_container.grid(row=0, column=0, sticky="e")

        self.btn_abort = ttk.Button(btn_container, text="Abandonner", command=self.on_abort, width=12)
        self.btn_abort.grid(row=0, column=0, padx=8)

        self.btn_execute = ttk.Button(btn_container, text="Exécuter", command=self.on_execute, width=12)
        self.btn_execute.grid(row=0, column=1, padx=8)

    def on_execute(self):
        in_dir = self.input_dir_var.get()
        out_dir = self.output_dir_var.get()
        target_name = self.target_name_var.get()
        selected_instrument = self.instrument_var.get()
        selected_mp3_types = [m_type for m_type, var in self.mp3_vars.items() if var.get()]

        if not in_dir or not out_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier d'entrée et un dossier de sortie.")
            return

        print("--- Lancement demandé ---")
        print(f"Entrée : {in_dir}")
        print(f"Sortie : {out_dir}")
        print(f"Nom cible PDF : {target_name}")
        print(f"Instrument : {selected_instrument}")
        print(f"Types MP3 sélectionnés : {selected_mp3_types}")
        
        #~ messagebox.showinfo("Info", "Paramètres validés et mémorisés !")
        separated2global_core(in_dir, out_dir, target_name, selected_instrument, selected_mp3_types)

    def on_abort(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = Separated2GlobalApp(root)
    root.mainloop()