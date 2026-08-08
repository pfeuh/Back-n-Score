// Fonction centrale d'envoi vers ton serveur Flask (URL relative pour éviter les erreurs CORS)
function sendAudioCommand(command) {
    // Affichage de la commande dans l'élément HTML (assure-toi d'avoir un élément avec l'id 'command-display')
    const displayElement = document.getElementById('command-display');
    if (displayElement) {
        displayElement.textContent = command;
    }

    fetch('/audio_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: command
    })
    .then(response => {
        if (!response.ok) {
            console.error(`Erreur serveur pour la commande : ${command}`);
        }
    })
    .catch(error => console.error('Erreur réseau :', error));
}

// Gestionnaire d'événements clavier basé sur les raccourcis
function handleAudioKeyboardShortcuts(event) {
    // Évite de déclencher si l'utilisateur tape dans un champ de texte/input
    if (['INPUT', 'TEXTAREA'].includes(event.target.tagName)) {
        return;
    }

    // Gestion de la touche Espace pour éviter le scroll de la page
    if (event.key === ' ') {
        event.preventDefault();
    }

    // Si on utilise Ctrl + chiffre pour définir les repères (Set)
    if (event.ctrlKey) {
        switch (event.key) {
            case '1':
                sendAudioCommand('set_a');
                break;
            case '2':
                sendAudioCommand('set_b');
                break;
            case '3':
                sendAudioCommand('set_c');
                break;
            case '4':
                sendAudioCommand('set_d');
                break;
        }
        return; // On sort pour ne pas croiser avec les autres touches simples
    }

    // Raccourcis standards
    switch (event.key) {
        case ' ': // Espace -> Lecture / Pause
            sendAudioCommand('play');
            break;

        case 'Enter': // Touche Return normale et clavier numérique -> Stop
        case 'NumpadEnter':
            sendAudioCommand('stop');
            break;

        case 'ArrowLeft': // Flèche gauche -> Reculer
            sendAudioCommand('rewind');
            break;

        case 'ArrowRight': // Flèche droite -> Avancer
            sendAudioCommand('ff');
            break;

        case 'm': // 'm' ou 'M' -> Mute VLC
        case 'M':
            sendAudioCommand('volume_mute');
            break;

        case 's': // 's' ou 'S' -> Mute Systèmes tiers
        case 'S':
            sendAudioCommand('system_mute');
            break;

        case 'c': // 'c' ou 'C' -> Boucle A-B
        case 'C':
            sendAudioCommand('cycle');
            break;

        case '0': // '0' -> Retour début
            sendAudioCommand('goto_start');
            break;

        case '1': // Chiffre 1 -> Saut vers repère A
            sendAudioCommand('goto_a');
            break;

        case '2': // Chiffre 2 -> Saut vers repère B
            sendAudioCommand('goto_b');
            break;

        case '3': // Chiffre 3 -> Saut vers repère C
            sendAudioCommand('goto_c');
            break;

        case '4': // Chiffre 4 -> Saut vers repère D
            sendAudioCommand('goto_d');
            break;

        case 'f': // 'f' ou 'F' -> Plein écran (Fullscreen)
        case 'F':
            event.preventDefault();
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.error("Erreur lors du passage en plein écran :", err);
                });
            } else {
                document.exitFullscreen();
            }
            break;

        case 'r': // 'r' ou 'R' -> Rafraîchir la page (remplace F5)
        case 'R':
            event.preventDefault();
            location.reload();
            break;

        default:
            // Autre touche ignorée
            break;
    }
}

// Démarrage / Initialisation du listener global au chargement du script
document.addEventListener('keydown', handleAudioKeyboardShortcuts);