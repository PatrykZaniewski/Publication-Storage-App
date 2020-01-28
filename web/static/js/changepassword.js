window.addEventListener("load", afterLoad);
var newPassword, newPasswordRepeat, loginCorrect = false;
//TODO porobić regexy i zrobić callback
function afterLoad() {
    /*let button = document.getElementById("registerButton");
    button.addEventListener("click", e => register(e));
    oldPassword = document.getElementById("oldPassword");
    oldPassword.addEventListener("keyup", checkPassword);
    newPassword = document.getElementById("newPassword");
    newPassword.addEventListener("keyup", checkPassword);
    newPasswordRepeat = document.getElementById("newPasswordRepeat");
    newPasswordRepeat.addEventListener("keyup", checkPassword);*/
    messageHandler();
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