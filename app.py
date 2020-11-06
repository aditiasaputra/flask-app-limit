import os
import sys
import time
import redis
from datetime import datetime

from flask import Flask, request
from flask.config import Config
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from http import HTTPStatus
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import (get_remote_address, get_ipaddr)
from flask.helpers import make_response
from flask.json import jsonify

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://" + \
    os.getenv('DB_HOST') + ":" + os.getenv('DB_PORT') + \
    "/" + os.getenv('DB_DATABASE')
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
cache = redis.Redis(host='127.0.0.1', port=6379)
jwt = JWTManager(app)
mongo = PyMongo(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
)


# Store hit count API

def get_hit_count():
    ip = str(get_remote_address())
    key = ip + ":" + \
        request.base_url + ":" + \
        str(datetime.today().hour) + ":" + str(datetime.today().minute)
    retries = 5
    while True:
        try:
            return cache.incr(key)
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

# Store info who use API


def store_limit(status):
    key = str(get_remote_address()) + ":" + \
        request.base_url + ":" + \
        str(datetime.today().hour) + ":" + str(datetime.today().minute)
    route_delimitter = " /" if request.base_url.split(
        "/")[-1] == "" else " /" + request.base_url.split("/")[-1]
    data = {
        'key': key,
        'info_ip': str(get_remote_address()) + " - " + datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        + " - " + request.method + " " + status + route_delimitter
    }
    limitcoll = mongo.db.limits.insert_one(data)
    return limitcoll


@app.route('/')
def home():
    count = get_hit_count()
    access_token = create_access_token(identity='Hello')
    store_limit(str(HTTPStatus.OK.value))
    # print(request.base_url.split('/')[-1])
    return make_response(jsonify({
        "hit_count": count,
        "message": "Hello world",
        "token": access_token,
        "IP_info": str(get_remote_address()) + " - " + datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        + " - " + request.method +
        " /" if request.base_url.split("/")[-1] == "" else "" +
        str(HTTPStatus.OK.value)
    }), 200)


@app.route('/api', methods=['GET'])
@limiter.limit("3/day")
@jwt_required
def index():
    count = get_hit_count()
    current_user = get_jwt_identity()
    store_limit(str(HTTPStatus.OK.value))
    return make_response(jsonify({
        "current_user": current_user,
        "hit_count": count,
        "message": "Hello world from api",
        "IP_info": str(get_remote_address()) + " - " + datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        + " - " + request.method + " /" +
        request.base_url.split("/")[-1] + " " + str(HTTPStatus.OK.value)
    }), 200)


@app.errorhandler(429)
def ratelimit_handler(e):
    count = get_hit_count()
    store_limit(str(HTTPStatus.TOO_MANY_REQUESTS.value))
    return make_response(jsonify({
        "hit_count": count,
        "error": "Too much request! Rate limit exceeded %s" % e.description,
        "code_status": str(HTTPStatus.TOO_MANY_REQUESTS.value)
    }), 429)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
