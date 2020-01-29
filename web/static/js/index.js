window.addEventListener("load", messageHandler);

function messageHandler() {
    var source = new EventSource('/stream');
    var out;
    var transmission = false;
    source.onmessage = function (e) {
        if (!transmission) {
            document.getElementById('col-3').innerHTML += '<div class="backgroundNotifications">\n' +
                '<h2 class="title">Powiadomienia:</h2>\n' +
                '<div id="notification" class="list-group">\n' +
                '</div>\n' +
                '</div>';
            transmission = true;
            out = document.getElementById('notification');
        }
        if(e.data !== "LOGGED_IN") {
            out.innerHTML = out.innerHTML + '<div class ="warning">Publikacja o tytule "' + e.data + '" została dodana w innej przeglądarce. Odśwież listę, aby ją zobaczyć.</div>';
        }
        else
        {
            out.innerHTML = out.innerHTML + '<div class ="error">Wykryto logowanie z innego źródła niż to!</div>';
        }
    };
}