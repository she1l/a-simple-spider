#!/usr/bin/env python
# utf-8

from flask import Flask
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import redis

redis_host = '127.0.0.1'
redis_pass = '123456'
redis_db = 15
redis_port = 6379

tokens = {
    "123456": "prod",
    "123456": "dev"
}

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
CORS(app, supports_credentials=True)

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

@app.route('/')
def root():
    return '---'

@app.route('/api/<key>/<area>')
@auth.login_required
def api(key, area):
    client = redis.Redis(host=redis_host, port=redis_port, password=redis_pass, db=redis_db, decode_responses=True)
    if client.exists(str(key)) and client.hget(str(key), str(area)):
        response = client.hget(str(key), str(area))
        return response
    else:
        return '--- 参数错误 ---'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)


