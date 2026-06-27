// *************************************************
// *** On essaie de rester compatible Android 4, ***
// *** vu le nombre de vieilles tablettes qui    ***
// *** trainent un peu partout...                ***
// *************************************************

// Au début du fichier
//var content = null; 

function initGlobalElements() {
    content = document.getElementById('content');
    if (!content) {
        console.error("FATAL : L'élément #content n'existe pas dans le HTML");
    }
}function sendPlayerCMD(cmd){
    // --- AJOUT : Mise à jour visuelle des locators ---
    // Remplacement de .includes par .indexOf pour compatibilité
    if (cmd.indexOf('goto_') !== -1 || cmd.indexOf('set_') !== -1) {
        setLocatorActive(cmd);
    } else if (cmd === 'stop' || cmd === 'rewind') {
        initPlayerUI(); // On reset si on stop ou revient au début
    }
    // ------------------------------------------------

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/audio_command", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            //~ console.log(cmd, "envoyé");
        }
    };
    xhr.send(cmd);
}

function handleKeyboard(event){
    // On bloque les touches de navigation système pour garder le focus
    // Remplacement de const par var
    var keysToBlock = [' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'PageUp', 'PageDown'];
    
    if (keysToBlock.indexOf(event.key) !== -1) {
        event.preventDefault();
        event.stopPropagation();
    }

    switch(event.key){
        case ' ':
            sendPlayerCMD('play');
            break;
        case 'a': case 'b': case 'c': case 'd':
            sendPlayerCMD('goto_' + event.key);
            break;
        case 'A': case 'B': case 'C': case 'D':
            sendPlayerCMD('set_' + event.key.toLowerCase());
            break;
        case 'i': case 'I':
            if (typeof getAvailableInstruments === "function") getAvailableInstruments();
            break;
        case 'ArrowLeft':  sendPlayerCMD('rewind'); break;
        case 'ArrowRight': sendPlayerCMD('ff'); break;
        case 'Home':       sendPlayerCMD('goto_start'); break;
        case 'PageDown':
        case 'ArrowRight':
            if (typeof nextPage === "function") nextPage();
            break;
        case 'PageUp':
        case 'ArrowLeft':
            if (typeof prevPage === "function") prevPage();
            break;
    }
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
        isDataLoaded = true;
        initMenu(); 
        
        var pendingLoc = track_location.get();
        if (pendingLoc) {
            updateTreeCursor(pendingLoc);
        }
    });
}

function formatNodeName(name) {
    // Correction de startsWith par indexOf
    var cleanName = name.indexOf('_') === 0 ? name.substring(1) : name;
    var formatted = cleanName.replace(/([A-Z])/g, " $1");
    return formatted.charAt(0).toUpperCase() + formatted.slice(1).trim();
} // <-- Accolade manquante rajoutée ici

function buildTreeStructure(flatData) {
    var root = {};
    for (var i = 0; i < flatData.length; i++) {
        var track = flatData[i];
        var parts = track.location.split('/');
        var currentNode = root;

        for (var j = 0; j < parts.length; j++) {
            var part = parts[j];
            if (!currentNode[part]) {
                currentNode[part] = (j === parts.length - 1) ? track : {};
            }
            currentNode = currentNode[part];
        }
    }
    return root;
}

function renderTree(node, container) {
    var ul = document.createElement('ul');
    ul.className = 'tree-list';

    for (var key in node) {
        var li = document.createElement('li');
        var content = node[key];

        if (content.title) {
            li.className = 'song-item';
            li.setAttribute('data-loc', content.location);
            // Plus de backticks !
            li.innerHTML = '📄 ' + content.title;
            
            li.onclick = (function(loc) {
                return function(e) {
                    if(e && e.stopPropagation) e.stopPropagation();
                    sendNewTrackLocation(loc);
                };
            })(content.location);
        } else {
            var folderName = formatNodeName(key);
            var folderSpan = document.createElement('span');
            folderSpan.className = 'folder';
            folderSpan.innerHTML = '📁 ' + folderName;
            li.appendChild(folderSpan);
            
            folderSpan.onclick = function(e) {
                if(e && e.stopPropagation) e.stopPropagation();
                var parent = this.parentNode;
                if (parent.className.indexOf('open') !== -1) {
                    parent.className = parent.className.replace('open', '');
                } else {
                    parent.className += ' open';
                }
            };
            renderTree(content, li);
        }
        ul.appendChild(li);
    }
    container.appendChild(ul);
}

