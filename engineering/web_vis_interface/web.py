#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Project: detectron2
@Author: sol@JinGroup
@File: web.py
@Time: 10/28/19 11:37 AM
@E-mail: hesuozhang@gmail.com
'''

from __future__ import division, unicode_literals
from flask import request, Flask, render_template
import json
from flask import Flask
import os
from infer import Infer


def get_receive_data():
    if request.headers['Content-Type'] == 'text/plain':
        receive_data = request.data.decode('utf-8')
    elif request.headers['Content-Type'] == 'application/json':
        receive_data = request.json
    elif request.headers['Content-Type'] == 'application/octet-stream':
        receive_data = request.data
    else:
        receive_data = "415 Unsupported Media Type;{}".format(
            request.headers['Content-Type'])
    return receive_data


def create_app(instance_path=None):
    # create and configure the app
    app = Flask(__name__, instance_path=instance_path,
                instance_relative_config=True)
    app.config.from_pyfile("config.py", silent=True)
    app.config.from_envvar("APP_CONFIG_FILE", silent=True)
    My_infer = Infer()
    return app, My_infer


app, My_infer = create_app()


@app.route('/detect_api', methods=['POST', 'GET'])
def application():
    if request.method == 'POST':
        root = os.path.dirname(__file__)
        img = request.data
        path = os.path.join(root, "static/", "unload.png")
        with open(path, "wb") as f:
            f.write(img)
        try:
            res = My_infer.infer(path, None)
        except:
            res = json.dumps({"Error": "Found Error in the server, please try again later.", "code": 510})
        return res
    else:
        return render_template('upload.html')


def return_img_stream(img_local_path):
    import base64
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream)
    img_stream = img_stream.decode()
    return img_stream


@app.route('/upload_image', methods=['POST'])
def upload():
    root = os.path.dirname(__file__)
    img = request.files.get('photo')
    path = os.path.join(root, "static/")
    des = os.path.join(root, "vis/")
    file_path = path + img.filename
    des_path = des + img.filename
    img.save(file_path)
    My_infer.infer(file_path, des_path)

    img_stream = return_img_stream(des_path)
    return render_template('index.html', img_stream=img_stream)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
