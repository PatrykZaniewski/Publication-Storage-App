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
    hateoas = {"_links": {"self": {"href": "https://cdn.company.com/list/" + uid, "method": "GET"},
                          "details": {"href": "https://cdn.company.com/list/" + uid + "/0", "method": "GET"},
                          "addPub": {"href": "https://cdn.company.com/list", "method": "POST"},
                          "deletePub": {"href": "https://cdn.company.com/dellist/" + uid + "/0", "method": "POST"},
                          "updPub": {"href": "https://cdn.company.com/updlist/" + uid + "/0", "method": "POST"},
                          "getFiles": {"href": "https://cdn.company.com/files/" + uid + "/0", "method": "GET"}
                          }}
    listOfPublications.update(hateoas)
    return json.dumps(listOfPublications)


@app.route('/list', methods=['POST'])
def pubUpload():
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
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
    pid = str(redisConn.addData(uid, author, publisher, title, date))
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
    return make_response("uploadedPublication", 200)


@app.route('/updlist/<uid>/<pid>', methods=['POST'])
def pubUpd(uid, pid):
    token = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')

    if uid is None or len(uid) == 0 or pid is None or len(pid) == 0:
        return make_response("noCredentials", 404)
    if token is None:
        return make_response("noTokenProvided", 400)
    if not valid(token):
        return make_response("invalidToken", 401)
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'edit':
        return make_response("invalidTokenPayload", 403)
    redisConn.updateData(pid, uid, author, publisher, title, date)
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
