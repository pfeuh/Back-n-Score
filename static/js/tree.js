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

    var closeBtn = document.createElement("div"); 
    closeBtn.className = "btn-cancel";
    closeBtn.innerText = "✕";
    closeBtn.style.position = "absolute";
    closeBtn.style.top = "10px";
    closeBtn.style.right = "10px";
    closeBtn.style.zIndex = "100";
    closeBtn.onclick = closeTreeView; 
    popupContent.appendChild(closeBtn);

    var treeHost = document.createElement('div');
    treeHost.id = "tree-container";
    treeHost.style.position = "absolute";
    treeHost.style.top = "40px";
    treeHost.style.bottom = "0"; 
    treeHost.style.left = "0";
    treeHost.style.right = "0";
    treeHost.style.overflowY = "scroll"; 
    treeHost.style.webkitOverflowScrolling = "touch";
    
    popupContent.appendChild(treeHost);
}

function addTreeRow(text, onClick, isSelected, container, indentLevel) {
    var div = document.createElement("div");
    div.className = "item-row";
    if (isSelected) {
        div.className += " selected";
        // Application d'une couleur jaune/or prononcée pour l'élément sélectionné
        div.style.setProperty('color', '#f1c40f', 'important');
    }
    
    // Utilisation de setProperty avec 'important' pour contourner d'éventuels conflits CSS globaux
    if (indentLevel) {
        div.style.setProperty('padding-left', (12 + (indentLevel * 20)) + 'px', 'important');
    }
    
    var cleanText = text.replace(/_/g, " ");
    div.innerHTML = isSelected ? "<b>" + cleanText + "</b>" : cleanText;
    
    if (isSelected) {
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

function renderAltInstrumentTree(container) {
    container.innerHTML = "";
    document.body.classList.add('tree-instruments-open');

    var selectedInstrument = typeof current_instrument !== "undefined" ? current_instrument.get() : "";

    var headerRow = document.createElement("div");
    headerRow.className = "item-row header-row";
    headerRow.innerText = "📁 Instruments du morceau";
    container.appendChild(headerRow);

    var branchDiv = document.createElement("div");
    container.appendChild(branchDiv);

    var loadingRow = document.createElement("div");
    loadingRow.className = "item-row loading-row";
    loadingRow.innerText = "Chargement des instruments...";
    branchDiv.appendChild(loadingRow);

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_available_instruments', true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            branchDiv.innerHTML = ""; 

            var instruments = [];
            if (xhr.status === 200) {
                try {
                    instruments = JSON.parse(xhr.responseText);
                } catch(e) {
                    console.error("Erreur parsing JSON instruments :", e);
                }
            }

            if (!instruments || instruments.length === 0) {
                var emptyRow = document.createElement("div");
                emptyRow.className = "item-row empty-row";
                emptyRow.innerText = "Aucun instrument trouvé pour ce morceau.";
                branchDiv.appendChild(emptyRow);
                return;
            }

            function getBaseInstrumentName(name) {
                if (name.indexOf("easy") === 0 && name.length > 4) name = name.substring(4);
                if (name.lastIndexOf("solo") === name.length - 4 && name.length > 4) name = name.substring(0, name.length - 4);
                if (name.length > 0) {
                    var lastChar = name.charAt(name.length - 1);
                    if (lastChar === '2' || lastChar === '3' || lastChar === '4') name = name.substring(0, name.length - 1);
                }
                return name;
            }

            var grouped = {};
            for (var i = 0; i < QUARTES_ORDER.length; i++) grouped[QUARTES_ORDER[i]] = [];
            grouped["NP"] = [];
            grouped["AUTRES"] = [];

            for (var i = 0; i < instruments.length; i++) {
                var instName = instruments[i];
                var tona = "AUTRES";
                var lookupName = instName;
                if (typeof META_INSTRUMENTS !== "undefined") {
                    if (!META_INSTRUMENTS[lookupName]) lookupName = getBaseInstrumentName(instName);
                    if (META_INSTRUMENTS[lookupName]) tona = META_INSTRUMENTS[lookupName][0];
                }
                if (!grouped[tona]) grouped[tona] = [];
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
                    subRow.className = "item-row tonalite-row";
                    subRow.style.setProperty('padding-left', '26px', 'important');
                    subRow.innerText = "🎵 " + tonName + " (" + listInsts.length + ")";
                    branchDiv.appendChild(subRow);

                    var subBranchDiv = document.createElement("div");
                    subBranchDiv.style.display = "none"; 
                    branchDiv.appendChild(subBranchDiv);

                    var openSub = function() {
                        subBranchDiv.style.display = "block";
                        subRow.classList.add('active');
                    };
                    var closeSub = function() {
                        subBranchDiv.style.display = "none";
                        subRow.classList.remove('active');
                    };

                    closeAllTonalites.push(closeSub);

                    var containsSelected = false;
                    for (var s = 0; s < listInsts.length; s++) {
                        if (listInsts[s] === selectedInstrument) { containsSelected = true; break; }
                    }
                    if (containsSelected) openSub();

                    subRow.onclick = function(e) {
                        e.stopPropagation(); 
                        if (subBranchDiv.style.display === "none") {
                            for (var s = 0; s < closeAllTonalites.length; s++) closeAllTonalites[s]();
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
                                    if (!META_INSTRUMENTS[lookupName]) lookupName = getBaseInstrumentName(instName);
                                    if (META_INSTRUMENTS[lookupName]) categoryName = META_INSTRUMENTS[lookupName][1] || "AUTRES";
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

                                    var infoXhr = new XMLHttpRequest();
                                    infoXhr.open('GET', infoUrl, true);
                                    infoXhr.onreadystatechange = function() {
                                        if (infoXhr.readyState === 4) {
                                            var nbPages = 1;
                                            if (infoXhr.status === 200) {
                                                try {
                                                    var data = JSON.parse(infoXhr.responseText);
                                                    if (data && data.status === "success" && data.nb_pages) nbPages = data.nb_pages;
                                                } catch(err) {}
                                            }
                                            getScore(instName, nbPages);
                                        }
                                    };
                                    infoXhr.send();
                                }
                                closeTreeView();
                            }, isSelected, subBranchDiv, 2);
                        })(listInsts[j]);
                    }
                })(tonaliteName, subInstruments);
            }
        }
    };
    xhr.send();
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
        if (data.hasOwnProperty(k)) fullData[k] = data[k];
    }

    for (var catName in fullData) {
        if (!fullData.hasOwnProperty(catName)) continue;

        (function(categoryName, categoryData) {
            var catRow = document.createElement("div");
            catRow.className = "item-row category-row";
            catRow.innerText = "🗄️ " + categoryName.replace(/_/g, " ");
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
                catRow.innerText = "🗄️ " + categoryName.replace(/_/g, " ");
            };

            closeAllCategories.push(closeMe);
            if (activeOpenedCategory === categoryName) openMe();

            catRow.onclick = function() {
                if (branchDiv.style.display === "none") {
                    for (var c = 0; c < closeAllCategories.length; c++) closeAllCategories[c]();
                    openMe();
                } else {
                    closeMe();
                    if (activeOpenedCategory === categoryName) activeOpenedCategory = null;
                }
            };

            if (categoryData instanceof Array) {
                for (var i = 0; i < categoryData.length; i++) {
                    (function(instName) {
                        var isSelected = (instName === selectedInstrument);
                        if (isSelected) openMe();
                        addTreeRow(instName, function() {
                            last_inst_path.set(modeName + "/" + categoryName + "/" + instName);
                            current_instrument.set(instName);
                            closeTreeView();
                        }, isSelected, branchDiv, 1);
                    })(categoryData[i]);
                }
            } else {
                var sortedSubKeys = [];
                for (var key in categoryData) {
                    if (categoryData.hasOwnProperty(key)) sortedSubKeys.push(key);
                }
                sortedSubKeys.sort(function(a, b) {
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
                        subRow.className = "item-row tonalite-row";
                        subRow.style.setProperty('padding-left', '25px', 'important');
                        subRow.innerText = tonaliteName;
                        branchDiv.appendChild(subRow);

                        var subBranchDiv = document.createElement("div");
                        subBranchDiv.style.display = "none"; 
                        branchDiv.appendChild(subBranchDiv);

                        var openSub = function() {
                            subBranchDiv.style.display = "block";
                            subRow.classList.add('active');
                            activeOpenedTonalite = tonaliteName;
                        };
                        var closeSub = function() {
                            subBranchDiv.style.display = "none";
                            subRow.classList.remove('active');
                        };

                        closeAllTonalites.push(closeSub);
                        if (activeOpenedTonalite === tonaliteName) openSub();

                        subRow.onclick = function(e) {
                            e.stopPropagation(); 
                            if (subBranchDiv.style.display === "none") {
                                for (var t = 0; t < closeAllTonalites.length; t++) closeAllTonalites[t]();
                                openSub();
                            } else {
                                closeSub();
                                if (activeOpenedTonalite === tonaliteName) activeOpenedTonalite = null;
                            }
                        };

                        for (var j = 0; j < subInstruments.length; j++) {
                            (function(instName) {
                                var isSelected = (instName === selectedInstrument);
                                if (isSelected) { openMe(); openSub(); }
                                addTreeRow(instName, function() {
                                    last_inst_path.set(modeName + "/" + categoryName + "/" + tonaliteName + "/" + instName);
                                    current_instrument.set(instName);
                                    closeTreeView();
                                }, isSelected, subBranchDiv, 2);
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

    function buildHtmlTree(folderData, currentContainer, currentPathParts) {
        var depth = currentPathParts.length; 

        if (!closeFunctionsByDepth[depth]) {
            closeFunctionsByDepth[depth] = [];
        }

        for (var folderName in folderData._subfolders) {
            if (!folderData._subfolders.hasOwnProperty(folderName)) continue;

            (function(name, subData) {
                var nextPathParts = currentPathParts.concat([name]);
                var folderFullPath = nextPathParts.join("/");
                var labelName = name.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); }).trim();

                var hasSubfolders = false;
                for (var subKey in subData._subfolders) {
                    if (subData._subfolders.hasOwnProperty(subKey)) { hasSubfolders = true; break; }
                }

                var isBook = !hasSubfolders;

                var folderRow = document.createElement("div");
                folderRow.className = isBook ? "item-row book-row" : "item-row folder-row";
                
                // Forçage de l'indentation avec setProperty pour contrer les !important potentiels du CSS global
                folderRow.style.setProperty('padding-left', (12 + (depth * 20)) + 'px', 'important');
                
                var icon = isBook ? "📘 " : "🗄️ ";
                folderRow.innerText = icon + labelName;
                currentContainer.appendChild(folderRow);

                var branchDiv = document.createElement("div");
                branchDiv.style.display = "none";
                currentContainer.appendChild(branchDiv);

                var openFolder = function() { branchDiv.style.display = "block"; };
                var closeFolder = function() { branchDiv.style.display = "none"; };

                closeFunctionsByDepth[depth].push(closeFolder);

                folderRow.onclick = function(e) {
                    e.stopPropagation();
                    if (branchDiv.style.display === "none") {
                        var siblingsClose = closeFunctionsByDepth[depth];
                        for (var s = 0; s < siblingsClose.length; s++) siblingsClose[s]();
                        openFolder();
                    } else {
                        closeFolder();
                    }
                };

                buildHtmlTree(subData, branchDiv, nextPathParts);

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
                    if (typeof current_page !== "undefined" && current_page.set) current_page.set(1);
                    if (typeof updateServerTrack === "function") updateServerTrack(track.location);
                    closeTreeView(); 
                }, isSelected, currentContainer, depth + 1);
            })(folderData._tracks[t]);
        }
    }

    buildHtmlTree(rootJson, container, []);

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