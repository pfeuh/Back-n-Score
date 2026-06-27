var contentDiv = document.getElementById("content"), 
    navDiv = document.getElementById("nav-bar"), 
    instDisplay = document.getElementById("current-inst");

var DATA_TRACKS = [], DATA_UI_POPULAR = {}, DATA_UI_CLASSY = {};
var SELECTED_INSTRUMENT = localStorage.getItem("selected_inst") || null;
var CURRENT_VOICE = localStorage.getItem("selected_voice") || "1";
var IS_SOLO = localStorage.getItem("is_solo") === "true";
var IS_EASY = localStorage.getItem("is_easy") === "true"; 
var CURRENT_MODE = localStorage.getItem("selected_mode") || "POPULAR";

var CURRENT_PAGE = 1;
var TOTAL_PAGES = 1;
var PDF_DOC = null;
var LAST_LOCATION = ""; 

window.onload = function() {
    if(SELECTED_INSTRUMENT) { instDisplay.innerText = SELECTED_INSTRUMENT.replace(/_/g, " "); }
    document.getElementById("voice-sel").value = CURRENT_VOICE;
    document.getElementById("solo-check").checked = IS_SOLO;
    document.getElementById("easy-check").checked = IS_EASY; 
    
    fetchData();

    startSync();
};

function setVoice(v) { CURRENT_VOICE = v; localStorage.setItem("selected_voice", v); }
function setSolo(s) { IS_SOLO = s; localStorage.setItem("is_solo", s); }
function setEasy(e) { IS_EASY = e; localStorage.setItem("is_easy", e); } 

var resizeTimer;
function handleResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        var loc = localStorage.getItem("last_track_loc");
        if (loc && document.getElementById("score-display")) {
            // On force IS_RENDERING à false pour permettre le redessinage du resize
            IS_RENDERING = false; 
            if (typeof renderV1 === "function") renderV1(loc, TOTAL_PAGES);
        }
    }, 250);
}
