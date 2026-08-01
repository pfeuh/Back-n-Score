var API_REFRESH_URL = '/api/admin/refresh';
var API_TREE_URL = '/server_data/db_tracks.json';
var API_CONFIG_URL = '/server_data/mp3_types.json'; 
var API_CRUD_URL = '/api/admin/crud';
var API_SAVE_PRIORITIES_URL = '/api/admin/save_mp3_types';

var activeTargetInputId = null;
var foldersOnlyMode = false;
var cachedRawData = null;
var currentPendingSelection = null; 
var loadedPriorityData = null;

function makeRequest(method, url, dataToSend, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var data = null;
                try { data = JSON.parse(xhr.responseText); } catch (e) { data = xhr.responseText; }
                callback(null, data);
            } else {
                callback(new Error("HTTP Error: " + xhr.status), null);
            }
        }
    };
    xhr.send(dataToSend ? JSON.stringify(dataToSend) : null);
}

function loadPriorityTree() {
    var zone = document.getElementById('priority-tree-zone');
    zone.innerHTML = "<p style='color: #888; margin: 0;'>Chargement du fichier mp3_types.json...</p>";
    
    makeRequest('GET', API_CONFIG_URL, null, function(err, data) {
        if (err || !data) {
            zone.innerHTML = "<p style='color: var(--danger-color); margin: 0;'>Impossible de lire mp3_types.json.</p>";
            return;
        }
        loadedPriorityData = data;
        renderPriorityDOM();
        document.getElementById('btn-save-priority').disabled = false;
    });
}

function renderPriorityDOM() {
    var zone = document.getElementById('priority-tree-zone');
    zone.innerHTML = "";
    if (!loadedPriorityData || loadedPriorityData.length === 0) {
        zone.innerHTML = "<p style='color: #666; font-style: italic; margin:0;'>Configuration vide.</p>";
        return;
    }
    zone.appendChild(buildPriorityLevelDOM(loadedPriorityData));
}

function buildPriorityLevelDOM(items) {
    var ul = document.createElement('ul');
    
    var _loop = function(i) {
        var item = items[i];
        var li = document.createElement('li');
        
        var row = document.createElement('div');
        row.className = "priority-row";
        
        var label = document.createElement('span');
        var isObject = (item !== null && typeof item === 'object');
        var itemType = (isObject && item.type === 'folder') ? 'folder' : 'track';
        var itemText = isObject ? (item.title || item.name) : item;
        
        label.className = "priority-label " + (itemType === 'folder' ? 'folder-item' : 'track-item');
        label.innerHTML = (itemType === 'folder' ? '📁 ' : '🎵 ') + itemText;
        row.appendChild(label);
        
        var controls = document.createElement('div');
        controls.className = "arrow-controls";
        
        var upBtn = document.createElement('button');
        upBtn.className = "btn-arrow";
        upBtn.innerHTML = "▲";
        upBtn.onclick = function() { 
            var currentIndex = items.indexOf(item);
            if (currentIndex !== -1) moveItemInArray(items, currentIndex, -1); 
        };
        
        var downBtn = document.createElement('button');
        downBtn.className = "btn-arrow";
        downBtn.innerHTML = "▼";
        downBtn.onclick = function() { 
            var currentIndex = items.indexOf(item);
            if (currentIndex !== -1) moveItemInArray(items, currentIndex, 1); 
        };
        
        controls.appendChild(upBtn);
        controls.appendChild(downBtn);
        row.appendChild(controls);
        li.appendChild(row);
        
        if (isObject && item.type === 'folder' && item.children && item.children.length > 0) {
            li.appendChild(buildPriorityLevelDOM(item.children));
        }
        
        ul.appendChild(li);
    };

    for (var i = 0; i < items.length; i++) {
        _loop(i);
    }
    return ul;
}

function moveItemInArray(array, index, direction) {
    var targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= array.length) return;
    
    var temp = array[index];
    array[index] = array[targetIndex];
    array[targetIndex] = temp;
    
    renderPriorityDOM();
}

function sanitizePriorityData(items) {
    var cleanArray = [];
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item !== null && typeof item === 'object') {
            if (item.type === 'folder') {
                var folderName = item.name || item.title || "";
                var cleanFolder = {
                    type: 'folder',
                    name: folderName,
                    title: folderName,
                    children: item.children ? sanitizePriorityData(item.children) : []
                };
                cleanArray.push(cleanFolder);
            } else {
                var trackName = item.title || item.name || "";
                cleanArray.push(trackName);
            }
        } else if (typeof item === 'string') {
            cleanArray.push(item);
        }
    }
    return cleanArray;
}

