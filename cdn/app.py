import jwt
import json
import os
import redis
import redisHandler
from flask import Flask
from flask import request
from flask import make_response
from flask import send_file
from dotenv import load_dotenv
from os import getenv
import shutil

load_dotenv(verbose=True)

app = Flask(__name__)
JWT_SECRET = getenv('JWT_SECRET')

redis = redis.Redis(host="redis", port="6379", decode_responses=True)
redisConn = redisHandler.RedisHandler(redis)


@app.route('/dellist/<uid>/<pid>', methods=['POST'])
def pubDel(uid, pid):
    token = request.args.get('token')
    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'delete':
        return make_response("invalidTokenPayload", 403)
    publication = json.loads(redisConn.getData(uid, pid))
    oldGuests = json.loads(publication).get('share')
    for user in oldGuests:
        redisConn.removeAccess(user, uid, pid)
    redisConn.deleteData(uid, pid)
    if os.path.exists('/tmp/' + uid + '/' + pid):
        shutil.rmtree('/tmp/' + uid + '/' + pid)
    return make_response("deletedPublication", 200)


@app.route('/list/<uid>/<pid>', methods=['GET'])
def pubDetails(uid, pid):
    token = request.args.get('token')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return make_response("invalidTokenPayload", 403)
    listOfFiles = []
    if os.path.exists("/tmp/" + uid + "/" + pid):
        listOfFiles = os.listdir("/tmp/" + uid + "/" + pid)
    publication = redisConn.getData(uid, pid)
    if publication is None or publication == "null":
        return make_response("PublicationNotFound", 404)
    publication = json.loads(publication)
    listOfFiles = json.dumps(listOfFiles)
    detailData = {'details': publication, 'files': listOfFiles}
    detailData = json.dumps(detailData)
    return detailData


@app.route('/filesshare/<uid>/<spid>/<suid>', methods=['GET'])
def fileShareDownload(uid, spid, suid):
    token = request.args.get('token')
    filename = request.args.get('filename')

    if uid is None or len(uid) == 0 or spid is None or len(spid) == 0 or suid is None or len(suid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'download':
        return make_response("invalidTokenPayload", 403)

    publication = json.loads(redisConn.getData(suid, spid))
    guests = json.loads(publication).get('share')
    try:
        guests.index(payload.get('uid'))
    except:
        return make_response("invalidTokenPayload", 403)

    if os.path.isfile("/tmp/" + suid + "/" + spid + "/" + filename) is False:
        return make_response("fileNotFound", 404)
    file = "/tmp/" + suid + "/" + spid + "/" + filename
    file = open(file, 'rb')
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/listshare/<uid>/<spid>/<suid>', methods=['GET'])
def pubDetailsShare(uid, spid, suid):
    token = request.args.get('token')

    if uid is None or len(uid) == 0 or spid is None or len(spid) == 0 or suid is None or len(suid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return make_response("invalidTokenPayload", 403)

    publication = json.loads(redisConn.getData(suid, spid))
    guests = json.loads(publication).get('share')
    try:
        guests.index(payload.get('uid'))
    except:
        return make_response("invalidTokenPayload", 403)

    listOfFiles = []
    if os.path.exists("/tmp/" + suid + "/" + spid):
        listOfFiles = os.listdir("/tmp/" + suid + "/" + spid)
    publication = redisConn.getData(suid, spid)
    publication = json.loads(publication)
    listOfFiles = json.dumps(listOfFiles)
    detailData = {'details': publication, 'files': listOfFiles}
    detailData = json.dumps(detailData)
    return detailData


@app.route('/list/<uid>', methods=['GET'])
def pubList(uid):
    token = request.args.get('token')

    if uid is None or len(uid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return make_response("invalidTokenPayload", 403)
    listOfPublications = redisConn.getList(uid)
    return json.dumps(listOfPublications)


@app.route('/list', methods=['POST'])
def pubUpload():
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
    share = request.form.getlist('share')
    uid = request.form.get('uid')
    files = request.files.getlist('files')

    if uid is None or len(uid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return make_response("invalidTokenPayload", 403)
    pid = str(redisConn.addData(uid, author, publisher, title, date, share))
    if files is not None:
        if not os.path.exists('/tmp/' + uid):
            os.mkdir('/tmp/' + uid)
        if not os.path.exists('/tmp/' + uid + '/' + pid):
            os.mkdir('/tmp/' + uid + '/' + pid)
        for file in files:
            if file.filename != "":
                file.save('/tmp/' + uid + '/' + pid + '/' + file.filename)
                file.close()
    redisConn.postMessage(uid, title)
    for user in share:
        redisConn.setAccess(user, uid, pid)
    return make_response("uploadedPublication", 200)


@app.route('/updlist/<uid>/<pid>', methods=['POST'])
def pubUpd(uid, pid):
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
    share = request.form.getlist('share')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'edit':
        return make_response("invalidTokenPayload", 403)
    publication = json.loads(redisConn.getData(uid, pid))
    oldGuests = json.loads(publication).get('share')
    redisConn.updateData(pid, uid, author, publisher, title, date, share)
    for user in oldGuests:
        redisConn.removeAccess(user, uid, pid)
    for user in share:
        redisConn.setAccess(user, uid, pid)
    return make_response("updatedPublication", 200)


@app.route('/files/<uid>/<pid>', methods=['GET'])
def fileDownload(uid, pid):
    token = request.args.get('token')
    filename = request.args.get('filename')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'download':
        return make_response("invalidTokenPayload", 403)
    if os.path.isfile("/tmp/" + uid + "/" + pid + "/" + filename) is False:
        return make_response("fileNotFound", 404)
    file = "/tmp/" + uid + "/" + pid + "/" + filename
    file = open(file, 'rb')
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/files/<uid>/<pid>', methods=['POST'])
def fileUpload(uid, pid):
    token = request.args.get('token')
    files = request.files.getlist('files')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return make_response("invalidTokenPayload", 403)

    if files is not None:
        if not os.path.exists('/tmp/' + uid):
            os.mkdir('/tmp/' + uid)
        if not os.path.exists('/tmp/' + uid + '/' + pid):
            os.mkdir('/tmp/' + uid + '/' + pid)
        for file in files:
            if file.filename != "":
                file.save('/tmp/' + uid + '/' + pid + '/' + file.filename)
                file.close()
    return make_response("uploadedFile", 200)


@app.route('/delfiles/<uid>/<pid>', methods=['POST'])
def fileDel(uid, pid):
    token = request.args.get('token')
    filename = request.args.get('filename')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'delete':
        return make_response("invalidTokenPayload", 403)
    if os.path.isfile("/tmp/" + uid + "/" + pid + "/" + filename) is False:
        return make_response("fileNotFound", 404)
    file = "/tmp/" + uid + "/" + pid + "/" + filename
    os.remove(file)
    return make_response("deletedFile", 200)


def valid(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        app.logger.error(str(e))
        return False
    return True
