
/* ici on affiche les images jpg copies des pages pdf */

var loadedPages = [];
var scoreInstrument = null;
var scoreNbPages = null;
var currentPage = 0;
var nbShowedPages = 0;
var loadedTrackPath = null;  // Le dossier actuel
var loadedInstrumentName = null; // L'instrument actuel

function getScore(instrument, nb_pages) {
    var track = track_location.get();
    
    // --- VÉRIFICATION DE LA SIGNATURE ---
    // Si c'est le même morceau ET le même instrument
    if (track === loadedTrackPath && instrument === loadedInstrumentName) {
        refreshScore(); 
        return; 
    }

    // --- SI NOUVEAU SCORE : INITIALISATION ---
    loadedTrackPath = track;
    loadedInstrumentName = instrument;
    scoreInstrument = instrument;
    scoreNbPages = nb_pages;
    loadedPages = [];
    currentPage = 0;
    
    var timestamp = new Date().getTime();

    // On précharge les objets Image en mémoire (le cache JS)
    for (var i = 1; i <= nb_pages; i++) {
        var img = new Image();
        img.src = "/scores/" + track + "/" + scoreInstrument + "_p" + i + ".jpg?t=" + timestamp;
        loadedPages.push(img);
    }

    // Dès que la page 1 est prête, on lance la construction initiale
    if (loadedPages.length > 0) {
        loadedPages[0].onload = function() {
            refreshScore(); 
        };
    }
}


function refreshScore() {
    if (!content || loadedPages.length === 0) return;

    // 1. On recrée la structure de base (vidée par le menu)
    content.innerHTML = '';
    
    var container = document.createElement('div');
    container.id = "score-container";
    container.style.width = "100%";
    container.style.height = "100%";
    container.style.position = "relative";
    container.style.overflow = "hidden";
    
    container.onclick = function(e) {
        var fullWidth = this.clientWidth;
        var clickX = e.pageX - this.offsetLeft;
        if (clickX < fullWidth / 2) {
            prevPage();
        } else {
            nextPage();
        }
    };

    content.appendChild(container);

    // 2. Calcul du nombre de pages affichables
    nbShowedPages = countDisplayablePages(container, loadedPages[0]);

    // 3. Lancement du rendu visuel
    renderScore();
}

function renderScore() {
    var container = document.getElementById('score-container');
    if (!container || loadedPages.length === 0) return;

    // 1. Nettoyage du conteneur multipurpose
    container.innerHTML = '';
    
    // On force le style pour l'alignement horizontal
    container.style.textAlign = "left"; // Les pages s'alignent à gauche
    container.style.whiteSpace = "nowrap";
    container.style.display = "block";

    var viewW = content.clientWidth;
    var viewH = content.clientHeight;
    var availableW = viewW / nbShowedPages;

    // 2. Boucle de rendu basée sur nbShowedPages
    for (var i = 0; i < nbShowedPages; i++) {
        var imgIndex = currentPage + i;
        
        if (loadedPages[imgIndex]) {
            // --- AFFICHAGE D'UNE PAGE RÉELLE ---
            var img = document.createElement('img');
            img.src = loadedPages[imgIndex].src;
            img.className = "score-page";
            
            // Style pour alignement côte à côte
            img.style.display = "inline-block";
            img.style.verticalAlign = "top";

            img.onload = function() {
                var ratioW = availableW / this.naturalWidth;
                var ratioH = viewH / this.naturalHeight;
                var scale = Math.min(ratioW, ratioH);

                var finalW = Math.floor(this.naturalWidth * scale);
                var finalH = Math.floor(this.naturalHeight * scale);

                this.style.width = finalW + "px";
                this.style.height = finalH + "px";
                
                // Centrage vertical de l'image
                this.style.marginTop = Math.max(0, Math.floor((viewH - finalH) / 2)) + "px";
                
                // Centrage horizontal dans sa propre colonne (optionnel)
                var paddingL = Math.max(0, Math.floor((availableW - finalW) / 2));
                this.style.marginLeft = paddingL + "px";
                this.style.marginRight = paddingL + "px";
            };

            container.appendChild(img);
        } else {
            // --- CAS D'UNE PAGE VIDE (BUTÉE) ---
            // On insère un bloc invisible pour garder la structure
            var spacer = document.createElement('div');
            spacer.style.display = "inline-block";
            spacer.style.width = Math.floor(availableW) + "px";
            spacer.style.height = "1px";
            container.appendChild(spacer);
        }
    }

    // 3. Reset du scroll pour les vieilles tablettes
    content.scrollTop = 0;
}

function countDisplayablePages(container, first_page_img) {
    if (!first_page_img || !container) return 1;

    var viewW = container.clientWidth;
    var viewH = container.clientHeight;

    // 1. On calcule d'abord l'échelle nécessaire pour que la page tienne en hauteur
    // C'est la contrainte principale pour une partition
    var scaleH = viewH / first_page_img.naturalHeight;
    
    // 2. On calcule la largeur que prendra cette page une fois mise à l'échelle
    var scaledWidth = first_page_img.naturalWidth * scaleH;

    // Sécurité anti-NaN ou division par zéro
    if (!scaledWidth || scaledWidth === 0) return 1;

    // 3. On regarde combien de fois cette largeur rentre dans le container
    // On utilise floor pour ne pas déborder
    var count = Math.floor(viewW / scaledWidth);

    // On retourne au moins 1, et on ne dépasse pas le nombre total de pages
    return Math.max(1, Math.min(count, scoreNbPages));
}

function resizeScorePages() {
    // 1. On doit récupérer l'élément pour savoir quelle largeur il fait maintenant
    var container = document.getElementById('score-container');
    
    // 2. On vérifie que tout est prêt avant de calculer
    if (container && loadedPages && loadedPages[0]) {
        
        // On recalcule le nombre de pages (1, 2 ou 3...)
        nbShowedPages = countDisplayablePages(container, loadedPages[0]);
        
        // Test anti incohérence du numéro de page
        if (currentPage + nbShowedPages > loadedPages.length) {
            currentPage = Math.max(0, loadedPages.length - nbShowedPages);
        }
        
        // On relance l'affichage
        renderScore();
    }
}

function nextPage() {
    // La dernière page affichée à l'écran est : currentPage + nbShowedPages
    // Mais attention, les index commencent à 0, donc la dernière page physique est loadedPages.length
    
    if (currentPage + nbShowedPages < loadedPages.length) {
        currentPage++;
        renderScore();
    } else {
        //~ console.log("Butée de fin atteinte");
    }
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderScore();
    }
}

