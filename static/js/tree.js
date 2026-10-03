// Variables globales pour mémoriser l'état d'ouverture de l'arbre
var activeOpenedCategory = null;
var activeOpenedTonalite = null;

// Ordre personnalisé selon le cycle des quartes pour le tri des sous-catégories (tonalités)
var QUARTES_ORDER = ["DO", "FA", "SIb", "MIb", "LAb", "REb", "FA#", "SOLb", "SI", "MI", "LA", "RE", "SOL"];

function uiSelectInstrument() {
    loadView('instruments', "");
}

function uiSelectTrack() {
    loadView('tracks', "");
}

function uiSelectAltInstrument() {
    loadView('alt', "");
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

    // Conteneur principal unique de l'arbre (élargi et étendu vers le bas)
    var treeHost = document.createElement('div');
    treeHost.id = "tree-container";
    treeHost.style.position = "absolute";
    treeHost.style.top = "40px"; /* Légèrement remonté pour gagner en hauteur */
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
    div.style.padding = "6px 12px"; /* Padding encore plus réduit (compact) */
    if (paddingLeft) {
        div.style.paddingLeft = paddingLeft + "px";
    }
    div.style.borderBottom = "1px solid #333";
    div.style.boxSizing = "border-box"; 
    div.style.cursor = "pointer";
    div.style.color = "#FFFFFF";
    div.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
    div.style.whiteSpace = "nowrap"; 
    
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
    if (typeof stopPooling === "function") stopPooling();
    prepareTreeInterface(viewType); 
    
    var treeDiv = document.getElementById('tree-container');
    
    if (viewType === 'tracks') {
        renderTrackTree(DATA_TRACKS, path, treeDiv);
    } else if (viewType === 'alt') {
        renderAltInstrumentTree(treeDiv);
    } else {
        renderTrueInstrumentTree(treeDiv);
    }
}

