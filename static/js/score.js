/* ici on affiche les images jpg copies des pages pdf */

var loadedPages = [];
var scoreInstrument = null;
var scoreNbPages = null;
var currentPage = 0;
var nbShowedPages = 0;
var loadedTrackPath = null;  // Le dossier actuel
var loadedInstrumentName = null; // L'instrument actuel

// Variables globales de référence pour stocker les dimensions de la partition
var refNaturalWidth = 0;
var refNaturalHeight = 0;

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
    refNaturalWidth = 0;
    refNaturalHeight = 0;
    
    var timestamp = new Date().getTime();

    // On précharge les objets Image en mémoire (le cache JS)
    for (var i = 1; i <= nb_pages; i++) {
        var img = new Image();
        img.src = "/scores/" + track + "/" + scoreInstrument + "_p" + i + ".jpg?t=" + timestamp;
        loadedPages.push(img);
    }

    // Dès que la page 1 est prête, on capture ses dimensions réelles et on lance l'affichage
    if (loadedPages.length > 0) {
        loadedPages[0].onload = function() {
            refNaturalWidth = this.naturalWidth;
            refNaturalHeight = this.naturalHeight;
            refreshScore(); 
        };
        
        // Sécurité si l'image était déjà instantanément en cache et que onload ne déclenche pas
        if (loadedPages[0].complete && loadedPages[0].naturalWidth > 0) {
            refNaturalWidth = loadedPages[0].naturalWidth;
            refNaturalHeight = loadedPages[0].naturalHeight;
            refreshScore();
        }
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

    // 2. Calcul du nombre de pages affichables (basé sur nos dimensions de référence)
    var fakeImgRef = { naturalWidth: refNaturalWidth, naturalHeight: refNaturalHeight };
    nbShowedPages = countDisplayablePages(container, fakeImgRef);

    // 3. Lancement du rendu visuel
    renderScore();
}

function renderScore() {
    var container = document.getElementById('score-container');
    if (!container || loadedPages.length === 0) return;

    // 1. Nettoyage du conteneur multipurpose
    container.innerHTML = '';
    
    // On force le style pour l'alignement horizontal et le CENTRAGE global du bloc
    container.style.textAlign = "center"; // Modifié : centre le groupe de pages dans l'écran
    container.style.whiteSpace = "nowrap";
    container.style.display = "block";

    var viewW = content.clientWidth;
    var viewH = content.clientHeight;

    // Protection au cas où les dimensions n'auraient pas été lues correctement
    var natW = refNaturalWidth > 0 ? refNaturalWidth : 800;
    var natH = refNaturalHeight > 0 ? refNaturalHeight : 1130;

    // Définition de l'espace humain entre les pages (passé à 4 pixels)
    var pageGap = 4;

    // Calcul de la largeur disponible réelle en retirant les espaces entre les pages
    var totalGaps = (nbShowedPages - 1) * pageGap;
    var availableW = (viewW - totalGaps) / nbShowedPages;

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

            // Calcul basé sur les dimensions de référence garanties de la page 1
            var ratioW = availableW / natW;
            var ratioH = viewH / natH;
            var scale = Math.min(ratioW, ratioH);

            var finalW = Math.floor(natW * scale);
            var finalH = Math.floor(natH * scale);

            img.style.width = finalW + "px";
            img.style.height = finalH + "px";
            
            // Centrage vertical de l'image
            img.style.marginTop = Math.max(0, Math.floor((viewH - finalH) / 2)) + "px";
            
            // GESTION CORRIGÉE DE L'ESPACE : Espace fixe de 4px entre les pages
            img.style.marginLeft = "0px";
            if (i > 0) {
                img.style.marginRight = "0px";
                img.style.marginLeft = pageGap + "px"; // N'ajoute l'espace qu'entre deux pages
            } else {
                img.style.marginRight = "0px";
            }

            container.appendChild(img);
        } else {
            // --- CAS D'UNE PAGE VIDE (BUTÉE) ---
            var spacer = document.createElement('div');
            spacer.style.display = "inline-block";
            spacer.style.width = Math.floor(availableW) + "px";
            spacer.style.height = "1px";
            if (i > 0) {
                spacer.style.marginLeft = pageGap + "px";
            }
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

    var natH = first_page_img.naturalHeight > 0 ? first_page_img.naturalHeight : 1130;
    var natW = first_page_img.naturalWidth > 0 ? first_page_img.naturalWidth : 800;

    // 1. On calcule d'abord l'échelle nécessaire pour que la page tienne en hauteur
    var scaleH = viewH / natH;
    
    // 2. On calcule la largeur que prendra cette page une fois mise à l'échelle
    var scaledWidth = natW * scaleH;

    if (!scaledWidth || scaledWidth === 0) return 1;

    // 3. Prise en compte de l'espace de 4px entre les pages dans l'estimation
    var pageGap = 4;
    // La formule pour savoir combien de pages + leurs espaces rentrent :
    var count = Math.floor((viewW + pageGap) / (scaledWidth + pageGap));

    return Math.max(1, Math.min(count, scoreNbPages));
}

function resizeScorePages() {
    var container = document.getElementById('score-container');
    
    if (container && loadedPages && loadedPages[0]) {
        var fakeImgRef = { naturalWidth: refNaturalWidth, naturalHeight: refNaturalHeight };
        nbShowedPages = countDisplayablePages(container, fakeImgRef);
        
        if (currentPage + nbShowedPages > loadedPages.length) {
            currentPage = Math.max(0, loadedPages.length - nbShowedPages);
        }
        
        renderScore();
    }
}

function nextPage() {
    if (currentPage + nbShowedPages < loadedPages.length) {
        currentPage++;
        renderScore();
    }
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderScore();
    }
}