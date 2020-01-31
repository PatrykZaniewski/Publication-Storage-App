window.addEventListener("load", afterLoad);
var sendButton, login, password;

function afterLoad() {
    login = document.getElementById("login");
    password = document.getElementById("password");
    sendButton = document.getElementById("sendButton");
    sendButton.addEventListener("click", checkData);
}

function checkInput() {

    let regexLogin = /^[a-zA-Z0-9]*$/;
    let regexPassword = /^[a-zA-Z0-9!@#$%^&]*$/;
    if (login.value.match(regexLogin) && password.value.match(regexPassword) && login.value.length <= 20 && password.value.length <= 30) {
        return true;
    }
    messageLogin("INVALID");
    return false;

}

function checkData() {
    let inputs = document.querySelectorAll(".fieldInput");
    if (inputs[0].value.length !== 0 || inputs[1].value.length !== 0) {
        if (checkInput()) {
            return;
        }
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
    if (type === "EMPTY") {
        child.innerHTML = "<br>Wypełnij wszystkie pola!";
    } else if (type === "INVALID") {
        child.innerHTML = "<br>Nieprawidłowe znaki w polach logowania! Prawidłowe to [a-zA-Z0-9] dla loginu i [a-zA-Z0-9!@#$%^&] dla hasła!";
    }

    parent.appendChild(child);
}