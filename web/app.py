from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from flask import session as se
from dotenv import load_dotenv
from os import getenv
import datetime
import redisHandler
import sessionHandler
import redis
import jwt
import requests
import json

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


@app.route('/details')
def details():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')

    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            detailData = json.loads(requests.get("http://cdn:5000/list/" + uid + "/" + pid + "?token=" + token).content)
            downloadToken = createDownloadToken(uid).decode('utf-8')
            deleteToken = createDeleteToken(uid).decode('utf-8')
            uploadToken = createUploadToken(uid).decode('utf-8')
            listToken = createListToken(uid).decode('utf-8')
            publication = detailData.get('details')
            files = detailData.get('files')
            #TODO ten listToken to tak 2/10
            return render_template("details.html", uid=uid, downloadToken=downloadToken, deleteToken=deleteToken, listToken=listToken, uploadToken=uploadToken,
                                   publication=json.loads(publication), files=json.loads(files))
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")

@app.route('/edit')
def edit():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')
    session_id = request.cookies.get('session_id')
    if session_id:
        if session.checkSession(session_id):
            detailData = json.loads(requests.get("http://cdn:5000/list/" + uid + "/" + pid + "?token=" + token).content)
            editToken = createEditToken(uid).decode('utf-8')
            publication = detailData.get('details')
            return render_template("edit.html", uid=uid, editToken=editToken, pid=pid, publication=json.loads(publication))
        else:
            response = redirect("/login")
            response.set_cookie("session_id", "INVALIDATE", max_age=INVALIDATE)
            return response
    return redirect("/login")


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is not "" and password is not "":
        response = make_response('', 303)
        if redisConn.checkUser(username, password) is True:
            session_id = session.createSession(username)
            response.set_cookie("session_id", session_id, max_age=SESSION_TIME, httponly=True)
            response.headers["Location"] = "/index"
        else:
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
def addFile():
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

def createEditToken(uid):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_SESSION_TIME)
    return jwt.encode({"iss": "web.company.com", "exp": exp, "uid": uid, "action": "edit"}, JWT_SECRET, "HS256")


def redirect(location):
    response = make_response('', 303)
    response.headers["Location"] = location
    return response


def createFileMessage(err):
    message = ''
    if err == "no file provided":
        message = f'<div class="error">Nie wybrano pliku!</div>'
    elif err == "missing file":
        message = f'<div class="error">Wybrany plik nie istnieje!</div>'
    elif err == "missing publication":
        message = f'<div class="error">Wybrana publikacja nie istnieje!</div>'
    elif err == "missing uid":
        message = f'<div class="error">Nieprawidłowy użytkownik!</div>'
    elif err == "no token provided":
        message = f'<div class="error">Brak tokenu - odśwież stronę!</div>'
    elif err == "invalid token":
        message = f'<div class="error">Token nieprawidłowy lub ważność wygasła!</div>'
    elif err == "invalid token payload":
        message = f'<div class="error">Niezgodność tokenu z użytkonikiem i/lub akcją!</div>'
    elif err == "deleted publication":
        message = f'<div class="info">Publikację usunięto!</div>'
    elif err == "ok publication":
        message = f'<div class="info">Publikację dodano!</div>'
    elif err == "ok file":
        message = f'<div class="info">Plik dodano do publikacji!</div>'
    elif err == "ok publication updated":
        message = f'<div class="info">Publikacja zaktualizowana!</div>'
    return message
