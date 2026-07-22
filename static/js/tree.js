// Variables globales pour mémoriser l'état d'ouverture de l'accordéon strict
var activeOpenedCategory = null;
var activeOpenedTonalite = null;

// Ordre personnalisé selon le cycle des quartes pour le tri des sous-catégories (tonalités)
var QUARTES_ORDER = ["DO", "FA", "SIb", "MIb", "LAb", "REb", "FA#", "SOLb", "SI", "MI", "LA", "RE", "SOL"];

function uiSelectInstrument() {
    loadView('instruments', "");
}

function uiSelectTrack() {
    var currentPath = track_location.get() || "";
    var lastSlash = currentPath.lastIndexOf("/");
    var folderPath = "";
    
    if (lastSlash !== -1) {
        folderPath = currentPath.substring(0, lastSlash);
    }

    loadView('tracks', folderPath);
}

function prepareTreeInterface(viewType) {
    var popupContent = document.getElementById('tree-popup-content');
    popupContent.innerHTML = ""; 

    document.body.classList.add('tree-open');
    
    var treeOverlay = document.getElementById('tree-popup-overlay');
    if (treeOverlay) treeOverlay.style.display = 'block';

    // Bouton de fermeture global ✕ en haut à droite de la popup
    var closeBtn = document.createElement("div"); 
    closeBtn.className = "btn-cancel";
    closeBtn.innerText = "✕";
    closeBtn.style.position = "absolute";
    closeBtn.style.top = "10px";
    closeBtn.style.right = "10px";
    closeBtn.style.zIndex = "100";
    closeBtn.onclick = closeTreeView; 
    popupContent.appendChild(closeBtn);

    // Conteneur principal unique de l'arbre
    var treeHost = document.createElement('div');
    treeHost.id = "tree-container";
    treeHost.style.position = "absolute";
    treeHost.style.top = "50px"; /* Laisse de l'espace pour le bouton fermer */
    treeHost.style.bottom = "0"; 
    treeHost.style.left = "0";
    treeHost.style.right = "0";
    treeHost.style.overflowY = "scroll"; 
    treeHost.style.webkitOverflowScrolling = "touch";
    
    popupContent.appendChild(treeHost);
}

function addTreeRow(text, onClick, isSelected, container, paddingLeft) {
    var div = document.createElement("div");
    div.className = "item-row";
    div.style.display = "block";
    div.style.width = "100%";
    div.style.padding = "12px 15px"; 
    if (paddingLeft) {
        div.style.paddingLeft = paddingLeft + "px";
    }
    div.style.borderBottom = "1px solid #333";
    div.style.boxSizing = "border-box"; 
    div.style.cursor = "pointer";
    div.style.color = "#FFFFFF";
    div.style.fontSize = "16px";
    
    var cleanText = text.replace(/_/g, " ");
    div.innerHTML = isSelected ? "<b>" + cleanText + "</b>" : cleanText;
    
    if (isSelected) {
        div.style.backgroundColor = "#444";
        div.style.color = "#f1c40f";

        setTimeout(function() {
            div.scrollIntoView(false);
        }, 150); 
    }

    div.onclick = onClick;
    container.appendChild(div);
    return div;
}

function loadView(viewType, path) {
    stopPooling();
    prepareTreeInterface(viewType); 
    
    var treeDiv = document.getElementById('tree-container');
    
    if (viewType === 'tracks') {
        renderTrackTree(DATA_TRACKS, path, treeDiv);
    } else {
        renderTrueInstrumentTree(treeDiv);
    }
}

