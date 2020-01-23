window.addEventListener("load", afterLoad);
var login, password, passwordRepeat;

function afterLoad() {
    let button = document.getElementById("registerButton");
    button.addEventListener("click", e => register(e));
    login = document.getElementById("login");
    login.addEventListener("keyup", checkLoginAvailable);
    password = document.getElementById("password");
    passwordRepeat = document.getElementById("passwordRepeat");
}

function checkLoginAvailable() {
    //TODO może jakieś regexy?
    //TODO jakieś czasy narzucić + komunikat?
    if (login.value.length >= 3) {
        let xhttp = new XMLHttpRequest();
        xhttp.overrideMimeType('text/xml');
        xhttp.onreadystatechange = function () {
            if (this.status === 200 && this.readyState === 4) {
                document.getElementById("login").style.background = "red";
            } else {
                document.getElementById("login").style.background = "green";
            }
        };
        xhttp.open("GET", "/checklogin/" + login.value, true);
        xhttp.send();
    }
    else
    {
        document.getElementById("login").style.background = null;
    }
}

function checkPasswordComplex() {
}



function register(e) {
    e.preventDefault();
}