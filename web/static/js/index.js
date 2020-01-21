window.addEventListener("load", messageHandler);

function messageHandler() {
        var source = new EventSource('/stream');
        var out = document.getElementById('title');
        source.onmessage = function(e) {
            out.innerHTML = out.innerHTML + '<div class ="warning">Publikacja o tytule "' +  e.data + '" została dodana w innej przeglądarce. Odśwież listę, aby ją zobaczyć.</div>';
        };
    }