function renderTrueInstrumentTree(container) {
    container.innerHTML = "";
    
    var modeName = (instru_select_mode.get() == MODE_POPULAR) ? "POPULAR" : "CLASSIQUE";
    var data = (modeName === "POPULAR") ? DATA_UI_POPULAR : DATA_UI_CLASSIQUE;
    var selectedInstrument = current_instrument.get();

    // Tableaux pour stocker les fonctions de fermeture afin de gérer l'accordéon strict à la volée
    var closeAllCategories = [];
    var closeAllTonalites = [];

    // --- Ajout manuel de la catégorie CHEF avec "conducteur" en minuscules ---
    var fullData = {};
    fullData["CHEF"] = ["conducteur", "tutti"];
    for (var k in data) {
        if (data.hasOwnProperty(k)) {
            fullData[k] = data[k];
        }
    }

    // Parcourt les catégories principales (CHEF, BOIS, CUIVRES, MELODISTES...)
    for (var catName in fullData) {
        if (!fullData.hasOwnProperty(catName)) continue;

        (function(categoryName, categoryData) {
            // Création de l'entête de la catégorie
            var catRow = document.createElement("div");
            catRow.style.backgroundColor = "#2a2a2a";
            catRow.style.borderBottom = "2px solid #444";
            catRow.style.color = "#f1c40f";
            catRow.style.fontWeight = "bold";
            catRow.style.padding = "14px 15px";
            catRow.style.cursor = "pointer";
            catRow.style.fontSize = "16px";
            catRow.innerText = "📁 " + categoryName.replace(/_/g, " ");
            container.appendChild(catRow);

            // Conteneur de la branche (les enfants)
            var branchDiv = document.createElement("div");
            branchDiv.style.display = "none"; // Masqué par défaut
            container.appendChild(branchDiv);

            // Fonctions internes pour ouvrir/fermer cette catégorie spécifique
            var openMe = function() {
                branchDiv.style.display = "block";
                catRow.innerText = "📂 " + categoryName.replace(/_/g, " ");
                activeOpenedCategory = categoryName;
            };
            var closeMe = function() {
                branchDiv.style.display = "none";
                catRow.innerText = "📁 " + categoryName.replace(/_/g, " ");
            };

            closeAllCategories.push(closeMe);

            // Si c'est la catégorie précédemment ouverte, on la garde ouverte au chargement
            if (activeOpenedCategory === categoryName) {
                openMe();
            }

            // Gestion du clic pour la catégorie (Accordéon Strict)
            catRow.onclick = function() {
                if (branchDiv.style.display === "none") {
                    // On ferme d'abord toutes les autres catégories principales
                    for (var c = 0; c < closeAllCategories.length; c++) {
                        closeAllCategories[c]();
                    }
                    openMe();
                } else {
                    closeMe();
                    activeOpenedCategory = null;
                }
            };

            // Remplissage de la branche
            if (categoryData instanceof Array) {
                // Cas standard : Tableau direct d'instruments (ex: CHEF, CUIVRES, VOIX...)
                for (var i = 0; i < categoryData.length; i++) {
                    (function(instName) {
                        var isSelected = (instName === selectedInstrument);
                        
                        // Si l'instrument est sélectionné au chargement, on déplie la catégorie
                        if (isSelected) {
                            for (var c = 0; c < closeAllCategories.length; c++) {
                                closeAllCategories[c]();
                            }
                            openMe();
                        }

                        addTreeRow(instName, function() {
                            last_inst_path.set(modeName + "/" + categoryName + "/" + instName);
                            current_instrument.set(instName);
                            closeTreeView();
                        }, isSelected, branchDiv, 35);
                    })(categoryData[i]);
                }
            } else {
                // Cas particulier : Imbrication par tonalités (ex: MELODISTES)
                // Extraction et tri des clés selon la suite des quartes
                var sortedSubKeys = Object.keys(categoryData).sort(function(a, b) {
                    var indexA = QUARTES_ORDER.indexOf(a);
                    var indexB = QUARTES_ORDER.indexOf(b);
                    if (indexA === -1) indexA = 999;
                    if (indexB === -1) indexB = 999;
                    return indexA - indexB;
                });

                for (var k = 0; k < sortedSubKeys.length; k++) {
                    var subKey = sortedSubKeys[k];
                    
                    (function(tonaliteName, subInstruments) {
                        // Ligne de la sous-catégorie (Tonalité)
                        var subRow = document.createElement("div");
                        subRow.style.backgroundColor = "#1f1f1f";
                        subRow.style.color = "#FFF";
                        subRow.style.padding = "10px 10px 10px 30px";
                        subRow.style.borderBottom = "1px solid #333";
                        subRow.style.cursor = "pointer";
                        subRow.style.fontWeight = "500";
                        subRow.innerText = tonaliteName;
                        branchDiv.appendChild(subRow);

                        // Conteneur pour les instruments de cette tonalité
                        var subBranchDiv = document.createElement("div");
                        subBranchDiv.style.display = "none"; 
                        branchDiv.appendChild(subBranchDiv);

                        // Fonctions internes pour ouvrir/fermer cette tonalité spécifique
                        var openSub = function() {
                            subBranchDiv.style.display = "block";
                            subRow.style.color = "#f1c40f"; 
                            activeOpenedTonalite = tonaliteName;
                        };
                        var closeSub = function() {
                            subBranchDiv.style.display = "none";
                            subRow.style.color = "#FFF";
                        };

                        closeAllTonalites.push(closeSub);

                        // Gestion du clic pour la tonalité (Accordéon Strict au sein de la catégorie)
                        subRow.onclick = function(e) {
                            e.stopPropagation(); // Évite de trigger le clic de la catégorie parente
                            if (subBranchDiv.style.display === "none") {
                                // On ferme toutes les autres tonalités ouvertes
                                for (var t = 0; t < closeAllTonalites.length; t++) {
                                    closeAllTonalites[t]();
                                }
                                openSub();
                            } else {
                                closeSub();
                                activeOpenedTonalite = null;
                            }
                        };

                        // Insertion des instruments sous la tonalité
                        for (var j = 0; j < subInstruments.length; j++) {
                            (function(instName) {
                                var isSelected = (instName === selectedInstrument);
                                
                                // Si l'instrument est celui sélectionné actuellement, on force l'ouverture
                                if (isSelected) {
                                    // 1. Ouvrir la catégorie principale
                                    for (var c = 0; c < closeAllCategories.length; c++) {
                                        closeAllCategories[c]();
                                    }
                                    openMe();
                                    
                                    // 2. Ouvrir la sous-catégorie de tonalité
                                    for (var t = 0; t < closeAllTonalites.length; t++) {
                                        closeAllTonalites[t]();
                                    }
                                    openSub();
                                }

                                addTreeRow(instName, function() {
                                    last_inst_path.set(modeName + "/" + categoryName + "/" + tonaliteName + "/" + instName);
                                    current_instrument.set(instName);
                                    closeTreeView();
                                }, isSelected, subBranchDiv, 55);
                            })(subInstruments[j]);
                        }
                    })(subKey, categoryData[subKey]);
                }
            }

        })(catName, fullData[catName]);
    }
}

