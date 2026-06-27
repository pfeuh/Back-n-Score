
function openScore(item, isSilent) {   
    if (!item) return;

    // Utilisation stricte de la location comme identifiant unique
    localStorage.setItem("last_track_loc", item.location);
    LAST_LOCATION = item.location;
    
    if (!SELECTED_INSTRUMENT) return; 
    
    navDiv.style.display = "none"; 
    document.body.className = "";
    contentDiv.innerHTML = "<div id='score-display'></div>";
    
    // Transmission au serveur (identique pour PC et tablettes)
    if (!isSilent) {
        var xhrSync = new XMLHttpRequest();
        xhrSync.open('POST', '/sync_push', true);
        xhrSync.setRequestHeader('Content-Type', 'application/json');
        xhrSync.send(JSON.stringify({ location: item.location }));
    }
    
    if (typeof startSync === "function") startSync(); // On relance le polling
    
    renderV1(item.location, TOTAL_PAGES);
}

// Dans app-viewer.js - On sécurise le rendu
function renderPDFPage(pageNum) {
    if (!PDF_DOC || IS_RENDERING) return; 
    
    PDF_DOC.getPage(pageNum).then(function(page) {
        var canvas = document.getElementById('pdf-canvas');
        if (!canvas) return;
        
        var ctx = canvas.getContext('2d');
        var unscaled = page.getViewport({ scale: 1 });
        
        // STABILISATION DE L'ÉCHELLE
        // On vérifie que la fenêtre a une dimension réelle
        var width = window.innerWidth > 0 ? window.innerWidth : screen.width;
        var height = window.innerHeight > 0 ? window.innerHeight : screen.height;
        
        var ratio = Math.min(width / unscaled.width, height / unscaled.height);
        
        // On multiplie par 2 pour la netteté, mais on bride le canvas en CSS
        var vp = page.getViewport({ scale: ratio * 2 }); 
        
        canvas.width = vp.width; 
        canvas.height = vp.height;
        canvas.style.width = "100%"; // Force l'occupation de l'espace
        canvas.style.height = "auto";

        page.render({ canvasContext: ctx, viewport: vp }).promise.then(function() {
            // On ne déverrouille QUE quand le dessin est fini
            IS_RENDERING = false; 
        });
    });
}

function changePage(delta) {
    var next = CURRENT_PAGE + delta;
    if (next >= 1 && next <= TOTAL_PAGES) {
        CURRENT_PAGE = next;
        if (isObsolete()) { updateImageLegacy(); } 
        else { renderPDFPage(CURRENT_PAGE); }
        contentDiv.scrollTop = 0;
    }
}

function renderV1(location, nbPages) {
    var display = document.getElementById("score-display");
    if(!display) return;
    display.innerHTML = "";
    CURRENT_PAGE = 1;
    // On ne touche pas à TOTAL_PAGES ici, le moteur de rendu le fera

    var overlay = document.createElement("div");
    overlay.id = "nav-overlay";
    overlay.innerHTML = '<div class="click-zone" id="zone-left" onclick="changePage(-1)"></div>' +
                        '<div class="click-zone" id="zone-right" onclick="changePage(1)"></div>';
    display.appendChild(overlay);

    var query = "location=" + encodeURIComponent(location) + 
                "&inst=" + encodeURIComponent(SELECTED_INSTRUMENT) + 
                "&voice=" + CURRENT_VOICE + 
                "&solo=" + IS_SOLO + 
                "&easy=" + IS_EASY +
                "&mode=" + (CURRENT_MODE === "POPULAR" ? "POPULAR" : "CLASSY");

    if (isObsolete()) {
        var img = document.createElement("img");
        img.id = "main-img";
        img.className = "score-page active";
        img.style.width = "100%"; img.style.height = "auto";
        display.appendChild(img);
        updateImageLegacy();
    } else {
        var canvas = document.createElement("canvas");
        canvas.id = "pdf-canvas";
        canvas.className = "score-page active";
        display.appendChild(canvas);
        
        pdfjsLib.getDocument("/get_score?" + query).promise.then(function(doc) {
            PDF_DOC = doc;
            TOTAL_PAGES = doc.numPages; // La vérité est dans le PDF
            renderPDFPage(1);
        }).catch(function(err) {
            console.error("Erreur PDF:", err);
            IS_RENDERING = false;
        });
    }
}

function updateImageLegacy() {
    var img = document.getElementById('main-img');
    if (!img) return;

    img.onerror = function() {
        if (CURRENT_PAGE > 1) {
            TOTAL_PAGES = CURRENT_PAGE - 1;
            CURRENT_PAGE = TOTAL_PAGES;
            updateImageLegacy();
        }
        IS_RENDERING = false;
        img.onerror = null;
    };

    var query = "location=" + encodeURIComponent(LAST_LOCATION) + 
                "&inst=" + encodeURIComponent(SELECTED_INSTRUMENT) + 
                "&page=" + CURRENT_PAGE;
    img.src = "/get_score?" + query + "&t=" + new Date().getTime();
    img.onload = function() { IS_RENDERING = false; };
}

function renderPDFPage(pageNum) {
    if (!PDF_DOC) return;
    PDF_DOC.getPage(pageNum).then(function(page) {
        var canvas = document.getElementById('pdf-canvas');
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        var unscaled = page.getViewport({ scale: 1 });
        
        // Stabilisation ratio
        var w = window.innerWidth > 0 ? window.innerWidth : screen.width;
        var h = window.innerHeight > 0 ? window.innerHeight : screen.height;
        var ratio = Math.min(w / unscaled.width, h / unscaled.height);
        
        var vp = page.getViewport({ scale: ratio * 2 }); 
        canvas.width = vp.width; canvas.height = vp.height;
        
        page.render({ canvasContext: ctx, viewport: vp }).promise.then(function() {
            IS_RENDERING = false; // Déverrouillage après dessin
        });
    });
}

