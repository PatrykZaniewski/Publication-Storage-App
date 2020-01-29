window.addEventListener("load", afterLoad);
var sendButton, login, password;

function afterLoad() {
    login = document.getElementById("login");
    password = document.getElementById("password");
    sendButton = document.getElementById("sendButton");
    login.addEventListener("keyup", function(){checkInput("login")});
    password.addEventListener("keyup", function(){checkInput("password")});
    sendButton.addEventListener("click", checkData);
}

function checkInput(type) {
    if (type === "login") {
        let regex = /^[a-zA-Z0-9]*$/;
        if (login.value.match(regex) && login.value.length > 2) {
            return true;
        }
        return false;
    } else if (type === "password") {
        let regex = /^[a-zA-Z0-9!@#$%^&]*$/;
        if (password.value.match(regex) && login.value.length > 5) {
            return true;
        }
        return false;
    }

}

function checkData() {
    let inputs = document.querySelectorAll(".fieldInput");
    if (inputs[0].value.length !== 0 || inputs[1].value.length !== 0) {
        if (checkInput("login") && checkInput("password")) {
            return;
        }
        //TODO zle dane
        messageLogin("");
        event.preventDefault();
        return;
    }
    messageLogin("EMPTY");
    event.preventDefault();

}

function messageLogin(type) {
    let parent = document.getElementById("title");
    if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
    }
    let child = document.createElement("label");
    child.setAttribute("class", "error");
    child.innerHTML = "<br>Wypełnij wszystkie pola!";

    parent.appendChild(child);
}