function renderTrackTree(tree, basePath, container) {
    container.innerHTML = ""; // On vide le conteneur avant le rendu pour éviter les cumuls de dossiers parents

    // Ajout du bouton de retour si on se trouve dans un sous-dossier
    if (basePath) {
        var lastSlash = basePath.lastIndexOf("/");
        var parentPath = "";
        if (lastSlash !== -1) {
            parentPath = basePath.substring(0, lastSlash);
        }
        addTreeRow("📁 .. [Retour]", function() {
            loadView('tracks', parentPath);
        }, false, container, 15);
    }

    var folders = {};
    var lastLoc = track_location.get();

    for (var i = 0; i < tree.length; i++) {
        var item = tree[i];
        var loc = item.location;
        if (basePath && loc.indexOf(basePath + "/") !== 0) continue;
        var relative = basePath ? loc.substring(basePath.length + 1) : loc;
        var parts = relative.split("/");
        var segment = parts[0];

        if (parts.length > 1) {
            if (!folders[segment]) {
                var fullPath = (basePath ? basePath + "/" : "") + segment;
                var depth = loc.split("/").length - fullPath.split("/").length;
                folders[segment] = { icon: (depth === 1 ? "📘 " : "🗄️ "), path: fullPath };
            }
        } else {
            (function(track) {
                var isSelected = (track.location === lastLoc);
                addTreeRow(track.title, function(){ 
                    track_location.set(track.location);
                    if (typeof updateServerTrack === "function") updateServerTrack(track.location);
                    closeTreeView(); 
                }, isSelected, container, 15); 
            })(item);
        }
    }

    for (var f in folders) {
        (function(name, info) {
            var label = name.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); }).trim();
            addTreeRow(info.icon + label, function() { loadView('tracks', info.path); }, false, container, 15);
        })(f, folders[f]);
    }
    if (typeof checkSync === "function") checkSync(); 
}

function closeTreeView() {
    var treeOverlay = document.getElementById('tree-popup-overlay');
    if (treeOverlay) treeOverlay.style.display = 'none';

    var popupContent = document.getElementById('tree-popup-content');
    if (popupContent) popupContent.innerHTML = ""; 
    
    document.body.classList.remove('tree-open');
    document.body.className = ""; 
    
    if (typeof checkUpdateScore === "function") {
        checkUpdateScore();
    }
    
    if (typeof startPooling === "function") startPooling(); 
}