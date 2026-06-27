// ---********************---
// ---*** Variables    ***---
// ---********************---

var DATA_TRACKS = null;               // supposed to be a constant
var DATA_UI_POPULAR = null;           // supposed to be a constant
var DATA_UI_CLASSIQUE = null;         // supposed to be a constant
var MODE_POPULAR = 1;                 // supposed to be a constant
var MODE_CLASSIQUE = 2;               // supposed to be a constant

var content = null;                   // the <div> which receives all trees and scores
var mode_div = null;                   // the <div> which receives all trees and scores

// --- Variables synchronisées (via objects.js) ---

var track_location = createProp({ 
    // l'emplacement du dossier track sur le serveur
    key: 'bn_track_loc', 
    default: null 
});
var old_track_location = null; // track change detector. null pour charger immédiatement

var current_instrument = createProp({ 
    // l'instrument choisi par le client
    key: 'bn_instru', 
    elId: 'instru-select', 
    isInner: true, 
    default: "DO" 
});
var old_instrument = current_instrument.get(); // instrument change detector.

var easy_toggle = createProp({ 
    // prefix easy
    key: 'bn_easy', 
    elId: 'easy-check', 
    isBool: true, 
    default: 0 
});
var old_easy = easy_toggle.get(); // easy change detector.

var voice_num = createProp({ 
    // numero de voix
    key: 'bn_voice', 
    elId: 'voice-sel', 
    default: "1" 
}); 
var old_voice = voice_num.get(); // voice change detector.

var solo_toggle = createProp({ 
    // suffixe solo
    key: 'bn_solo', 
    elId: 'solo-check', 
    isBool: true, 
    default: 0 
});
var old_solo = solo_toggle.get();// solo change detector.

var instru_select_mode = createProp({ 
    // façon de trier les instruments
    key: 'bn_mode', 
    //~ elId: 'mode-toggle', 
    //~ isInner: true, 
    default: MODE_POPULAR 
}); 
var old_mode = instru_select_mode.get();// mode POP OLDchange detector.

var last_inst_path = createProp({
    // chemin vers l'intrument dans le tree en fonction du mode
    key: 'bn_last_inst_path',
    default: ''
});

// ---********************---
// ---*** Fonctions    ***---
// ---********************---

function getFormattedInstrumentName() {
    // 1. Récupération de la base (ex: "sax_alto")
    var baseInst = current_instrument.get();
    if (!baseInst) return "";

    var result = baseInst;

    // 2. Préfixe "Easy" (si activé, sax_alto -> easysax_alto)
    if (typeof easy_toggle !== "undefined" && easy_toggle.get() === true) {
        result = "easy" + result;
    }

    // 3. Suffixe "Solo" (si activé, sax_alto -> sax_altosolo)
    if (typeof solo_toggle !== "undefined" && solo_toggle.get() === true) {
        result = result + "solo";
    }

    // 4. Suffixe de Voix (si différent de 1, sax_alto -> sax_alto3)
    var vNum = voice_num.get();
    if (vNum && vNum !== "1" && vNum !== 1) {
        result = result + vNum;
    }

    return result;
}

function callForScore(loc) {
    var instName = getFormattedInstrumentName();
    var mode = instru_select_mode.get();
    
    if (typeof ScoreViewer !== "undefined") {
        //~ console.log("demande de",location, instName, mode);
        // On passe tout au viewer, qui se chargera de la requête AJAX ou de l'IMG
        ScoreViewer.open(location, instName, mode, 1);
    }
}

function isObsolete(){
    return /Android [4-6]\./.test(navigator.userAgent);
}

function getJSON(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onreadystatechange = function() { 
        if (xhr.readyState === 4 && xhr.status === 200) { 
            callback(JSON.parse(xhr.responseText)); 
        } 
    };
    xhr.send();
}

function fetchData() {
    getJSON('/server_data/db_tracks.json', function(d1) {
        DATA_TRACKS = d1;
        
        getJSON('/server_data/ui_popular.json', function(d2) {
            DATA_UI_POPULAR = d2;
            
            getJSON('/server_data/ui_classy.json', function(d3) {
                DATA_UI_CLASSIQUE = d3;
                
                //~ console.log("Tout est prêt");
                startApp();
            });
        });
    });
}


