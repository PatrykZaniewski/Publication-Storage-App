window.addEventListener("load", afterLoad);
var files;

function afterLoad() {
    files = document.getElementById("files");
    document.getElementById("submitButton").addEventListener("click", checkFiles);
    messageHandler();
}

function checkFiles(e){
    if (files.files.length === 0 || files.files.length == 0) {
        let parent = document.getElementById("title");
        let child = document.createElement("div");

        if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
        }

        child.setAttribute("class", "error");
        child.innerHTML = "Wybierz plik do dodania!";
        parent.appendChild(child);

        e.preventDefault()
    }
}

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
        out.innerHTML = out.innerHTML + '<div class ="warning">Publikacja o tytule "' + e.data + '" została dodana w innej przeglądarce. Odśwież listę, aby ją zobaczyć.</div>';
    };
}