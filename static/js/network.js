
var POOLING_TIMEOUT_MSEC = 2000; // supposed to be a constant
var POOLING_VALUE = 2000; // supposed to be a constant
var poolingId = null ;// fonction retardée

function poolServer() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/sync_check?t=" + new Date().getTime(), true);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                track_location.set(xhr.responseText);
                checkUpdateScore();
            }
            // On ne relance le prochain check que 2s APRES la fin de celui-ci
            if (poolingId) { // Si on n'a pas fait stopPooling entre temps
                poolingId = setTimeout(poolServer, POOLING_VALUE);
            }
        }
    };
    //~ console.log("pool! 🎯");
    xhr.send();
}

function startPooling() {
    if (poolingId) return;
    // On simule un ID pour dire que c'est actif
    poolingId = true; 
    poolServer();
    //~ console.log("pooling démarré");
}

function stopPooling() {
    clearTimeout(poolingId);
    poolingId = null;
    //~ console.log("pooling stoppé");
}

function updateServerTrack(newLocation) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_track", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            //~ console.log("morceau sélectionné:",newLocation);
        }
    };

    // On envoie la donnée sous forme de petit objet JSON
    var data = JSON.stringify({ location: newLocation });
    xhr.send(data);
}

function getScoreNameNbPages() {
    var loc = track_location.get();
    var instrument = current_instrument.get();
    var voice = voice_num.get();
    var mode = instru_select_mode.get();
    var solo = solo_toggle.get();
    var easy = easy_toggle.get();
    
    var htmlContent = "";

    // Fonction utilitaire pour formater la ligne (compatible vieux JS)
    //~ function formatLine(label, value) {
        //~ var type = typeof value;
        //~ return "<b>" + label + " :</b> " + value + " <i>(" + type + ")</i><br>";
    //~ }
    //~ htmlContent += formatLine("Dossier", loc);
    //~ htmlContent += formatLine("Instrument", inst);
    //~ htmlContent += formatLine("Voix", voice);
    //~ htmlContent += formatLine("Mode", mode);
    //~ htmlContent += formatLine("Solo", solo);
    //~ htmlContent += formatLine("Facile", easy);
    //~ content.innerHTML = htmlContent;

    var infoUrl = "/get_score_info" + "?loc=" + encodeURIComponent(loc) +
        "&instrument=" + encodeURIComponent(instrument) +
        "&voice=" + encodeURIComponent(voice) +
        "&mode=" + encodeURIComponent(mode) +
        "&solo=" + encodeURIComponent(solo) +
        "&easy=" + encodeURIComponent(easy);

    var xhr = new XMLHttpRequest();
    xhr.open("GET", infoUrl, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var info = JSON.parse(xhr.responseText);
            if(info.status == "error"){
                console.log("error message:", info.message);
                if (typeof getScore === "function") {
                    getScore(null, 0); 
                }
                showModal("Attention", info.message);
            }
            else
                //~ console.log("score:", info.score, "nb_pages:", info.nb_pages);
                // Vérification de sécurité avant l'appel
            if (typeof getScore === "function") {
                getScore(info.score, info.nb_pages);
            } else {
                console.error("ERREUR : score.js n'est pas encore chargé ou getScore est introuvable");
            }
        }
    };
    xhr.send();
}

function getAvailableInstruments() {
    var url = '/get_available_instruments';
    console.log('get_available_instruments');
    // On utilise ta fonction getJSON (en espérant qu'elle soit compatible)
    getJSON(url, function(instruments) {
        console.log(JSON.stringify(instruments, null, 2));
    });
}
