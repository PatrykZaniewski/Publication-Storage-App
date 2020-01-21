window.addEventListener("load", afterLoad);
var login, password, passwordRepeat;

function afterLoad(){
    let button = document.getElementById("registerButton");
    button.addEventListener("click", register());
    login = document.getElementById("login");
    password = document.getElementById("password");
    passwordRepeat = document.getElementById("passwordRepeat");

}

function checkLogin()
{
    //TODO może jakieś regexy?
    if (login.length >= 3) {
        let xhttp = new XMLHttpRequest();
        xhttp.overrideMimeType('text/xml');
        xhttp.onreadystatechange = function () {
            if (this.status === 200 && this.readyState === 4) {
                document.getElementById("login").style.background = "red";
                addError("loginlength");
            } else {
                document.getElementById("login").style.background = null;
                removeError("login");
            }
        };
        xhttp.open("GET", "/checkLogin" + nick, true);
        xhttp.send();
    }
}

function register() {
    e.preventDefault();
}