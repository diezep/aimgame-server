#/usr/bin/python3
import os
import random 

from flask import Flask, request, render_template
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from bson.json_util import dumps
from pymongo import MongoClient
from flask_cors import CORS
import threading 

from models.room import Room 
from utils import generate_code

from dotenv import load_dotenv
load_dotenv()

# import eventlet
# eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


if os.getenv('MONGODB_URI') is not None:
    MONGODB_URI = os.environ['MONGODB_URI']
    mongo = MongoClient(MONGODB_URI)
else:
    mongo = MongoClient()


rooms = Room(mongo)

active_rooms = []
active_hits = []

def generate_point(room):
    print('Generated point thread init.')
    while room in active_rooms:
        nPoint = generate_code(10)
        active_hits.append(nPoint)
        cords = {
            'x' : random.randint(1,100),
            'y' : random.randint(1,100),
        }
        point = {'hitCode':nPoint, 'cords':cords}
        
        print(f'Generated point', room, '@', point)
        socketio.emit('point', dumps(point), room=room, namespace='/game')
        socketio.sleep(1)


@socketio.on('connect', namespace='/game')
def connect_game():
    print('New user connected to sockets in Game page.')


@socketio.on('disconnect', namespace='/game')
def disconnected_game():
    print('User disconnected from sockets in Game page.')
    _room = rooms.leave(request.sid)
    
    if _room != None :
        if len(_room['players']) == 0 and active_rooms.count(_room['code']) == 1:
            print('Removing inactive room.')
            active_rooms.remove(_room['code'])

        emit('leave', dumps({'sid':request.sid}), room=_room['code'], broadcast=True, namespace='/game', include_self=False)


@app.route('/create', methods=['POST'])
def create(): 

    _name = request.form['name']
    _room = rooms.create(_name)
    
    active_rooms.append(_room['code'])
    
    socketio.start_background_task(generate_point, _room['code'])
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
    if len(_room['players'])==0:
        active_rooms.remove(_room['code'])
    leave_room(room)

    # Message to all users..
    emit('leave', dumps({'sid':request.sid}), room=room, broadcast=True, namespace='/game', include_self=False)


@socketio.on('point', namespace='/game')
def on_hit_game(data):

    room = data['room']
    hitCode = data['code']
    sid = request.sid;

    if hitCode in active_hits:
        print('Hit #', hitCode, ' in room @', room)

        emit('hit', dumps({'hitCode': hitCode, 'sid':sid}), room=room, namespace="/game")  
        
        active_hits.remove(hitCode)
        rooms.hit(room, sid)
        

if __name__ == "__main__":
    socketio.run(app, port=int(os.environ.get('PORT', '5000')))
    