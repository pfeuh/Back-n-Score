function loadView(viewType, path) {
    if (typeof stopSync === "function") stopSync(); // On coupe le polling
    
    contentDiv.innerHTML = ""; contentDiv.scrollTop = 0;
    var currentPath = (typeof path === "string") ? path : "";
    localStorage.setItem(viewType === 'tracks' ? "last_track_path" : "last_inst_path", currentPath);
    if (viewType === 'instruments' && currentPath) {
        var m = currentPath.split("/")[0];
        if (m === "POPULAR" || m === "CLASSY") { CURRENT_MODE = m; localStorage.setItem("selected_mode", m); }
    }
    renderNavigation(viewType, currentPath);
    if (viewType === 'tracks') { renderTrackTree(DATA_TRACKS, currentPath); }
    else { renderInstrumentTree(currentPath); }
}

function renderNavigation(view, path) {
    navDiv.innerHTML = ""; navDiv.style.display = "block"; document.body.className = "with-nav";
    var cancelBtn = document.createElement("div"); cancelBtn.className = "btn-cancel"; cancelBtn.innerText = "✖"; 
    //~ cancelBtn.onclick = function() { contentDiv.innerHTML = ""; navDiv.style.display = "none"; document.body.className = ""; startSync()};
    cancelBtn.onclick = function() { 
        // On cache les menus
        navDiv.style.display = "none"; 
        document.body.className = ""; 
        
        // On relance la synchro
        if (typeof startSync === "function") startSync(); 
        
        // Au lieu de vider le contentDiv, on s'assure juste 
        // que la partition actuelle est bien affichée
        var loc = localStorage.getItem("last_track_loc");
        if (loc) {
            // On récupère l'objet morceau pour le rafraîchir
            var track = DATA_TRACKS.filter(function(t) { return t.location === loc; })[0];
            if (track) {
                openScore(track, true); // true = ne pas pousser au serveur
            }
        }
    };
    navDiv.appendChild(cancelBtn);
    var rootBtn = document.createElement("div"); rootBtn.className = "breadcrumb-item link"; rootBtn.innerText = (view === 'tracks' ? "🏠 Biblio" : "🏠 Instr.");
    rootBtn.onclick = function() { loadView(view, ""); }; navDiv.appendChild(rootBtn);
    if (path !== "") {
        var parts = path.split("/"), builtPath = "";
        for (var i = 0; i < parts.length; i++) {
            if (!parts[i]) continue;
            builtPath += (builtPath === "" ? "" : "/") + parts[i];
            (function(p, targetPath, last) {
                var segment = document.createElement("div"); segment.className = "breadcrumb-item " + (last ? "current" : "link");
                segment.innerText = p.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); }).trim();
                if (!last) segment.onclick = function() { loadView(view, targetPath); }; navDiv.appendChild(segment);
            })(parts[i], builtPath, (i === parts.length - 1));
        }
    }
}

function renderTrackTree(tree, basePath) {
    var folders = {};
    // NETTOYAGE : Une seule source de vérité : la location technique
    var lastLoc = localStorage.getItem("last_track_loc");

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
                // On ne compare que la location pour garantir la synchro PC/Tablette
                var isSelected = (track.location === lastLoc);
                
                addTreeRow(
                    "🎵 " + track.title, 
                    function(){ openScore(track); }, 
                    isSelected
                ); 
            })(item);
        }
    }

    for (var f in folders) {
        (function(name, info) {
            var label = name.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); }).trim();
            addTreeRow(info.icon + label, function() { loadView('tracks', info.path); });
        })(f, folders[f]);
    }

    if (typeof checkSync === "function") {
        checkSync(); 
    }
}

function renderInstrumentTree(path) {
    if (!path) { addTreeRow("📂 MODE POPULAR", function() { loadView('instruments', "POPULAR"); }); addTreeRow("📂 MODE CLASSY", function() { loadView('instruments', "CLASSY"); }); return; }
    var parts = path.split("/"), currentLevel = (parts[0] === "POPULAR") ? DATA_UI_POPULAR : DATA_UI_CLASSY;
    for (var i = 1; i < parts.length; i++) { if (currentLevel) currentLevel = currentLevel[parts[i]]; }
    if (currentLevel instanceof Array) {
        for (var k = 0; k < currentLevel.length; k++) {
            (function(inst) { addTreeRow("🎺 " + inst, function() { selectInstrument(inst); }, (inst === SELECTED_INSTRUMENT)); })(currentLevel[k]);
        }
    } else { for (var sub in currentLevel) { (function(s) { addTreeRow("📁 " + s, function() { loadView('instruments', path + "/" + s); }); })(sub); } }
}

function addTreeRow(text, onClick, isSelected) {
    var div = document.createElement("div"); div.className = "item-row"; var cleanText = text.replace(/_/g, " ");
    div.innerHTML = isSelected ? "<b>" + cleanText + "</b>" : cleanText;
    if (isSelected) {
        div.style.backgroundColor = "#fff9c4"; div.style.borderLeft = "5px solid #f1c40f";
        contentDiv.appendChild(div); 
        setTimeout(function(){ div.scrollIntoView({behavior: "smooth", block: "center"}); }, 100);
    } else { contentDiv.appendChild(div); }
    div.onclick = onClick;
}

function selectInstrument(inst) {
    SELECTED_INSTRUMENT = inst; localStorage.setItem("selected_inst", inst);
    instDisplay.innerText = inst.replace(/_/g, " ");
    contentDiv.innerHTML = "<h2 style='color:white; text-align:center;'>✅ Instrument sélectionné !</h2>"; 
    navDiv.style.display = "none"; document.body.className = "";
}