// Affichage des instruments du morceau courant regroupés par tonalité grâce à META_INSTRUMENTS
function renderAltInstrumentTree(container) {
    container.innerHTML = "";
    document.body.classList.add('tree-instruments-open');

    var selectedInstrument = typeof current_instrument !== "undefined" ? current_instrument.get() : "";

    // Titre de section
    var headerRow = document.createElement("div");
    headerRow.style.backgroundColor = "#2a2a2a";
    headerRow.style.borderBottom = "2px solid #444";
    headerRow.style.color = "#f1c40f";
    headerRow.style.fontWeight = "bold";
    headerRow.style.padding = "8px 12px"; /* Padding compact */
    headerRow.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
    headerRow.style.whiteSpace = "nowrap";
    headerRow.innerText = "📁 Instruments du morceau";
    container.appendChild(headerRow);

    var branchDiv = document.createElement("div");
    branchDiv.style.display = "block";
    container.appendChild(branchDiv);

    fetch('/get_available_instruments')
        .then(function(response) {
            return response.json();
        })
        .then(function(instruments) {
            if (!instruments || instruments.length === 0) {
                var emptyRow = document.createElement("div");
                emptyRow.style.padding = "10px 12px";
                emptyRow.style.fontSize = "22px";
                emptyRow.style.color = "#888";
                emptyRow.innerText = "Aucun instrument trouvé pour ce morceau.";
                branchDiv.appendChild(emptyRow);
                return;
            }

            function getBaseInstrumentName(name) {
                if (name.startsWith("easy") && name.length > 4) {
                    name = name.substring(4);
                }
                if (name.endsWith("solo") && name.length > 4) {
                    name = name.substring(0, name.length - 4);
                }
                if (name.length > 0 && "234".indexOf(name.charAt(name.length - 1)) !== -1) {
                    name = name.substring(0, name.length - 1);
                }
                return name;
            }

            var grouped = {};
            for (var i = 0; i < QUARTES_ORDER.length; i++) {
                grouped[QUARTES_ORDER[i]] = [];
            }
            grouped["NP"] = [];
            grouped["AUTRES"] = [];

            for (var i = 0; i < instruments.length; i++) {
                var instName = instruments[i];
                var tona = "AUTRES";

                var lookupName = instName;
                if (typeof META_INSTRUMENTS !== "undefined") {
                    if (!META_INSTRUMENTS[lookupName]) {
                        lookupName = getBaseInstrumentName(instName);
                    }
                    if (META_INSTRUMENTS[lookupName]) {
                        tona = META_INSTRUMENTS[lookupName][0];
                    }
                }

                if (!grouped[tona]) {
                    grouped[tona] = [];
                }
                grouped[tona].push(instName);
            }

            var closeAllTonalites = [];
            var allKeysToDisplay = QUARTES_ORDER.concat(["NP", "AUTRES"]);

            for (var t = 0; t < allKeysToDisplay.length; t++) {
                var tonaliteName = allKeysToDisplay[t];
                var subInstruments = grouped[tonaliteName];
                if (!subInstruments || subInstruments.length === 0) continue;

                subInstruments.sort();

                (function(tonName, listInsts) {
                    var subRow = document.createElement("div");
                    subRow.style.backgroundColor = "#1f1f1f";
                    subRow.style.color = "#FFF";
                    subRow.style.padding = "6px 10px 6px 26px"; /* Padding compact */
                    subRow.style.borderBottom = "1px solid #333";
                    subRow.style.cursor = "pointer";
                    subRow.style.fontWeight = "500";
                    subRow.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
                    subRow.style.whiteSpace = "nowrap";
                    subRow.innerText = "🎵 " + tonName + " (" + listInsts.length + ")";
                    branchDiv.appendChild(subRow);

                    var subBranchDiv = document.createElement("div");
                    subBranchDiv.style.display = "none"; 
                    branchDiv.appendChild(subBranchDiv);

                    var openSub = function() {
                        subBranchDiv.style.display = "block";
                        subRow.style.color = "#f1c40f"; 
                    };
                    var closeSub = function() {
                        subBranchDiv.style.display = "none";
                        subRow.style.color = "#FFF";
                    };

                    closeAllTonalites.push(closeSub);

                    var containsSelected = listInsts.indexOf(selectedInstrument) !== -1;
                    if (containsSelected) {
                        openSub();
                    }

                    subRow.onclick = function(e) {
                        e.stopPropagation(); 
                        if (subBranchDiv.style.display === "none") {
                            for (var s = 0; s < closeAllTonalites.length; s++) {
                                closeAllTonalites[s]();
                            }
                            openSub();
                        } else {
                            closeSub();
                        }
                    };

                    for (var j = 0; j < listInsts.length; j++) {
                        (function(instName) {
                            var isSelected = (instName === selectedInstrument);
                            addTreeRow(instName, function() {
                                var modeName = (typeof instru_select_mode !== "undefined" && instru_select_mode.get() == MODE_POPULAR) ? "POPULAR" : "CLASSIQUE";
                                var categoryName = "AUTRES";
                                var lookupName = instName;

                                if (typeof META_INSTRUMENTS !== "undefined") {
                                    if (!META_INSTRUMENTS[lookupName]) {
                                        lookupName = getBaseInstrumentName(instName);
                                    }
                                    if (META_INSTRUMENTS[lookupName]) {
                                        categoryName = META_INSTRUMENTS[lookupName][1] || "AUTRES";
                                    }
                                }

                                if (typeof last_inst_path !== "undefined" && last_inst_path.set) {
                                    if (tonName === "AUTRES" || tonName === "NP") {
                                        last_inst_path.set(modeName + "/" + categoryName + "/" + instName);
                                    } else {
                                        last_inst_path.set(modeName + "/" + categoryName + "/" + tonName + "/" + instName);
                                    }
                                }

                                if (typeof track_location !== "undefined" && typeof getScore === "function") {
                                    var loc = track_location.get();
                                    var mode = (typeof instru_select_mode !== "undefined") ? instru_select_mode.get() : MODE_POPULAR;
                                    var voice = (typeof voice_num !== "undefined") ? voice_num.get() : 1;
                                    var solo = (typeof solo_toggle !== "undefined") ? (solo_toggle.get() ? 1 : 0) : 0;
                                    var easy = (typeof easy_toggle !== "undefined") ? (easy_toggle.get() ? 1 : 0) : 0;

                                    var infoUrl = '/get_score_info?loc=' + encodeURIComponent(loc) +
                                                  '&instrument=' + encodeURIComponent(instName) +
                                                  '&voice=' + encodeURIComponent(voice) +
                                                  '&mode=' + encodeURIComponent(mode) +
                                                  '&solo=' + encodeURIComponent(solo) +
                                                  '&easy=' + encodeURIComponent(easy);

                                    fetch(infoUrl)
                                        .then(function(res) { return res.json(); })
                                        .then(function(data) {
                                            var nbPages = (data && data.status === "success" && data.nb_pages) ? data.nb_pages : 1;
                                            getScore(instName, nbPages);
                                        })
                                        .catch(function(err) {
                                            console.error("Erreur get_score_info :", err);
                                            getScore(instName, 1);
                                        });
                                }

                                closeTreeView();
                            }, isSelected, subBranchDiv, 50);
                        })(listInsts[j]);
                    }
                })(tonaliteName, subInstruments);
            }
        })
        .catch(function(error) {
            console.error("Erreur lors du chargement des instruments alternatifs :", error);
        });
}