function actionSavePriority() {
    if (!loadedPriorityData) return;
    
    var cleanedConfigData = sanitizePriorityData(loadedPriorityData);
    console.log("Données nettoyées prêtes à l'envoi :", cleanedConfigData);
    
    var btnSave = document.getElementById('btn-save-priority');
    btnSave.disabled = true;
    btnSave.innerHTML = "⏳ Envoi...";

    makeRequest('POST', API_SAVE_PRIORITIES_URL, cleanedConfigData, function(err, res) {
        btnSave.disabled = false;
        btnSave.innerHTML = "💾 Sauvegarder l'ordre des priorités";

        if (!err && res && (res.status === "success" || res.success === true)) {
            alert("Succès : L'ordre de priorité global a été enregistré !");
            cachedRawData = null; 
        } else {
            console.error("Détail de l'erreur serveur :", res);
            alert("Erreur lors de l'enregistrement des priorités : " + (res && res.message ? res.message : err));
        }
    });
}

function parseFlatListToTree(flatList) {
    var root = { name: "Root", type: "folder", path: "", children: [] };
    for (var i = 0; i < flatList.length; i++) {
        var item = flatList[i];
        var parts = item.location.split('/');
        var currentLevel = root.children;
        var currentPath = "";

        for (var j = 0; j < parts.length; j++) {
            var partName = parts[j];
            currentPath = currentPath ? currentPath + "/" + partName : partName;
            var isLast = (j === parts.length - 1);
            var found = null;

            for (var k = 0; k < currentLevel.length; k++) {
                if (currentLevel[k].name === partName && currentLevel[k].type === "folder") {
                    found = currentLevel[k];
                    break;
                }
            }

            if (isLast) {
                currentLevel.push({ name: partName, title: item.title, path: item.location, type: "track" });
            } else {
                if (!found) {
                    found = { name: partName, type: "folder", path: currentPath, children: [] };
                    currentLevel.push(found);
                }
                currentLevel = found.children;
            }
        }
    }
    return root.children;
}

function clearVisualSelection() {
    var selectedElements = document.querySelectorAll('.active-selection');
    for (var i = 0; i < selectedElements.length; i++) {
        selectedElements[i].classList.remove('active-selection');
    }
}

function renderTreeDOM(nodes) {
    var ul = document.createElement('ul');
    for (var i = 0; i < nodes.length; i++) {
        var item = nodes[i];
        
        if (item.type === 'folder') {
            var li = document.createElement('li');
            li.className = "folder-branch";
            
            var rowDiv = document.createElement('div');
            rowDiv.className = "tree-row";
            
            var toggleSpan = document.createElement('span');
            toggleSpan.className = "folder-toggle";
            toggleSpan.innerHTML = "▶";
            
            toggleSpan.onclick = (function(targetLi) {
                return function(e) {
                    targetLi.classList.toggle('expanded');
                };
            })(li);

            rowDiv.appendChild(toggleSpan);
            
            var folderSpan = document.createElement('span');
            folderSpan.className = "selectable-path folder-node";
            folderSpan.innerHTML = "📁 " + item.name;
            
            folderSpan.onclick = (function(spanEl, path) {
                return function(e) {
                    clearVisualSelection();
                    spanEl.classList.add('active-selection');
                    currentPendingSelection = path;
                };
            })(folderSpan, item.path);

            rowDiv.appendChild(folderSpan);
            li.appendChild(rowDiv);

            if (item.children && item.children.length > 0) {
                li.appendChild(renderTreeDOM(item.children));
            }
            ul.appendChild(li);
        } else {
            if (!foldersOnlyMode) {
                var li = document.createElement('li');
                
                var rowDiv = document.createElement('div');
                rowDiv.className = "tree-row";
                
                var spacer = document.createElement('span');
                spacer.className = "track-spacer";
                rowDiv.appendChild(spacer);
                
                var trackSpan = document.createElement('span');
                trackSpan.className = "selectable-path track-node";
                trackSpan.innerHTML = "🎵 " + item.title;
                
                trackSpan.onclick = (function(spanEl, path) {
                    return function(e) {
                        clearVisualSelection();
                        spanEl.classList.add('active-selection');
                        currentPendingSelection = path;
                    };
                })(trackSpan, item.path);

                rowDiv.appendChild(trackSpan);
                li.appendChild(rowDiv);
                ul.appendChild(li);
            }
        }
    }
    return ul;
}

