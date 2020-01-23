from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from flask import session as se
from flask import Response
from dotenv import load_dotenv
from os import getenv
import datetime
import redisHandler
import sessionHandler
import redis
import jwt
import requests
import json
import hashlib
import os

load_dotenv(verbose=True)

app = Flask(__name__)
app.secret_key = "super secret key"
SESSION_TIME = int(getenv("SESSION_TIME"))
JWT_SESSION_TIME = int(getenv('JWT_SESSION_TIME'))
JWT_SECRET = getenv("JWT_SECRET")
INVALIDATE = -1

redis = redis.Redis(host="redis", port="6379", decode_responses=True)
redisConn = redisHandler.RedisHandler(redis)
redisConn.initUser()

session = sessionHandler.SessionHandler(redis)


@app.route('/')
def index():
    redisConn.checkLogin("dsadasd")
    redisConn.checkLogin("test")
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return redirect("/login")
    return redirect("/index")


@app.route('/login', methods=['GET'])
def login():
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            return redirect("/index")
    return render_template("login.html")


@app.route('/index')
def welcome():
    err = se.get('err')
    se['err'] = ''
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            message = createFileMessage(err)
            uid = session.getNicknameSession(session_id)
            listToken = createListToken(uid).decode('utf-8')
            listOfPublications = json.loads(requests.get("http://cdn:5000/list/" + uid + "?token=" + listToken).content)
            return render_template("index.html", uid=uid, listToken=listToken,
                                   listOfPublications=listOfPublications, message=message)
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")

@app.route('/stream')
def stream():
    name = session.getNicknameSession(request.cookies.get('session_id'))
    def event_stream(name):
        pubsub = redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(name)
        for message in pubsub.listen():
            yield 'data: %s\n\n' % message['data']
    return Response(event_stream(name), mimetype="text/event-stream")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/checklogin/<login>')
def checkLogin(login):
    print("XDDDDDD", flush=True)
    if redisConn.checkLogin(login):
        return make_response("Login exists", 200)
    return make_response("Login free", 404)


@app.route('/registeruser')
def checkLogin(login):
    #TODO konieczne sprawdzanie loginu raz jeszcze !!!
    print("XDDDDDD", flush=True)
    if redisConn.checkLogin(login):
        return make_response("Login exists", 200)
    return make_response("Login free", 404)


@app.route('/details')
def detailsPublication():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')

    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            req = requests.get("http://cdn:5000/list/" + uid + "/" + pid + "?token=" + token)
            if req.status_code != requests.codes.ok:
                return redirectCallback(req.text)
            detailData = json.loads(req.content)
            downloadToken = createDownloadToken(uid).decode('utf-8')
            deleteToken = createDeleteToken(uid).decode('utf-8')
            uploadToken = createUploadToken(uid).decode('utf-8')
            listToken = createListToken(uid).decode('utf-8')
            publication = detailData.get('details')
            files = detailData.get('files')
            return render_template("details.html", uid=uid, downloadToken=downloadToken, deleteToken=deleteToken,
                                   listToken=listToken, uploadToken=uploadToken,
                                   publication=json.loads(publication), files=json.loads(files))
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")


@app.route('/edit')
def editPublication():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            req = requests.get("http://cdn:5000/list/" + uid + "/" + pid + "?token=" + token)
            if req.status_code != requests.codes.ok:
                return redirectCallback(req.text)
            detailData = json.loads(req.content)
            editToken = createEditToken(uid).decode('utf-8')
            publication = detailData.get('details')
            return render_template("edit.html", uid=uid, editToken=editToken, pid=pid,
                                   publication=json.loads(publication))
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")


@app.route('/editpublication', methods=['POST'])
def editPublicationExecutive():
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
    pid = request.form.get('pid')
    uid = request.form.get('uid')

    objToSend = {'author': author, 'publisher': publisher, 'title': title, 'publishDate': date, 'uid': uid,
                 'token': token}

    req = requests.post("http://cdn:5000/updlist/" + uid + "/" + pid, data=objToSend)

    return redirectCallback(req.text)