function setEasy(checked) {
    easy_toggle.set(checked);
}

function setVoice(val) {
    voice_num.set(val);
}

function setSolo(checked) {
    solo_toggle.set(checked);
}

function xx_setMode(mode) {
    instru_select_mode.set(mode);
    if(mode == MODE_POPULAR){
        instru_select_mode.set(MODE_POPULAR);
        mode_div.txt = "POP";
    }
    else{
        instru_select_mode.set(MODE_CLASSIQUE);
        mode_div.txt = "OLD";
    }
}

function setMode(modeValue) {
    var current = instru_select_mode.get();
    var newVal;

    // Si on passe une valeur (ex: au chargement), on l'utilise.
    // Sinon (ex: clic), on bascule entre POPULAR et CLASSIQUE.
    if (modeValue !== undefined) {
        newVal = parseInt(modeValue, 10);
    } else {
        newVal = (parseInt(current, 10) === MODE_POPULAR) ? MODE_CLASSIQUE : MODE_POPULAR;
    }

    if (isNaN(newVal)) newVal = MODE_POPULAR;

    // Mise à jour de la propriété synchronisée (gère le Storage et l'UI via innerHTML)
    instru_select_mode.set(newVal);

    // Mise à jour du texte spécifique
    if (mode_div) {
        mode_div.innerHTML = (newVal === MODE_POPULAR) ? "POP" : "OLD";
    }
}

function instrumentChanged() {
    // On compare les valeurs actuelles aux anciennes
    var changed = (old_instrument !== current_instrument.get()) ||
        (old_voice !== voice_num.get()) ||
        (old_easy !== easy_toggle.get()) ||
        (old_solo !== solo_toggle.get()) ||
        (old_mode !== instru_select_mode.get());

    if (changed) {
        //~ console.log("instrument changed:", getFormattedInstrumentName(), mode_div.innerText);
        
        // Mise à jour des "old" pour le prochain tour
        old_instrument = current_instrument.get();
        old_voice      = voice_num.get();
        old_easy       = easy_toggle.get();
        old_solo       = solo_toggle.get();
        old_mode       = instru_select_mode.get();
    }
    
    return changed;
}

function trackChanged(){
    var changed = (old_track_location != track_location.get());
    if(changed){
        //~ console.log("track changed:", track_location.get());
        old_track_location = track_location.get();
    }
    return changed;
}

function checkUpdateScore(){
    var track_changed =  trackChanged();
    var instrument_changed =  instrumentChanged();

    if(track_changed || instrument_changed){
        getScoreNameNbPages(); 
    }
}

function showModal(title, message) {
    var mainContent = document.getElementById('content');
    if (!mainContent) return;

    var html =  '<div class="error-screen">' +
                '  <div class="error-box">' +
                '    <div class="error-title">' + title + '</div>' +
                '    <div class="error-msg">' + message + '</div>' +
                '    <button class="btn-ok" onclick="document.getElementById(\'content\').innerHTML=\'\'">OK</button>' +
                '  </div>' +
                '</div>';
    
    mainContent.innerHTML = html;
}

function devDebug()
{
    instrumentChanged();
}

function startApp() {
    // lancement de la demande cyclique du track actuel pour detecter un nouveau track
    if (typeof startPooling === "function") startPooling();
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

// ---********************---
// ---*** Main Program ***---
// ---********************---

// On attend que la fenêtre soit chargée pour éviter tout conflit
window.onload = function() {
    content = document.getElementById('content');
    mode_div = document.getElementById('mode-toggle');

    // On force une première synchro pour que l'UI affiche les valeurs du localStorage
    easy_toggle.syncUI();
    solo_toggle.syncUI();
    voice_num.syncUI();
    current_instrument.syncUI();
    setMode(instru_select_mode.get());

    // Dans pupitre.js (ton window.onload)
    window.addEventListener('resize', function() {
        setTimeout(function() {
            // On vérifie si la fonction existe avant de l'appeler
            if (typeof resizeScorePages === "function") {
                resizeScorePages();
            }
        }, 200);
    });
    
    fetchData();
};