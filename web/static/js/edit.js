window.addEventListener("load", afterLoad);
var author, title, publisher, date;

function afterLoad() {
    author = document.getElementById("author");
    title = document.getElementById("pubTitle");
    publisher = document.getElementById("publisher");
    date = document.getElementById("publishDate");
    document.getElementById("submitButton").addEventListener("click", checkData)
}

function checkData(e) {
    if (author.value == "" || title.value == "" || publisher.value == "" || date.value == "") {
        let parent = document.getElementById("title");
        let child = document.createElement("div");

        if (parent.childElementCount > 0) {
        parent.removeChild(parent.children[0]);
        }

        child.setAttribute("class", "error");
        child.innerHTML = "Wypełnij wszystkie pola!";
        parent.appendChild(child);

        e.preventDefault()
    }
}