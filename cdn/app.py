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
    #TODO zrobic usuwanie plikow od razu
    token = request.args.get('token')
    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if pid is None or len(pid) == 0:
        return redirect("missing+publication")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'delete':
        return redirect("invalid+token+payload")
    redisConn.deleteData(uid, pid)
    if os.path.exists('/tmp/' + uid + '/' + pid):
        shutil.rmtree('/tmp/' + uid + '/' + pid)
    return redirect('deleted+publication')


@app.route('/list/<uid>/<pid>', methods=['GET'])
def pubDetails(uid, pid):
    token = request.args.get('token')
    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if pid is None or len(pid) == 0:
        return redirect("missing+publication")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return redirect("invalid+token+payload")
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
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'list':
        return redirect("invalid+token+payload")
    listOfPublications = redisConn.getList(uid)
    return listOfPublications


@app.route('/list', methods=['POST'])
def pubUpload():
    #TODO z data jest jakis problem
    t = request.form.get('token')
    author = request.form.get('author', 'NN')
    publisher = request.form.get('publisher', 'NN')
    title = request.form.get('title', 'NN')
    date = request.form.get('publishDate', 'NN')
    uid = request.form.get('uid')
    files = request.files.getlist('files')

    if t is None:
        return redirect("no+token+provided")
    if not valid(t):
        return redirect("invalid+token")
    payload = jwt.decode(t, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return redirect("invalid+token+payload")
    # TODO zrobic sprawdzanie czy takiego nie ma
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
    return redirect("ok+publication")

@app.route('/updlist/<uid>/<pid>', methods=['POST'])
def pubUpd(uid, pid):
    t = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')

    if t is None:
        return redirect("no+token+provided")
    if not valid(t):
        return redirect("invalid+token")
    payload = jwt.decode(t, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'edit':
        return redirect("invalid+token+payload")
    redisConn.updateData(pid, uid, author, publisher, title, date)
    #TODO zmienic kod
    return redirect("ok+publication+updated")


@app.route('/files', methods=['GET'])
def fileDownload():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')
    filename = request.args.get('filename')

    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'download':
        return redirect("invalid+token+payload")
    file = "/tmp/" + uid + "/" + pid + "/" + filename
    file = open(file, 'rb')
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/files', methods=['POST'])
def fileUpload():
    pid = request.args.get('pid')
    token = request.args.get('token')
    uid = request.args.get('uid')
    files = request.files.getlist('files')

    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return redirect("invalid+token+payload")
    if files is not None:
        if not os.path.exists('/tmp/' + uid):
            os.mkdir('/tmp/' + uid)
        if not os.path.exists('/tmp/' + uid + '/' + pid):
            os.mkdir('/tmp/' + uid + '/' + pid)
        for file in files:
            if file.filename != "":
                file.save('/tmp/' + uid + '/' + pid + '/' + file.filename)
                file.close()
    return redirect("ok+file")


@app.route('/delfiles', methods=['POST'])
def fileDel():
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    token = request.args.get('token')
    filename = request.args.get('filename')

    if os.path.isfile("/tmp/" + uid + "/" + pid + "/" + filename) is False:
        return redirect("missing+file")
    if uid is None or len(uid) == 0:
        return redirect("missing+uid")
    if token is None:
        return redirect("no+token+provided")
    if not valid(token):
        return redirect("invalid+token")
    payload = jwt.decode(token, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'delete':
        return redirect("invalid+token+payload")
    file = "/tmp/" + uid + "/" + pid + "/" + filename
    os.remove(file)
    return redirect("deleted+file")


def valid(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        app.logger.error(str(e))
        return False
    return True


def redirect(error):
    response = make_response("", 303)
    response.headers["Location"] = "https://web.company.com/callback?error=" + error
    response.headers["Content-Type"] = "multipart/form-data"
    return response