function renderTrueInstrumentTree(container) {
    container.innerHTML = "";
    
    document.body.classList.add('tree-instruments-open');
    
    var modeName = (instru_select_mode.get() == MODE_POPULAR) ? "POPULAR" : "CLASSIQUE";
    var data = (modeName === "POPULAR") ? DATA_UI_POPULAR : DATA_UI_CLASSIQUE;
    var selectedInstrument = current_instrument.get();

    var closeAllCategories = [];
    var closeAllTonalites = [];

    var fullData = {};
    fullData["CHEF"] = ["conducteur", "tutti"];
    for (var k in data) {
        if (data.hasOwnProperty(k)) {
            fullData[k] = data[k];
        }
    }

    for (var catName in fullData) {
        if (!fullData.hasOwnProperty(catName)) continue;

        (function(categoryName, categoryData) {
            var catRow = document.createElement("div");
            catRow.style.backgroundColor = "#2a2a2a";
            catRow.style.borderBottom = "2px solid #444";
            catRow.style.color = "#f1c40f";
            catRow.style.fontWeight = "bold";
            catRow.style.padding = "8px 12px"; /* Padding compact */
            catRow.style.cursor = "pointer";
            catRow.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
            catRow.style.whiteSpace = "nowrap";
            catRow.innerText = "📁 " + categoryName.replace(/_/g, " ");
            container.appendChild(catRow);

            var branchDiv = document.createElement("div");
            branchDiv.style.display = "none"; 
            container.appendChild(branchDiv);

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

            if (activeOpenedCategory === categoryName) {
                openMe();
            }

            catRow.onclick = function() {
                if (branchDiv.style.display === "none") {
                    for (var c = 0; c < closeAllCategories.length; c++) {
                        closeAllCategories[c]();
                    }
                    openMe();
                } else {
                    closeMe();
                    if (activeOpenedCategory === categoryName) {
                        activeOpenedCategory = null;
                    }
                }
            };

            if (categoryData instanceof Array) {
                for (var i = 0; i < categoryData.length; i++) {
                    (function(instName) {
                        var isSelected = (instName === selectedInstrument);
                        if (isSelected) {
                            openMe();
                        }
                        addTreeRow(instName, function() {
                            last_inst_path.set(modeName + "/" + categoryName + "/" + instName);
                            current_instrument.set(instName);
                            closeTreeView();
                        }, isSelected, branchDiv, 25);
                    })(categoryData[i]);
                }
            } else {
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
                        var subRow = document.createElement("div");
                        subRow.style.backgroundColor = "#1f1f1f";
                        subRow.style.color = "#FFF";
                        subRow.style.padding = "6px 10px 6px 25px"; /* Padding compact */
                        subRow.style.borderBottom = "1px solid #333";
                        subRow.style.cursor = "pointer";
                        subRow.style.fontWeight = "500";
                        subRow.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
                        subRow.style.whiteSpace = "nowrap";
                        subRow.innerText = tonaliteName;
                        branchDiv.appendChild(subRow);

                        var subBranchDiv = document.createElement("div");
                        subBranchDiv.style.display = "none"; 
                        branchDiv.appendChild(subBranchDiv);

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

                        if (activeOpenedTonalite === tonaliteName) {
                            openSub();
                        }

                        subRow.onclick = function(e) {
                            e.stopPropagation(); 
                            if (subBranchDiv.style.display === "none") {
                                for (var t = 0; t < closeAllTonalites.length; t++) {
                                    closeAllTonalites[t]();
                                }
                                openSub();
                            } else {
                                closeSub();
                                if (activeOpenedTonalite === tonaliteName) {
                                    activeOpenedTonalite = null;
                                }
                            }
                        };

                        for (var j = 0; j < subInstruments.length; j++) {
                            (function(instName) {
                                var isSelected = (instName === selectedInstrument);
                                if (isSelected) {
                                    openMe();
                                    openSub();
                                }
                                addTreeRow(instName, function() {
                                    last_inst_path.set(modeName + "/" + categoryName + "/" + tonaliteName + "/" + instName);
                                    current_instrument.set(instName);
                                    closeTreeView();
                                }, isSelected, subBranchDiv, 50);
                            })(subInstruments[j]);
                        }
                    })(subKey, categoryData[subKey]);
                }
            }

        })(catName, fullData[catName]);
    }
}

