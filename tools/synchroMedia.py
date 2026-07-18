#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CONFIG_FILE = ".synchro_config.json"


class SynchroApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Back'n Score - Synchro Base de Données")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        # Chemins par défaut initiaux
        default_src = os.path.expanduser("~")
        default_dest = "/media/" + os.getlogin()

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    default_src = config.get("source", default_src)
                    default_dest = config.get("destination", default_dest)
            except Exception:
                pass

        self.source_dir = tk.StringVar(value=default_src)
        self.dest_dir = tk.StringVar(value=default_dest)

        self.create_widgets()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(
                    {
                        "source": self.source_dir.get(),
                        "destination": self.dest_dir.get(),
                    },
                    f,
                )
        except Exception:
            pass

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SECTION SOURCE ---
        src_label = ttk.Label(
            main_frame,
            text="Source (Base PC Ubuntu) :",
            font=("Helvetica", 11, "bold"),
        )
        src_label.pack(anchor=tk.W, pady=(0, 5))

        src_frame = ttk.Frame(main_frame)
        src_frame.pack(fill=tk.X, pady=(0, 15))

        src_entry = ttk.Entry(
            src_frame, textvariable=self.source_dir, font=("Helvetica", 10)
        )
        src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        src_btn = ttk.Button(
            src_frame, text="Parcourir...", command=self.browse_source
        )
        src_btn.pack(side=tk.RIGHT)

        # --- SECTION DESTINATION ---
        dest_label = ttk.Label(
            main_frame,
            text="Destination (Nouvelle clé USB) :",
            font=("Helvetica", 11, "bold"),
        )
        dest_label.pack(anchor=tk.W, pady=(0, 5))

        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=(0, 20))

        dest_entry = ttk.Entry(
            dest_frame, textvariable=self.dest_dir, font=("Helvetica", 10)
        )
        dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        dest_btn = ttk.Button(
            dest_frame, text="Parcourir...", command=self.browse_dest
        )
        dest_btn.pack(side=tk.RIGHT)

        # --- BARRE DE PROGRESSION & STATUT ---
        self.status_label = ttk.Label(
            main_frame, text="Prêt", font=("Helvetica", 10, "italic")
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 2))

        self.progress = ttk.Progressbar(
            main_frame, orient="horizontal", mode="determinate"
        )
        self.progress.pack(fill=tk.X, pady=(0, 15))

        # --- BOUTON DE LANCEMENT ---
        self.sync_btn = ttk.Button(
            main_frame, text="Lancer la Synchronisation", command=self.run_sync
        )
        self.sync_btn.pack(pady=10, ipady=5, fill=tk.X)

        # --- LOGS DE TRANSFERT ---
        log_label = ttk.Label(main_frame, text="Journal de suivi / Analyse des erreurs :")
        log_label.pack(anchor=tk.W, pady=(5, 2))

        self.log_text = tk.Text(
            main_frame,
            height=12,
            wrap=tk.WORD,
            background="#1e1e1e",
            foreground="#ffffff",
            font=("Monospace", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def browse_source(self):
        directory = filedialog.askdirectory(
            initialdir=self.source_dir.get(), title="Sélectionner la base PC"
        )
        if directory:
            self.source_dir.set(directory)
            self.save_config()

    def browse_dest(self):
        directory = filedialog.askdirectory(
            initialdir=self.dest_dir.get(), title="Sélectionner la clé USB"
        )
        if directory:
            self.dest_dir.set(directory)
            self.save_config()

    def run_sync(self):
        src = self.source_dir.get()
        dest = self.dest_dir.get()

        if not src or not dest:
            messagebox.showerror("Erreur", "Veuillez remplir les deux chemins.")
            return

        if not os.path.exists(src) or not os.path.exists(dest):
            messagebox.showerror(
                "Erreur", "L'un des dossiers spécifiés n'existe pas."
            )
            return

        self.save_config()

        if not src.endswith("/"):
            src += "/"

        self.status_label.config(
            text="Analyse de la base de données (calcul du nombre de fichiers)..."
        )
        self.root.update()

        # Calcul du nombre de fichiers restant (sans filtre, options USB standards)
        count_cmd = ["rsync", "-rntvO", "--modify-window=1", "--delete", src, dest]
        try:
            res = subprocess.run(
                count_cmd, stdout=subprocess.PIPE, text=True, check=True
            )
            lines = res.stdout.splitlines()

            total_files = 0
            for line in lines:
                if (
                    line
                    and not line.endswith("/")
                    and not line.startswith("sending incremental")
                    and not line.startswith("total size")
                ):
                    total_files += 1

            if total_files == 0:
                self.status_label.config(
                    text="La clé USB est déjà parfaitement à jour."
                )
                messagebox.showinfo(
                    "Déjà à jour", "Aucun fichier à synchroniser."
                )
                return

            self.progress["maximum"] = total_files

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur lors du calcul des fichiers : {str(e)}"
            )
            return

        # --- TRANSFERT RÉEL SANS FORÇAGE ---
        self.sync_btn.config(state=tk.DISABLED)
        self.log_text.delete("1.0", tk.END)
        self.progress["value"] = 0
        self.status_label.config(
            text=f"Synchronisation en cours ({total_files} fichiers à traiter)..."
        )
        self.root.update()

        # Options rsync standards pour supports externes
        sync_cmd = [
            "rsync",
            "-rtvO",
            "--modify-window=1",
            "--delete",
            src,
            dest,
        ]

        errors_found = []

        try:
            process = subprocess.Popen(
                sync_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # On capte stderr pour lister les 26 fichiers rejetés
                text=True,
                bufsize=1,
            )

            current_count = 0
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    self.log_text.insert(tk.END, line)
                    self.log_text.see(tk.END)

                    cleaned = line.strip()
                    if (
                        cleaned
                        and not cleaned.endswith("/")
                        and not cleaned.startswith("sending incremental")
                        and not cleaned.startswith("total size")
                        and not cleaned.startswith("bytes")
                    ):
                        current_count += 1
                        if current_count <= total_files:
                            self.progress["value"] = current_count
                            self.status_label.config(
                                text=f"Progression : {current_count} / {total_files} fichiers"
                            )

                    self.root.update()

            # Extraction fine des erreurs générées par rsync sur ces fichiers
            stderr_output = process.stderr.read()
            if stderr_output:
                for err_line in stderr_output.splitlines():
                    if "failed:" in err_line or "error" in err_line.lower():
                        errors_found.append(err_line)

            if process.returncode == 0 and not errors_found:
                self.status_label.config(text="Synchronisation terminée avec succès !")
                messagebox.showinfo(
                    "Succès", "La clé USB est prête et 100% identique au PC !"
                )
            else:
                self.status_label.config(
                    text=f"Terminé. {len(errors_found)} fichier(s) refusé(s) par la clé."
                )
                
                # Insertion de la liste des 26 exclus tout en haut de la console
                self.log_text.insert(
                    "1.0",
                    f"========== LISTE DES {len(errors_found)} FICHIERS CONSERVÉS SUR PC MAIS INTEGRALEMENT IGNORÉS PAR LA CLÉ ==========\n\n",
                )
                for err in reversed(errors_found):
                    self.log_text.insert("3.0", f" ❌ {err}\n")

                messagebox.showwarning(
                    "Fichiers rejetés",
                    f"La synchronisation globale est finie, mais {len(errors_found)} fichiers n'ont pas pu être écrits.\n\nLa liste complète de ces fichiers s'affiche en haut de la zone noire.",
                )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur pendant l'exécution : {str(e)}"
            )

        finally:
            self.sync_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = SynchroApp(root)
    root.mainloop()