function updateTreeCursor(activeLocation) {
    if (!isDataLoaded) return;
    
    // Remplacement de allOpenNodes.forEach par boucle for
    var allOpenNodes = document.querySelectorAll('.tree-list li.open');
    for (var i = 0; i < allOpenNodes.length; i++) {
        allOpenNodes[i].classList.remove('open');
    }

    var oldActive = document.querySelector('.song-item.active');
    if (oldActive) oldActive.classList.remove('active');

    // Plus de backticks ici non plus
    var newActive = document.querySelector('.song-item[data-loc="' + activeLocation + '"]');
    
    if (newActive) {
        newActive.classList.add('active');

        var parent = newActive.parentElement;
        while (parent && parent !== document.body) {
            if (parent.tagName === 'LI') {
                parent.classList.add('open');
            }
            parent = parent.parentElement;
        }

        // On enlève le "smooth" qui fait souvent planter Android 4
        newActive.scrollIntoView();
    }
}

function showModal(title, msg){
    console.log(title, msg);
}

function initPlayerUI() {
    var letters = ['A', 'B', 'C', 'D'];
    var buttons = document.querySelectorAll('#transport-bar .btn');
    for (var i = 0; i < buttons.length; i++) {
        var btn = buttons[i];
        var text = btn.innerText || btn.textContent;
        if (letters.indexOf(text.trim()) !== -1) {
            btn.style.backgroundColor = ""; 
            btn.style.color = "";
        }
    }
}

function setLocatorActive(locator_name) {
    if (locator_name.indexOf('set_') !== 0) return;

    var parts = locator_name.split('_');
    var letter = parts[parts.length - 1].toUpperCase();
    var buttons = document.querySelectorAll('#transport-bar .btn');
    
    for (var i = 0; i < buttons.length; i++) {
        var btn = buttons[i];
        var text = btn.innerText || btn.textContent;
        if (text.trim() === letter) {
            btn.style.backgroundColor = "#2ecc71"; 
            btn.style.color = "white";
        }
    }
}

function initMenu() {
    var treeContainer = document.getElementById('tree');
    if (!DATA_TRACKS || !treeContainer) return;
    treeContainer.innerHTML = '<h3 class="header">Library</h3>';
    var treeData = buildTreeStructure(DATA_TRACKS);
    renderTree(treeData, treeContainer);
}

function sendNewTrackLocation(loc) {
    if (typeof updateServerTrack === "function") updateServerTrack(loc);
    updateTreeCursor(loc);
}

// Variables Globales
var DATA_TRACKS = null;
var MODE_POPULAR = 1;
var MODE_CLASSIQUE = 2;
var isDataLoaded = false;
var old_track_location = null;

// Initialisation des propriétés (en supposant que createProp existe ailleurs)
var track_location = createProp({ 
    key: 'bn_track_loc', 
    default: null 
});

// Hack pour lier track_location à l'UI (plus de const)
var originalSet = track_location.set;
track_location.set = function(val) {
    if (val && val !== this.get()) {
        updateTreeCursor(val);
    }
    originalSet.call(track_location, val);
};

window.onload = function() {
    initGlobalElements(); // On récupère les éléments DOM ici
    fetchData();
    
    if (window.addEventListener) {
        window.addEventListener('keydown', handleKeyboard, true); 
    } else if (window.attachEvent) {
        window.attachEvent('onkeydown', handleKeyboard);
    }
    
    if (typeof resizeScorePages === "function") window.onresize = resizeScorePages;
    if (typeof startPooling === "function") startPooling();
};