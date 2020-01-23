window.addEventListener("load", afterLoad);
var login, password, passwordRepeat;

function afterLoad() {
    let button = document.getElementById("registerButton");
    button.addEventListener("click", e => register(e));
    login = document.getElementById("login");
    login.addEventListener("keyup", checkLoginAvailable);
    password = document.getElementById("password");
    password.addEventListener("keyup", checkPassword);
    passwordRepeat = document.getElementById("passwordRepeat");
    passwordRepeat.addEventListener("keyup", checkPassword);
}
//TODO entropia
//TODO sprawdzanie 2 hasel

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
                document.getElementById("login").style.background = "greenyellow";
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

function checkPassword(){
    console.log(checkPasswordEquality(), " ", checkPasswordEquality());
    if (checkPasswordComplex() && checkPasswordEquality()){
        //document.getElementById("passwordRepeat").style.background = "greenyellow";
        //document.getElementById("password").style.background = "greenyellow";
    }
}

function checkPasswordEquality(){
    if (passwordRepeat.value === password.value){
        document.getElementById("passwordRepeat").style.background = null;
        return true;
    }
    document.getElementById("passwordRepeat").style.background = "red";
    document.getElementById("password").style.background = "red";
    return false;
}

function checkPasswordComplex() {
    let countArray = {}, letterAmount = 0, result = 0;
    for (let letter of password.value.split('')){
        countArray[letter] ? countArray[letter]++ : countArray[letter] = 1;
        letterAmount++;
    }

    for (let letter in countArray)
    {
        result += countArray[letter]/letterAmount * Math.log2(countArray[letter]/letterAmount)
    }
    result *= -1;
    if(result < 2)
    {
        document.getElementById("password").style.background = "red";
    }
    else if(result >= 2 && result < 3){
        document.getElementById("password").style.background = "yellow";
    }
    else
    {
        document.getElementById("password").style.background = "greenyellow";
    }
    return result >= 2;
}



function register(e) {
    e.preventDefault();
}