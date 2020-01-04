window.addEventListener("load", afterLoad);
var files

function afterLoad() {
    files = document.getElementById("files");
    document.getElementById("submitButton").addEventListener("click", checkFiles)
}

function checkFiles(e){
    if (files.files.length === 0 || files.files.length == 0) {
        let parent = document.getElementById("title");
        let child = document.createElement("div");

        if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
        }

        child.setAttribute("class", "error");
        child.innerHTML = "Wybierz plik do dodania!";
        parent.appendChild(child);

        e.preventDefault()
    }
}