@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data['username']
    password = data['password']
    if username is not "" and password is not "":
        if redisConn.login(username, password) is True:
            response = make_response('', 200)
            session_id = session.createSession(username)
            response.set_cookie("session_id", session_id, max_age=SESSION_TIME, httponly=True, secure=True)
        else:
            response = make_response('', 404)
            response.set_cookie("session_id", "INVALIDATE", max_age=1)
            response.headers["Location"] = "/login"
        return response
    return redirect("/login")


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        session.deleteSession(session_id)
        response = redirect("/login")
        response.set_cookie("session_id", "LOGGED_OUT", max_age=1)
        return response
    return redirect("/login")


@app.route('/add')
def addPublication():
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            uid = session.getNicknameSession(session_id)
            uploadToken = createUploadToken(uid).decode('utf-8')
            return render_template("add.html", uid=uid, uploadToken=uploadToken)
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")


@app.route('/addfiles', methods=['POST'])
def addFilesExecutive():
    token = request.form.get('token')
    uid = request.form.get('uid')
    pid = request.form.get('pid')
    files = request.files.getlist('files')

    files = [('files', (f.filename, f.read())) for f in files]

    req = requests.post("http://cdn:5000/files/" + uid + "/" + pid + "?token=" + token, files=files)
    return redirectCallback(req.text)


@app.route('/addpublication', methods=['POST'])
def addPubExecutive():
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
    uid = request.form.get('uid')
    files = request.files.getlist('files')

    objToSend = {'author': author, 'publisher': publisher, 'title': title, 'publishDate': date, 'uid': uid,
                 'token': token}
    files = [('files', (f.filename, f.read())) for f in files]

    req = requests.post("http://cdn:5000/list", data=objToSend, files=files)
    return redirectCallback(req.text)


@app.route('/deletepublication', methods=['POST'])
def delPubExecutive():
    token = request.form.get('token')
    uid = request.form.get('uid')
    pid = request.form.get('pid')

    req = requests.post("http://cdn:5000/dellist/" + uid + "/" + pid + "?token=" + token)
    return redirectCallback(req.text)


@app.route('/deletefile', methods=['POST'])
def delFileExecutive():
    token = request.form.get('token')
    uid = request.form.get('uid')
    pid = request.form.get('pid')
    filename = request.form.get('filename')

    req = requests.post("http://cdn:5000/delfiles/" + uid + "/" + pid + "?token=" + token + "&filename=" + filename)
    return redirectCallback(req.text)


def redirectCallback(error):
    response = make_response("", 303)
    response.headers["Location"] = "https://web.company.com/callback?error=" + error
    response.headers["Content-Type"] = "multipart/form-data"
    return response


@app.route('/callback')
def callback():
    session_id = request.cookies.get('session_id')
    err = request.args.get('error')
    if session_id:
        if session.checkSession(session_id):
            se['err'] = err

    return redirect('/login')


def createDownloadToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "download"}, JWT_SECRET, "HS256")


def createUploadToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "upload"}, JWT_SECRET, "HS256")


def createListToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "list"}, JWT_SECRET, "HS256")


def createDeleteToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "delete"}, JWT_SECRET, "HS256")

#TODO dodac do tokenow id plikow
def createEditToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "edit"}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response


def createFileMessage(err):
    message = ''
    if err == "fileNotFound":
        message = f'<div class="error">Wybrany plik nie istnieje!</div>'
    elif err == "noCredentials":
        message = f'<div class="error">Nieprawidłowe dane użytkownika/publikacji!</div>'
    elif err == "noTokenProvided":
        message = f'<div class="error">Brak tokenu - odśwież stronę!</div>'
    elif err == "invalidToken":
        message = f'<div class="error">Token nieprawidłowy lub ważność wygasła!</div>'
    elif err == "invalidTokenPayload":
        message = f'<div class="error">Niezgodność tokenu z użytkownikiem i/lub akcją!</div>'
    elif err == "deletedPublication":
        message = f'<div class="info">Publikację usunięto!</div>'
    elif err == "uploadedPublication":
        message = f'<div class="info">Publikację dodano!</div>'
    elif err == "uploadedFile":
        message = f'<div class="info">Plik dodano do publikacji!</div>'
    elif err == "updatedPublication":
        message = f'<div class="info">Publikacja zaktualizowana!</div>'
    elif err == "deletedFile":
        message = f'<div class="info">Plik usunięto!</div>'
    return message
