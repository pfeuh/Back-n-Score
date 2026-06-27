import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ExtracteurAudiobooksApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Extracteur de Books du Dimanche")
        self.root.geometry("1000x680")
        self.root.minsize(800, 550)

        # Configuration du redimensionnement de la grille principale
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=3)  # Arbre
        self.root.grid_columnconfigure(1, weight=1)  # Extensions

        # Variables de données
        self.src_dir = tk.StringVar()
        self.dst_dir = tk.StringVar()
        self.output_format = tk.StringVar(value="folder")

        # { node_id: {"type": "dir"|"book"|"track", "name": str, "path": str, "checked": bool, "children": list} }
        self.tree_data = {}
        self.extensions_vars = {}

        self.creer_interface()

    def creer_interface(self):
        # ==========================================
        # 1. BLOC HAUT : Sélection Source
        # ==========================================
        frame_haut = tk.LabelFrame(
            self.root, text=" 1. Répertoire Source ", padx=10, pady=10
        )
        frame_haut.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        frame_haut.grid_columnconfigure(1, weight=1)

        tk.Label(frame_haut, text="Source :").grid(row=0, column=0, sticky="w")
        entry_src = tk.Entry(
            frame_haut, textvariable=self.src_dir, state="readonly"
        )
        entry_src.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(
            frame_haut, text="Parcourir...", command=self.choisir_source
        ).grid(row=0, column=2)

        # ==========================================
        # 2. BLOC MILIEU GAUCHE : Arbre Récursif Complet
        # ==========================================
        frame_arbre = tk.LabelFrame(
            self.root, text=" 2. Arborescence des Dossiers ", padx=10, pady=10
        )
        frame_arbre.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=5)
        frame_arbre.grid_rowconfigure(0, weight=1)
        frame_arbre.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame_arbre, columns=("path"), show="tree")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_tree = ttk.Scrollbar(
            frame_arbre, orient="vertical", command=self.tree.yview
        )
        scroll_tree.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll_tree.set)

        self.tree.bind("<Button-1>", self.gerer_clic_arbre)

        # ==========================================
        # 3. BLOC MILIEU DROITE : Panneau Extensions
        # ==========================================
        self.frame_ext = tk.LabelFrame(
            self.root, text=" 3. Extensions ", padx=10, pady=10
        )
        self.frame_ext.grid(row=1, column=1, sticky="nsew", padx=(5, 15), pady=5)

        self.canvas_ext = tk.Canvas(self.frame_ext, borderwidth=0)
        self.scroll_ext = ttk.Scrollbar(
            self.frame_ext, orient="vertical", command=self.canvas_ext.yview
        )
        self.scrollable_frame_ext = tk.Frame(self.canvas_ext)

        self.scrollable_frame_ext.bind(
            "<Configure>",
            lambda e: self.canvas_ext.configure(
                scrollregion=self.canvas_ext.bbox("all")
            ),
        )
        self.canvas_ext.create_window(
            (0, 0), window=self.scrollable_frame_ext, anchor="nw"
        )
        self.canvas_ext.configure(yscrollcommand=self.scroll_ext.set)

        self.canvas_ext.pack(side="left", fill="both", expand=True)
        self.scroll_ext.pack(side="right", fill="y")

        # ==========================================
        # 4. BLOC BAS : Destination & Options de sortie
        # ==========================================
        frame_bas = tk.LabelFrame(
            self.root, text=" 4. Extraction & Destination ", padx=10, pady=10
        )
        frame_bas.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        frame_bas.grid_columnconfigure(1, weight=1)

        tk.Label(frame_bas, text="Destination :").grid(row=0, column=0, sticky="w")
        entry_dst = tk.Entry(
            frame_bas, textvariable=self.dst_dir, state="readonly"
        )
        entry_dst.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(
            frame_bas, text="Parcourir...", command=self.choisir_destination
        ).grid(row=0, column=2)

        # Zone d'actions et de progression
        frame_actions = tk.Frame(frame_bas, pady=10)
        frame_actions.grid(row=1, column=0, columnspan=3, sticky="ew")

        tk.Label(frame_actions, text="Format de sortie : ").pack(side="left")
        tk.Radiobutton(
            frame_actions,
            text="📂 Dossier normal",
            variable=self.output_format,
            value="folder",
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            frame_actions,
            text="🤐 Archive ZIP",
            variable=self.output_format,
            value="zip",
        ).pack(side="left", padx=10)

        self.btn_extraire = tk.Button(
            frame_actions,
            text="🚀 Lancer l'extraction",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            command=self.lancer_extraction,
        )
        self.btn_extraire.pack(side="right", padx=10)

        # Barre de progression ajoutée en bas de la zone d'action
        self.progress_bar = ttk.Progressbar(
            frame_bas, orient="horizontal", mode="determinate"
        )
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 0))

    # ==========================================
    # SCAN & RECONSTRUCTION DE L'ARBRE DISQUE
    # ==========================================
    def choisir_source(self):
        dossier = filedialog.askdirectory(title="Sélectionner le dossier source")
        if dossier:
            self.src_dir.set(dossier)
            self.tree.delete(*self.tree.get_children())
            self.tree_data.clear()
            for widget in self.scrollable_frame_ext.winfo_children():
                widget.destroy()
            self.extensions_vars.clear()
            self.progress_bar["value"] = 0

            threading.Thread(
                target=self.scanner_repertoire, args=(dossier,), daemon=True
            ).start()

    def scanner_repertoire(self, root_path):
        extensions_trouvees = set()
        tracks_detectees = []

        # 1er passage : Trouver toutes les tracks valides
        for root, dirs, files in os.walk(root_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    extensions_trouvees.add(ext.lower())

            if "trackname.txt" in files:
                tracks_detectees.append(root)

        # Si aucune track, on s'arrête
        if not tracks_detectees:
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Info", "Aucun fichier trackname.txt trouvé."
                ),
            )
            return

        # Déterminer tous les dossiers intermédiaires nécessaires
        chemins_a_garder = set()
        books_detectes = set()

        for track_path in tracks_detectees:
            chemins_a_garder.add(track_path)
            parent = os.path.dirname(track_path)
            if parent and parent != root_path:
                books_detectes.add(parent)

            # On remonte jusqu'à la racine pour garder la chaîne de dossiers parents
            while parent and parent != root_path and len(parent) >= len(root_path):
                chemins_a_garder.add(parent)
                parent = os.path.dirname(parent)

        # Événement de mise à jour de l'interface
        self.root.after(
            0,
            self.construire_arbre_disque,
            root_path,
            chemins_a_garder,
            books_detectes,
            tracks_detectees,
            extensions_trouvees,
        )

    def construire_arbre_disque(
        self, root_path, chemins_valides, books, tracks, extensions
    ):
        # Dictionnaire pour retrouver les identifiants de nœuds Treeview par leur chemin absolu
        chemin_vers_id = {root_path: ""}

        # On trie par longueur de chemin pour créer les parents avant les enfants
        pour_construction = sorted(list(chemins_valides), key=len)

        for path in pour_construction:
            parent_path = os.path.dirname(path)
            parent_id = chemin_vers_id.get(parent_path, "")

            nom_dossier = os.path.basename(path)

            # Déterminer le type du dossier pour l'icône/comportement
            if path in tracks:
                node_type = "track"
            elif path in books:
                node_type = "book"
            else:
                node_type = "dir"

            # Insertion dans l'arbre Tkinter
            node_id = self.tree.insert(
                parent_id, "end", text=f"☐ {nom_dossier}", values=(path,)
            )
            chemin_vers_id[path] = node_id

            # Stockage des métadonnées
            self.tree_data[node_id] = {
                "type": node_type,
                "name": nom_dossier,
                "path": path,
                "checked": False,
                "children": [],
                "parent": parent_id if parent_id != "" else None,
            }

            # Lier l'enfant au parent dans notre dictionnaire personnalisé
            if parent_id in self.tree_data:
                self.tree_data[parent_id]["children"].append(node_id)

        # Remplissage du panneau des extensions à droite
        for ext in sorted(list(extensions)):
            var = tk.BooleanVar(value=(ext == ".txt"))
            self.extensions_vars[ext] = var
            state = "disabled" if ext == ".txt" else "normal"
            cb = tk.Checkbutton(
                self.scrollable_frame_ext, text=ext, variable=var, state=state
            )
            cb.pack(anchor="w", padx=5, pady=2)

        messagebox.showinfo(
            "Scan terminé",
            f"Arborescence chargée !\n{len(books)} Book(s) identifié(s).",
        )

    # ==========================================
    # LOGIQUE DE COCHAGE EN CASCADE (DESCENDANT)
    # ==========================================
    def gerer_clic_arbre(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id or item_id not in self.tree_data:
            return

        # On bascule l'état de l'élément cliqué
        new_state = not self.tree_data[item_id]["checked"]
        self.propager_cochage_descendant(item_id, new_state)

    def propager_cochage_descendant(self, node_id, state):
        """Coche ou décoche récursivement tous les sous-dossiers et tracks."""
        node = self.tree_data[node_id]
        node["checked"] = state

        symbole = "☑" if state else "☐"
        self.tree.item(node_id, text=f"{symbole} {node['name']}")

        for child_id in node["children"]:
            self.propager_cochage_descendant(child_id, state)

    # ==========================================
    # PROCESSUS D'EXTRACTION
    # ==========================================
    def choisir_destination(self):
        dossier = filedialog.askdirectory(title="Sélectionner le dossier cible")
        if dossier:
            self.dst_dir.set(dossier)

    def lancer_extraction(self):
        src = self.src_dir.get()
        dst = self.dst_dir.get()
        fmt = self.output_format.get()

        if not src or not dst:
            messagebox.showwarning("Attention", "Dossiers source/cible manquants !")
            return

        # On extrait uniquement les dossiers de type "track" qui sont cochés
        tracks_a_copier = [
            info
            for info in self.tree_data.values()
            if info["type"] == "track" and info["checked"]
        ]
        ext_a_garder = [
            ext for ext, var in self.extensions_vars.items() if var.get()
        ]

        if not tracks_a_copier:
            messagebox.showwarning(
                "Attention",
                "Veuillez cocher des éléments (ou des dossiers contenant des thèmes) à extraire.",
            )
            return

        if not ext_a_garder:
            messagebox.showwarning(
                "Attention", "Veuillez cocher au moins une extension."
            )
            return

        # Configuration de la barre de progression
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(tracks_a_copier)

        self.btn_extraire.config(state="disabled", text="Extraction en cours...")
        threading.Thread(
            target=self.processus_copie,
            args=(tracks_a_copier, src, ext_a_garder, dst, fmt),
            daemon=True,
        ).start()

    def processus_copie(self, tracks, src_root, extensions, dest_root, format_sortie):
        try:
            dossier_travail = (
                os.path.join(dest_root, "Extraction_Temporaire")
                if format_sortie == "zip"
                else dest_root
            )
            compteur_fichiers = 0

            for index, track in enumerate(tracks):
                track_src_path = track["path"]

                # Pour conserver l'intégralité de l'arborescence sélectionnée depuis la racine source :
                rel_path = os.path.relpath(track_src_path, src_root)
                cible_dir = os.path.join(dossier_travail, rel_path)

                files = os.listdir(track_src_path)
                for file in files:
                    src_file = os.path.join(track_src_path, file)
                    if os.path.isfile(src_file):
                        _, ext = os.path.splitext(file)
                        if ext.lower() in extensions:
                            if not os.path.exists(cible_dir):
                                os.makedirs(cible_dir)

                            dst_file = os.path.join(cible_dir, file)
                            shutil.copy2(src_file, dst_file)
                            compteur_fichiers += 1

                # Mise à jour asynchrone de la barre de progression
                self.root.after(0, self.mettre_a_jour_barre, index + 1)

            if format_sortie == "zip":
                archive_path = os.path.join(dest_root, "Extraction_Books")
                shutil.make_archive(archive_path, "zip", dossier_travail)
                shutil.rmtree(dossier_travail)

            self.root.after(
                0,
                self.fin_extraction,
                True,
                f"Extraction réussie !\n{compteur_fichiers} fichiers extraits.",
            )

        except Exception as e:
            self.root.after(0, self.fin_extraction, False, str(e))

    def mettre_a_jour_barre(self, valeur):
        self.progress_bar["value"] = valeur

    def fin_extraction(self, succes, message):
        self.btn_extraire.config(state="normal", text="🚀 Lancer l'extraction")
        if succes:
            messagebox.showinfo("Succès !", message)
        else:
            messagebox.showerror("Erreur", f"Une erreur est survenue :\n{message}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExtracteurAudiobooksApp(root)
    root.mainloop()