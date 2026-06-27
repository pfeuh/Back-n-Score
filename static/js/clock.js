document.addEventListener("DOMContentLoaded", function () {
    var clockButton = document.getElementById("bt_clock");

    function updateClock() {
        var now = new Date();
        var hours = now.getHours();
        var minutes = now.getMinutes();

        // On ajoute un zéro devant si le chiffre est inférieur à 10
        if (hours < 10) { hours = "0" + hours; }
        if (minutes < 10) { minutes = "0" + minutes; }

        var timeString = hours + ":" + minutes ;//+ ":" + seconds;

        // Met à jour le texte du bouton
        if (clockButton) {
            clockButton.innerHTML = timeString;
        }
    }

    // Lance l'horloge immédiatement au chargement
    updateClock();

    // Met à jour l'horloge toutes les secondes
    setInterval(updateClock, 1000);
});
