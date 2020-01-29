window.addEventListener("load", afterLoad);
var newPassword, newPasswordRepeat, oldPassword;
//TODO porobić regexy i zrobić callback
function afterLoad() {
    let button = document.getElementById("changeButton");
    button.addEventListener("click", e => changePassword(e));
    oldPassword = document.getElementById("oldPassword");
    oldPassword.addEventListener("keyup", checkOldPassword);
    newPassword = document.getElementById("newPassword");
    newPassword.addEventListener("keyup", checkNewPassword);
    newPasswordRepeat = document.getElementById("newPasswordRepeat");
    newPasswordRepeat.addEventListener("keyup", checkNewPassword);
    messageHandler();
}

function changePassword(e) {
    if (checkOldPassword() === false || checkNewPassword() === false) {
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

function checkOldPassword(){
    if (document.getElementById("labelOldPassword").childElementCount > 0) {
        document.getElementById("labelOldPassword").removeChild(document.getElementById("oldPasswordCorrectness"));
            document.getElementById("oldPassword").style.background = null;

    }
    let regex = /^[a-zA-Z0-9!@#$%^&]*$/;
    if (oldPassword.value.match(regex) && oldPassword.value.length >= 6) {
        return true;
    }
    let parent = document.getElementById("labelOldPassword");
    let child = document.createElement("div");
    child.setAttribute("id", "oldPasswordCorrectness");
    child.innerHTML = "Stare hasło nie spełnia wymogów - co najmniej 6 znaków ze zbioru [a-zA-Z0-9!@#$%^&]";
    document.getElementById("oldPassword").style.background = "red";
    parent.appendChild(child);
    return false;
}

function checkNewPassword() {
    if (document.getElementById("labelNewPassword").childElementCount > 0) {
        document.getElementById("labelNewPassword").removeChild(document.getElementById("newPasswordComplex"));
    }
    if (document.getElementById("labelNewPasswordRepeat").childElementCount > 0) {
        document.getElementById("labelNewPasswordRepeat").removeChild(document.getElementById("passwordEquality"));
    }
    if (checkNewPasswordComplex() && checkNewPasswordEquality()) {
        return true
    }
    return false;
}

function checkNewPasswordEquality() {
    if (newPasswordRepeat.value === newPassword.value) {
        document.getElementById("newPasswordRepeat").style.background = null;
        return true;
    }
    document.getElementById("newPasswordRepeat").style.background = "red";

    let parent = document.getElementById("labelNewPasswordRepeat");
    let child = document.createElement("div");
    child.setAttribute("id", "passwordEquality");
    child.innerHTML = "Wpisane hasła są różne";
    parent.appendChild(child);

    return false;
}

function checkNewPasswordComplex() {
    let regex = /^[a-zA-Z0-9!@#$%^&]*$/;
    if (newPassword.value.match(regex) && newPassword.value.length >= 6) {
        let countArray = {}, letterAmount = 0, result = 0;
        for (let letter of newPassword.value.split('')) {
            countArray[letter] ? countArray[letter]++ : countArray[letter] = 1;
            letterAmount++;
        }

        for (let letter in countArray) {
            result += countArray[letter] / letterAmount * Math.log2(countArray[letter] / letterAmount)
        }
        result *= -1;
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
    let parent = document.getElementById("labelNewPassword");
    let child = document.createElement("div");
    child.setAttribute("id", "newPasswordComplex");
    switch (code) {
        case 3:
            child.innerHTML = "Hasło nie spełnia wymogów - co najmniej 6 znaków ze zbioru [a-zA-Z0-9!@#$%^&]";
            document.getElementById("newPassword").style.background = "red";
            break;
        case 2:
            child.innerHTML = "Słabe hasło - wpisz mocniejsze";
            document.getElementById("newPassword").style.background = "red";
            break;
        case 1:
            child.innerHTML = "Średnie hasło";
            document.getElementById("newPassword").style.background = "yellow";
            break;
        case 0:
            child.innerHTML = "Mocne hasło";
            document.getElementById("newPassword").style.background = "greenyellow";
            break;
    }
    parent.appendChild(child);
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