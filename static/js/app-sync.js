var DATA_TRACKS = null;
var DATA_UI_POPULAR = null;
var DATA_UI_CLASSY = null;
var TOTAL_PAGES = 1;
var IS_RENDERING = false; 

var syncInterval = null;

function startSync() {
    if (syncInterval) return; // Déjà lancé
    console.log("Synchro activée");
    syncInterval = setInterval(function() {
        if (DATA_TRACKS && DATA_TRACKS.length > 0) {
            checkSync();
        }
    }, 2000);
}

function stopSync() {
    if (syncInterval) {
        console.log("Synchro désactivée");
        clearInterval(syncInterval);
        syncInterval = null;
    }
}/**
 * CHARGEMENT DES JSON
 */
function fetchData() {
    var loaded = 0;
    function checkReady() {
        loaded++;
        if (loaded === 3) waitForDependencies();
    }
    // Utilisation de getJSON classique (compatible obsolète)
    getJSON('/server_data/db_tracks.json', function(d) { DATA_TRACKS = d; checkReady(); });
    getJSON('/server_data/ui_popular.json', function(d) { DATA_UI_POPULAR = d; checkReady(); });
    getJSON('/server_data/ui_classy.json', function(d) { DATA_UI_CLASSY = d; checkReady(); });
}

function getJSON(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onreadystatechange = function() { 
        if (xhr.readyState === 4 && xhr.status === 200) { callback(JSON.parse(xhr.responseText)); } 
    };
    xhr.send();
}

/**
 * ATTENTE DES DÉPENDANCES
 */
function waitForDependencies() {
    // Si openScore n'est pas encore là, on boucle
    if (typeof openScore !== 'function') {
        setTimeout(waitForDependencies, 100);
        return;
    }
    
    // RETOUR DE L'OBSOLÈTE : On initialise l'instrument AVANT checkSync
    window.SELECTED_INSTRUMENT = localStorage.getItem("selected_inst") || "";
    
    // On lance la synchro systématiquement au démarrage
    checkSync(true);
}

/**
 * SYNCHRONISATION
 */
function checkSync(force) {
    if (!DATA_TRACKS || IS_RENDERING) return; 

    var inst = localStorage.getItem("selected_inst") || "";
    var mode = localStorage.getItem("selected_mode") || "POPULAR";
    
    var params = "instrument=" + encodeURIComponent(inst) + "&mode=" + encodeURIComponent(mode) +
                 "&easy=" + (localStorage.getItem("is_easy") || "false") +
                 "&solo=" + (localStorage.getItem("is_solo") || "false") +
                 "&voice=" + (localStorage.getItem("current_voice") || "1");

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/sync_check?' + params, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = xhr.responseText.trim();
            if (!response || response === "None" || response.indexOf('|') === -1) return; 
            
            var parts = response.split('|');
            var loc = parts[0]; 

            if (force === true || loc !== localStorage.getItem("last_track_loc")) {
                IS_RENDERING = true; 
                localStorage.setItem("last_track_loc", loc);
                window.LAST_LOCATION = loc;

                var trackObj = null;
                for (var i = 0; i < DATA_TRACKS.length; i++) {
                    if (DATA_TRACKS[i].location === loc) { 
                        trackObj = DATA_TRACKS[i]; 
                        var pathParts = loc.split('/');
                        pathParts.pop(); 
                        localStorage.setItem("last_track_path", pathParts.join('/'));
                        break; 
                    }
                }

                if (trackObj && typeof openScore === "function") {
                    setTimeout(function() {
                        try {
                            openScore(trackObj, true);
                        } catch(e) { 
                            console.error("Erreur rendu:", e);
                            IS_RENDERING = false; 
                        }
                    }, 200);
                } else {
                    IS_RENDERING = false;
                }
            }
        }
    };
    xhr.send();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fetchData);
} else {
    fetchData();
}

function onInstrumentChanged() { checkSync(true); }