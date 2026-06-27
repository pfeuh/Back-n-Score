/**
 * Usine à variables synchronisées (ES5 - Android 4/5/6)
 * Gère automatiquement : Variable <-> LocalStorage <-> Interface UI
 */

function createProp(config) {
    var _val = null;
    var key = config.key;
    var elId = config.elId;
    var isBool = config.isBool || false;
    var isInner = config.isInner || false;
    var defaultValue = config.default;

    // Fonction interne pour mettre à jour l'UI sans toucher au Storage
    var updateUI = function(value) {
        if (!elId) return;
        var el = document.getElementById(elId);
        if (!el) return;

        if (isBool) {
            el.checked = (value === true || value === "1" || value === 1);
        } else if (isInner) {
            el.innerHTML = value;
        } else {
            el.value = value;
        }
    };

    // 1. Initialisation
    try {
        var saved = localStorage.getItem(key);
        if (saved !== null) {
            _val = isBool ? (saved === "1") : saved;
        } else {
            _val = defaultValue;
        }
    } catch(e) {
        _val = defaultValue;
    }

    return {
        get: function() { return _val; },
        
        set: function(newVal) {
            _val = newVal;
            
            // A. Persistance (uniquement si nécessaire)
            try {
                var storageVal = isBool ? (_val ? "1" : "0") : _val;
                localStorage.setItem(key, storageVal);
            } catch(e) {
                console.error("Storage erreur");
            }

            // B. UI
            updateUI(_val);
            
            // C. Callback
            if (typeof config.onChange === "function") {
                config.onChange(_val);
            }
        },

        syncUI: function() {
            updateUI(_val);
        }
    };
}
