window.addEventListener("load", afterLoad);
var author, title, publisher, date;

function afterLoad() {
    author = document.getElementById("author");
    title = document.getElementById("pubTitle");
    publisher = document.getElementById("publisher");
    date = document.getElementById("publishDate");
    document.getElementById("submitButton").addEventListener("click", checkData);
    messageHandler();
}

function checkData(e) {

    let regex = /^[A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ.,]*$/;
    if (author.value == "" || title.value == "" || publisher.value == "" || date.value == "") {
        let parent = document.getElementById("title");
        let child = document.createElement("div");

        if (parent.childElementCount > 0) {
            parent.removeChild(parent.children[0]);
        }

        child.setAttribute("class", "error");
        child.innerHTML = "Wypełnij wszystkie pola!";
        parent.appendChild(child);

        e.preventDefault();
        return;
    }
    if (!author.value.match(regex) || !title.value.match(regex) || !publisher.value.match(regex) || !author.value.length > 128 || title.value.length > 128 || publisher.value.length > 128)
    {
        let parent = document.getElementById("title");
        let child = document.createElement("div");

        if (parent.childElementCount > 0) {
            parent.removeChild(parent.children[0]);
        }

        child.setAttribute("class", "error");
        child.innerHTML = "Pola nie spełniają wymogów - co najmniej 1, a co najwyżej 128 znaków ze zbioru [A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]!";
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