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
    publication = redisConn.getData(uid, pid)
    return publication


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


@app.route('/publication', methods=['POST'])
def upload():
    t = request.form.get('token')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    title = request.form.get('title')
    date = request.form.get('publishDate')
    uid = request.form.get('uid')
    files = request.files.getlist('files')
    print(files, flush=True)

    if t is None:
        return redirect("no+token+provided")
    if not valid(t):
        return redirect("invalid+token")
    payload = jwt.decode(t, JWT_SECRET)
    if payload.get('uid') != uid or payload.get('action') != 'upload':
        return redirect("invalid+token+payload")
    # TODO zrobic sprawdzanie czy takiego nie ma
    pubID = str(redisConn.addData(uid, author, publisher, title, date))
    if files is not None:
        if not os.path.exists('/tmp/' + uid):
            os.mkdir('/tmp/' + uid)
        if not os.path.exists('/tmp/' + uid + '/' + pubID):
            os.mkdir('/tmp/' + uid + '/' + pubID)
        for file in files:
            if file.filename != "":
                file.save('/tmp/' + uid + '/' + pubID + '/' + file.filename)
                file.close()
    return redirect("ok+publication")


@app.route('/files', methods=['GET'])
def download():
    uid = request.args.get('uid')
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
    file = '/tmp/test/' + filename
    file = open(file, 'rb')
    return send_file(file, attachment_filename=filename, as_attachment=True)


@app.route('/delfiles', methods=['POST'])
def delete():
    uid = request.args.get('uid')
    token = request.args.get('token')
    filename = request.args.get('filename')

    if os.path.isfile("/tmp/" + uid + "/" + filename) is False:
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
    file = '/tmp/test/' + filename
    os.remove(file)
    return redirect("deleted")


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
