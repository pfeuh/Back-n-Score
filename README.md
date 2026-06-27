# Back'n Score 🎼🎯

## 📝 Description

**Back'n Score** est un serveur backend léger conçu pour stocker, organiser et distribuer des partitions musicales et leurs ressources associées.

Pour s'affranchir d'un système de gestion de base de données complexe (SGBD), le projet utilise une **fausse base de données** directement basée sur une arborescence de dossiers sur le disque dur. Le stockage est structuré comme une bibliothèque physique (Étagères, Livres, Pistes).

---

## 🛠️ Fonctionnalités Principales (La Fonction)

* **Serveur de Ressources Musicales** : Distribue tous les fichiers nécessaires à l'apprentissage et à l'exécution d'un morceau (partitions, audio, fichiers éditables).
* **Base de Données sur Disque ("File-based DB")** : Utilise l'arborescence native du système de fichiers pour trier et répertorier les œuvres sans aucune dépendance externe.
* **Légèreté & Portabilité** : Aucune base de données à installer ou à configurer. Sauvegarder ou déplacer la base de données se fait par un simple copier-coller du dossier racine.
* **A partir d'Android 4** : Les vieilles tablettes de 2015 jusqu'a celle d'aujourd'hui sont gérées par Back'n Score ansi que tout ce qui peut faire tourner un navigateur web capable d'afficher des images.
* **A base de pooling** : chaque client demande cycliquement quel est le track en cours. Chaque client peut aussi sélectionner son instrument.

---

## 📂 Organisation de la Base de Données (L'Arborescence)

La "fausse base de données" respecte scrupuleusement la hiérarchie suivante :

1. **Étagère (Dossier)** : Peut contenir d'autres sous-étagères (pour affiner le classement par style, époque, compositeur...) ou des Livres.
2. **Livre (Dossier)** : Représente un recueil ou un album, et contient un ou plusieurs *Tracks*.
3. **Track (Dossier)** : Représente le morceau en lui-même. C'est le conteneur final qui regroupe toutes les données du morceau :
   * `*.pdf` : La ou les partitions prêtes à être lues ou imprimées.
   * `*.mp3` : Le fichier audio pour l'écoute ou l'accompagnement.
   * `*.mscz` : Le fichier source MuseScore pour éditer ou modifier la partition.
   * `trackname.txt` : Un fichier texte brut encodé en **UTF-8** contenant le titre officiel du morceau.

---

## ⚙️ Architecture & Modèle de Données

```text
+-----------------------------------------------------------------------+
|                           CLIENT / FRONTEND                           |
|                 (Application Web, Mobile ou Tablette)                 |
+-----------------------------------------------------------------------+
                                    |
                                    | Requêtes HTTP (GET / POST)
                                    v
+-----------------------------------------------------------------------+
|                         BACK'N SCORE SERVER                           |
|                                                                       |
|   +--------------------+          +-------------------------------+   |
|   |   Routeur / API    | -------> |    Gestionnaire de Fichiers   |   |
|   | (Requêtes clients) |          | (Navigation & Lecture Disque) |   |
|   +--------------------+          +-------------------------------+   |
|                                                   |                   |
+---------------------------------------------------|-------------------+
                                                    |
                                                    | Accès I/O Direct
                                                    v
+-----------------------------------------------------------------------+
|                     ARBORESCENCE SUR LE DISQUE                        |
|                                                                       |
| [Étagère_Racine/]                                                     |
|    ├── [Étagère_Classique/]  <-- (Une étagère peut contenir une autre)|
|    │     └── [Livre_Chopin_Nocturnes/]                                |
|    │           └── [Track_Nocturne_Op9_No2/]                          |
|    │                 ├── trackname.txt  (Nom du morceau en UTF-8)     |
|    │                 ├── piano.pdf  (Fichier de lecture)              |
|    │                 ├── ...                                          |
|    │                 ├── tutti.pdf      (Fichier de lecture)          |
|    │                 ├── backtrack.mp3      (Fichier d'écoute)        |
|    │                 ├── melody.mp3      (Fichier d'écoute)           |
|    │                 ├── slowed-down.mp3      (Fichier d'écoute)      |
|    │                 └── projet.mscz    (Fichier éditable MuseScore)  |
|    └── [Étagère_Jazz/]                                                |
|          └── [Livre_Miles_Davis_Kind_Of_Blue/]                        |
|                └── [Track_So_What/]                                   |
|                      ├── trackname.txt                                |
|                      └── ...                                          |
+-----------------------------------------------------------------------+