function renderTrackTree(tree, basePath, container) {
    container.innerHTML = "";
    var lastLoc = track_location.get();

    var rootJson = { _tracks: [], _subfolders: {} };

    for (var i = 0; i < tree.length; i++) {
        var item = tree[i];
        var loc = item.location || "";
        var parts = loc.split("/");
        
        var currentFolder = rootJson;
        for (var p = 0; p < parts.length; p++) {
            var part = parts[p];
            if (p === parts.length - 1) {
                currentFolder._tracks.push(item);
            } else {
                if (!currentFolder._subfolders[part]) {
                    currentFolder._subfolders[part] = { _tracks: [], _subfolders: {} };
                }
                currentFolder = currentFolder._subfolders[part];
            }
        }
    }

    var closeFunctionsByDepth = [];

    function buildHtmlTree(folderData, currentContainer, padding, currentPathParts) {
        var depth = currentPathParts.length + 1;

        if (!closeFunctionsByDepth[depth]) {
            closeFunctionsByDepth[depth] = [];
        }

        for (var folderName in folderData._subfolders) {
            if (!folderData._subfolders.hasOwnProperty(folderName)) continue;

            (function(name, subData) {
                var nextPathParts = currentPathParts.concat([name]);
                var folderFullPath = nextPathParts.join("/");
                var labelName = name.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); }).trim();

                var folderRow = document.createElement("div");
                folderRow.style.backgroundColor = (depth === 1) ? "#2a2a2a" : "#1f1f1f";
                folderRow.style.borderBottom = "1px solid #333";
                folderRow.style.color = (depth === 1) ? "#f1c40f" : "#FFF";
                folderRow.style.fontWeight = (depth === 1) ? "bold" : "500";
                folderRow.style.padding = "6px 12px"; /* Padding compact */
                folderRow.style.paddingLeft = padding + "px";
                folderRow.style.cursor = "pointer";
                folderRow.style.fontSize = "22px"; /* Taille de police augmentée à 22px */
                folderRow.style.whiteSpace = "nowrap";
                
                var icon = (depth === 1) ? "📁 " : (depth === 2 ? "📘 " : "🗄️ ");
                folderRow.innerText = icon + labelName;
                currentContainer.appendChild(folderRow);

                var branchDiv = document.createElement("div");
                branchDiv.style.display = "none";
                currentContainer.appendChild(branchDiv);

                var openFolder = function() {
                    branchDiv.style.display = "block";
                    if (depth === 1) folderRow.innerText = "📂 " + labelName;
                };
                var closeFolder = function() {
                    branchDiv.style.display = "none";
                    if (depth === 1) folderRow.innerText = "📁 " + labelName;
                };

                closeFunctionsByDepth[depth].push(closeFolder);

                folderRow.onclick = function(e) {
                    e.stopPropagation();
                    if (branchDiv.style.display === "none") {
                        var siblingsClose = closeFunctionsByDepth[depth];
                        for (var s = 0; s < siblingsClose.length; s++) {
                            siblingsClose[s]();
                        }
                        openFolder();
                    } else {
                        closeFolder();
                    }
                };

                buildHtmlTree(subData, branchDiv, padding + 16, nextPathParts); /* Retrait légèrement réduit pour la récursion */

                if (lastLoc && lastLoc.indexOf(folderFullPath + "/") === 0) {
                    openFolder();
                }

            })(folderName, folderData._subfolders[folderName]);
        }

        for (var t = 0; t < folderData._tracks.length; t++) {
            (function(track) {
                var isSelected = (track.location === lastLoc);
                addTreeRow(track.title, function() { 
                    track_location.set(track.location);
                    
                    if (typeof current_page !== "undefined" && current_page.set) {
                        current_page.set(1);
                    }
                    
                    if (typeof updateServerTrack === "function") {
                        updateServerTrack(track.location);
                    }
                    closeTreeView(); 
                }, isSelected, currentContainer, padding);
            })(folderData._tracks[t]);
        }
    }

    buildHtmlTree(rootJson, container, 12, []);

    if (typeof checkSync === "function") checkSync(); 
}

function closeTreeView() {
    var treeOverlay = document.getElementById('tree-popup-overlay');
    if (treeOverlay) treeOverlay.style.display = 'none';

    var popupContent = document.getElementById('tree-popup-content');
    if (popupContent) popupContent.innerHTML = ""; 
    
    document.body.classList.remove('tree-open');
    document.body.classList.remove('tree-instruments-open');
    document.body.className = ""; 
    
    var menuOverlay = document.getElementById('menu-popup-overlay');
    if (menuOverlay) menuOverlay.style.display = 'none';
    
    if (typeof updateScoreView === "function") {
        updateScoreView();
    } else if (typeof checkUpdateScore === "function") {
        checkUpdateScore();
    } else if (typeof loadScore === "function") {
        loadScore();
    }
    
    if (typeof startPooling === "function") startPooling(); 
}