function openTreeModal(targetInputId, foldersOnly) {
    activeTargetInputId = targetInputId;
    foldersOnlyMode = foldersOnly;
    currentPendingSelection = null; 
    
    var modal = document.getElementById('tree-modal');
    var titleText = document.getElementById('modal-title-text');
    
    titleText.innerHTML = foldersOnly ? "Sélectionner un dossier" : "Sélectionner un élément";
    modal.style.display = "block";

    if (cachedRawData) {
        renderModalTree(cachedRawData);
    } else {
        fetchAndRenderTree();
    }
}

function hideModal() {
    document.getElementById('tree-modal').style.display = "none";
}

function confirmModalSelection() {
    if (currentPendingSelection !== null && activeTargetInputId) {
        document.getElementById(activeTargetInputId).value = currentPendingSelection;
        hideModal();
    } else {
        alert("Veuillez d'abord sélectionner un élément dans l'arbre.");
    }
}

function fetchAndRenderTree() {
    var bodyContainer = document.getElementById('modal-tree-body');
    bodyContainer.innerHTML = "<p style='color: #888; margin: 0;'>Chargement du disque...</p>";
    
    makeRequest('GET', API_TREE_URL, null, function (err, flatData) {
        if (!err && flatData && flatData.length > 0) {
            cachedRawData = flatData;
            renderModalTree(flatData);
        } else {
            bodyContainer.innerHTML = "<p style='color:#ff6b6b; margin:0;'>Index vide ou introuvable.</p>";
        }
    });
}

function renderModalTree(flatData) {
    var bodyContainer = document.getElementById('modal-tree-body');
    bodyContainer.innerHTML = "";
    var treeStructure = parseFlatListToTree(flatData);
    bodyContainer.appendChild(renderTreeDOM(treeStructure));
}

function triggerRefresh() {
    var btn = document.getElementById('btn-refresh');
    btn.disabled = true; btn.innerHTML = "⏳ Indexation...";
    
    makeRequest('POST', API_REFRESH_URL, {}, function (err, data) {
        btn.disabled = false; btn.innerHTML = "🔄 Indexer la DB";
        
        if (err) {
            alert("Erreur critique système lors de la communication avec le serveur.");
            return;
        }
        
        if (data && (data.status === "success" || data.status === "warning")) {
            var msg = "Indexation terminée !\n";
            msg += "Morceaux indexés : " + data.tracks_count + "\n";
            msg += "Nouveaux PDF convertis : " + data.converted_count + "\n";
            msg += "Temps d'exécution : " + data.duration + "\n";
            
            if (data.errors && data.errors.length > 0) {
                msg += "\n[⚠️ Attention] Des anomalies d'instruments ont été ignorées (" + data.errors.length + ") :\n";
                for (var i = 0; i < data.errors.length; i++) {
                    msg += "- " + data.errors[i] + "\n";
                }
            }
            alert(msg);
            cachedRawData = null;
        } else {
            alert("Erreur indéterminée renvoyée par le serveur.");
        }
    });
}

function convertToCamelCase(str) {
    if (!str) return "";
    var accents = "ÀÁÂÃÄÅ📂🎒ÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ";
    var sansAccents = "AAAAAAAECEEEEIIIIDNOOOOOOUUUUYbBaaaaaaaeceeeeiiiidnoooooouuuuyby";
    var cleanStr = "";
    for (var i = 0; i < str.length; i++) {
        var c = str.charAt(i);
        var index = accents.indexOf(c);
        if (index !== -1) {
            cleanStr += sansAccents.charAt(index);
        } else {
            cleanStr += c;
        }
    }

    var words = cleanStr.split(/[^a-zA-Z0-9]/);
    var camelCaseResult = "";
    var isFirstWordFound = false;

    for (var j = 0; j < words.length; j++) {
        var word = words[j];
        if (word.length === 0) continue;

        if (!isFirstWordFound) {
            camelCaseResult += word.toLowerCase();
            isFirstWordFound = true;
        } else {
            camelCaseResult += word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        }
    }
    return camelCaseResult;
}

function actionCreate() {
    var loc = document.getElementById('create-location').value;
    var title = document.getElementById('create-title').value;
    if (!loc || !title) { alert("Champs manquants."); return; }
    
    var cleanDirName = convertToCamelCase(title);
    var fullLocation = loc + '/' + cleanDirName;

    var params = { action: 'create', location: fullLocation, title: title };

    makeRequest('POST', API_CRUD_URL, params, function(err, res) {
        if (!err && res && (res.status === "success" || res.success === true)) {
            alert("Succès : Le morceau a été créé !");
            cachedRawData = null;
        } else {
            alert("Erreur lors de la création.");
        }
    });
}