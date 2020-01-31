window.addEventListener("load", afterLoad);
var login, password, passwordRepeat, loginCorrect = false;

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

function checkLoginAvailable() {
    let regex = /^[a-zA-Z0-9]*$/;
    if (document.getElementById("labelLogin").childElementCount > 0) {
        document.getElementById("labelLogin").removeChild(document.getElementById("loginAvailable"));
    }
    let parent = document.getElementById("labelLogin");
    let child = document.createElement("div");
    child.setAttribute("id", "loginAvailable");
    if (login.value.length <= 20 && login.value.length >= 3 && login.value.match(regex)) {
        let xhttp = new XMLHttpRequest();
        xhttp.overrideMimeType('text/xml');
        xhttp.onreadystatechange = function () {
            if (this.status === 200) {
                child.innerHTML = "Login zajęty!";
                parent.appendChild(child);
                document.getElementById("login").style.background = "red";
                loginCorrect = false;
            } else if (this.status === 404) {
                child.innerHTML = "Login dostępny!";
                parent.appendChild(child);
                document.getElementById("login").style.background = "greenyellow";
                loginCorrect = true;
            }
        };
        xhttp.open("GET", "/checklogin/" + login.value, true);
        xhttp.send();
    } else {
        child.innerHTML = "Login nie spełnia wymogów - co  najmniej 3, a co najwyżej 20 znaków ze zbioru [a-zA-Z0-9]!";
        parent.appendChild(child);
        document.getElementById("login").style.background = "red";
        loginCorrect = false;
    }
}

function checkPassword() {
    if (document.getElementById("labelPassword").childElementCount > 0) {
        document.getElementById("labelPassword").removeChild(document.getElementById("passwordComplex"));
    }
    if (document.getElementById("labelRepeatPassword").childElementCount > 0) {
        document.getElementById("labelRepeatPassword").removeChild(document.getElementById("passwordEquality"));
    }
    if (checkPasswordComplex() && checkPasswordEquality()) {
        return true
    }
    return false;
}

function checkPasswordEquality() {
    if (passwordRepeat.value === password.value) {
        document.getElementById("passwordRepeat").style.background = null;
        return true;
    }
    document.getElementById("passwordRepeat").style.background = "red";

    let parent = document.getElementById("labelRepeatPassword");
    let child = document.createElement("div");
    child.setAttribute("id", "passwordEquality");
    child.innerHTML = "Wpisane hasła są różne";
    parent.appendChild(child);

    return false;
}

function checkPasswordComplex() {
    let regex = /^[a-zA-Z0-9!@#$%^&]*$/;
    if (password.value.match(regex) && password.value.length >= 6 && password.value.length <= 30) {
        let countArray = {}, letterAmount = 0, result = 0;
        for (let letter of password.value.split('')) {
            countArray[letter] ? countArray[letter]++ : countArray[letter] = 1;
            letterAmount++;
        }

        for (let letter in countArray) {
            result += countArray[letter] / letterAmount * Math.log2(countArray[letter] / letterAmount)
        }
        result *= -1;
        console.log(result);
        if (result < 2) {
            passwordNotification(2)
        } else if (result >= 2 && result < 3) {
            passwordNotification(1)
        } else {
            passwordNotification(0)
        }
        return result >= 2;
    }
    passwordNotification(3);
    return false;
}

function passwordNotification(code) {
    let parent = document.getElementById("labelPassword");
    let child = document.createElement("div");
    child.setAttribute("id", "passwordComplex");
    switch (code) {
        case 3:
            child.innerHTML = "Hasło nie spełnia wymogów - co najmniej 6, a co najwyżej 30 znaków ze zbioru [a-zA-Z0-9!@#$%^&]";
            document.getElementById("password").style.background = "red";
            break;
        case 2:
            child.innerHTML = "Słabe hasło - wpisz mocniejsze";
            document.getElementById("password").style.background = "red";
            break;
        case 1:
            child.innerHTML = "Średnie hasło";
            document.getElementById("password").style.background = "yellow";
            break;
        case 0:
            child.innerHTML = "Mocne hasło";
            document.getElementById("password").style.background = "greenyellow";
            break;
    }
    parent.appendChild(child);
}

function register(e) {
    if (loginCorrect === false || checkPassword() === false) {
        e.preventDefault();
        if (document.getElementById("title").childElementCount > 0) {
            document.getElementById("title").removeChild(document.getElementById("generalError"));
        }
        let parent = document.getElementById("title");
        let child = document.createElement("div");
        child.setAttribute("id", "generalError");
        child.innerHTML = "Nie wypełniono prawidłowo wszystkich pól!";
        child.style.color = "red";
        parent.appendChild(child);
    }
}