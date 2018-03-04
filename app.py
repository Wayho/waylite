# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import url_for
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)


################################################################
def Get_Domain():
	# 返回值可用与识别App
	# #domain和WORK_ID统一为一个标识符
	str_url =  url_for('index', _external=True)     #http://mlite101.leanapp.cn/
	arr_split = str_url.split('/')[2]                  #['http:', '', 'mlite101.leanapp.cn', '']
	Domain = arr_split.split('.')[0]                  #['mlite101', 'leanapp', 'cn']
	return Domain
################################################################

@app.route('/')
def index():
	print Get_Domain()
	return 'index'


@app.route('/time')
def time():
	return str(datetime.now())

@app.route('/heart')
def heart():
	return 'Heart'


@sockets.route('/echo')
def echo_socket(ws):
	while True:
		message = ws.receive()
		ws.send(message)
