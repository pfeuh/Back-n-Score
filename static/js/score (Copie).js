
/* ici on affiche les images jpg copies des pages pdf */

var loadedPages = [];
var scoreInstrument = null;
var scoreNbPages = null;
var currentPage = 0;

function getScore(instrument, nb_pages) {
    scoreInstrument = instrument;
    scoreNbPages = nb_pages;

    if (!content) return;

    // On vide content comme d'habitude
    content.innerHTML = '';
    loadedPages = [];
    currentPage = 0;

    var track = track_location.get();
    var timestamp = new Date().getTime();

    // --- CRÉATION DU CALQUE DÉDIÉ ---
    var container = document.createElement('div');
    container.id = "score-container";
    // On lui donne toute la place disponible dans content
    container.style.width = "100%";
    container.style.height = "100%";
    container.style.position = "relative";
    container.style.overflow = "hidden";
    
    // C'est LUI qui gère le clic, et uniquement lui
    container.onclick = function(e) {
        var fullWidth = this.clientWidth;
        var clickX = e.pageX - this.offsetLeft;

        if (clickX < fullWidth / 2) {
            if (currentPage > 0) prevPage();
        } else {
            if (currentPage < loadedPages.length - 1) nextPage();
        }
    };

    content.appendChild(container);

    // Préchargement
    for (var i = 1; i <= nb_pages; i++) {
        var img = new Image();
        img.src = "/scores/" + track + "/" + scoreInstrument + "_p" + i + ".jpg?t=" + timestamp;
        loadedPages.push(img);
    }

    console.log("on peut afficher",countDisplayablePages(container, loadedPages[0]), "page(s)");
    
    // Création de l'image dans NOTRE container
    var view = document.createElement('img');
    view.id = "score-view";
    view.className = "score-page";
    container.appendChild(view);

    renderPage();
}

function xx_renderPage() {
    var container = document.getElementById('score-container');
    var view = document.getElementById('score-view');
    if (!container || !view || !loadedPages[currentPage]) return;

    view.src = loadedPages[currentPage].src;

    view.onload = function() {
        var viewW = container.clientWidth;
        var viewH = container.clientHeight;
        
        var ratioW = viewW / this.naturalWidth;
        var ratioH = viewH / this.naturalHeight;
        var scale = Math.min(ratioW, ratioH);

        var finalW = Math.floor(this.naturalWidth * scale);
        var finalH = Math.floor(this.naturalHeight * scale);

        this.style.width = finalW + "px";
        this.style.height = finalH + "px";
        this.style.marginTop = Math.max(0, Math.floor((viewH - finalH) / 2)) + "px";
    };
}

function renderPage() {
    var view = document.getElementById('score-view');
    if (!view || !loadedPages[currentPage]) return;

    view.src = loadedPages[currentPage].src;

    view.onload = function() {
        // 1. Espace disponible (on retire la barre de menu)
        var viewW = content.clientWidth;
        var viewH = content.clientHeight;
        
        // 2. Calcul du ratio
        var ratioW = viewW / this.naturalWidth;
        var ratioH = viewH / this.naturalHeight;
        
        // 3. On choisit le ratio le plus restrictif
        // Sur PC, ce sera ratioH (la hauteur), sur Tablette, ratioW (la largeur)
        var scale = Math.min(ratioW, ratioH);

        var finalW = Math.floor(this.naturalWidth * scale);
        var finalH = Math.floor(this.naturalHeight * scale);

        // 4. On applique les dimensions exactes
        this.style.width = finalW + "px";
        this.style.height = finalH + "px";
        
        // 5. Centrage vertical pour le PC
        // On calcule l'espace vide restant en hauteur et on divise par 2
        var marginT = Math.max(0, Math.floor((viewH - finalH) / 2));
        this.style.marginTop = marginT + "px";

        // 6. Reset du scroll
        content.scrollTop = 0;
    };

    // Préchargeur (pour le delay des vieilles tablettes)
    if (loadedPages[currentPage + 1]) {
        var preloader = new Image();
        preloader.src = loadedPages[currentPage + 1].src;
    }
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
    renderPage();
}

function nextPage() {
    if (currentPage < loadedPages.length - 1) {
        currentPage++;
        renderPage();
    }
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderPage();
    }
}

/* --- GESTION DES PÉDALES ET CLAVIER (PAGE UP/DOWN) --- */
window.onkeydown = function(e) {
    // On ne fait rien si le conteneur de partition n'est pas là
    var container = document.getElementById('score-container');
    if (!container) return;

    var key = e.keyCode || e.which;

    // Précédent : Flèche Gauche (37) ou Page Up (33)
    if (key == 37 || key == 33) {
        if (currentPage > 0) {
            prevPage();
        }
    } 
    // Suivant : Flèche Droite (39), Page Down (34) ou Espace (32)
    else if (key == 39 || key == 34 || key == 32) {
        if (currentPage < loadedPages.length - 1) {
            nextPage();
        }
    }
};