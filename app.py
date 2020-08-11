#/usr/bin/python3

from flask import Flask, request, render_template
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from bson.json_util import dumps
from pymongo import MongoClient
from flask_cors import CORS


from models.room import Room 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

host = 'localhost'
port = 27017
mongo = MongoClient(host, port)

rooms = Room(mongo)


app.debug = False

active_rooms = []
active_hits = []

import time, threading
# def foo():
#     print(time.ctime())
#     threading.Timer(60, foo).start()

# foo()

# def logging(func):
#     def function():
#         print(func.__name__+" has called")
#         return func;

# @logging
# @app.route('/')
# def index():
    # return render_template('hello.html')

@socketio.on('connect', namespace='/game')
def connect_game():
    print('New user connected to sockets in Game page.')

@socketio.on('disconnect', namespace='/game')
def disconnected_game():
    print('User disconnected from sockets in Game page.')
    _room = rooms.leave(request.sid)

    # Message to all users..
    print(_room)
    if _room != None:
        emit('leave', dumps({'sid':request.sid}), room=_room['code'], broadcast=True, namespace='/game', include_self=False)


@app.route('/create', methods=['POST'])
def create(): 

    _name = request.form['name']
    _room = rooms.create(request.form)
    
    active_rooms.append(_room['code'])

    return dumps(_room)


@socketio.on('join', namespace='/game')
def on_join_game(data):
    room = data['code']
    name = data['name']

    _room = rooms.join(name, room, request.sid)

    # Message to user joined.
    emit('join', dumps(_room), broadcast=False)
   
    join_room(room)
    
    # Message to all users..
    emit('join',dumps({'name': name, 'score':0, 'sid':request.sid}), broadcast=True, include_self=False)

@socketio.on('leave', namespace='/game')
def on_leave_game(data):

    room = data['code']
    name = data['name']

    _room = rooms.leave(request.sid, room)
    
    leave_room(room)

    # Message to all users..
    emit('leave', dumps({'sid':request.sid}), room=room, broadcast=True, namespace='/game', include_self=False)


@socketio.on('hit', namespace='/game')
def on_hit_game(data):

    room = data['room']
    name = data['name']

    hit_code = data['hit']
    if hit_code in active_hits:
        active_hits.remove(hit_code)
        # score = rooms.hit(name, room)
        emit('hit', {'name':name, 'score':score}, room=room, namespace="/game")  
        

if __name__ == "__main__":
    socketio.run(app)
    # while True:
    #     time.sleep(1)
    #     if(active_rooms):
# if __name__ == '__main__':
#     eventlet.wsgi.server(eventlet.listen(('', 5000)), app)