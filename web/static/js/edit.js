window.addEventListener("load", afterLoad);
var author, title, publisher, date;

function afterLoad() {
    author = document.getElementById("author")
    title = document.getElementById("title")
    publisher = document.getElementById("publisher")
    date = document.getElementById("date")
    document.getElementById("submitButton").addEventListener("click", checkData)
}

function checkData(e){
    //TODO dorobic checki + wyswietlanie bledu i bedize git
    e.preventDefault()
}