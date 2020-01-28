window.addEventListener("load", afterLoad);
var sendButton;

function afterLoad() {
    sendButton = document.getElementById("sendButton")
    sendButton.addEventListener("click", checkData);
}

function checkData() {
    let inputs = document.querySelectorAll(".fieldInput");
    if (inputs[0].value.length === 0 || inputs[1].value.length === 0) {
        messageLogin("EMPTY");
        return null;
    }
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.status === 200) {
            window.location.href = "https://web.company.com/index";
        } else if (this.status === 404) {
            messageLogin("INVALIDATE")
        }
        else if (this.status === 400){
            messageLogin("BADDATA")
        }
        else {
            messageLogin("OTHER")
        }
    };

    xhttp.open("POST", "auth", false);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({"username": inputs[0].value, "password": inputs[1].value}));
}

function messageLogin(type) {
    let parent = document.getElementById("title");
    if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
    }
    let child = document.createElement("label");
    switch (type) {
        case "EMPTY":
            child.setAttribute("class", "error");
            child.innerHTML = "<br>Wypełnij wszystkie pola!";
            break;
        case "INVALIDATE":
            child.setAttribute("class", "error");
            child.innerHTML = "<br>Wprowadzono nieprawidłowy login i/lub hasło!";
            break;
        case "OTHER":
            child.setAttribute("class", "error");
            child.innerHTML = "<br>Wystąpił błąd logowania! Spróbuj później.";
            break;
    }
    parent.appendChild(child);
}