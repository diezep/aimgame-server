#/usr/bin/python3

from flask import Flask, request, render_template
from flask_socketio import SocketIO, join_room, leave_room, send
from models.room import Room 
# from providers.game import Game 
from bson.json_util import dumps
from pymongo import  MongoClient
from flask_cors  import CORS

app = Flask(__name__)
CORS(app)

host = 'localhost'
port = 27017
mongo = MongoClient(host, port)

# rooms = Room(mongo)
# games = Game(mongo)

socketio = SocketIO(app, cors_allowed_origins="*")
app.debug = True

active_rooms = []
active_hits = []

room = Room(mongo)

# def logging(func):
#     def function():
#         print(func.__name__+" has called")
#         return func;

# @logging
# @app.route('/')
# def index():
    # return render_template('hello.html')

@socketio.on('connect')
def connect():
    print('New client connected to socket.')

    send('Mensaje desde servidor')
    send('Mensaje desde servidor', broadcast=True)
    send('Mensaje desde servidor', namespace='/game')
    

@socketio.on('connect', namespace='/game')
def connect_game():
    print('[Sockets] CONNECT')

    send("Someone has join to the room.", json=False, broadcast=True, namespace="/game")


@app.route('/create', methods=['POST'])
def create(): 

    _name = request.form['name']
    # _room = rooms.create(_name)
    
    active_rooms.append(_room['code'])

    return dumps(_room)


@socketio.on('join', namespace='/game')
def on_join_game(data):
    print('On join game', data)
    room = data['code']
    name = data['name']

    # _room = rooms.join(name, room)
    join_room(room)

    # Message to user joined.
    send(dumps(_room), room=room, namespace='/game')

    # Message to all users..
    send({'name': name, 'score':0}, room=room, broadcast=True, namespace='/game', include_self=False)

@socketio.on('leave', namespace='/game')
def on_leave_game(data):

    room = data['code']
    name = data['name']

    # _room = rooms.leave(name, room)
    
    leave_room(room)

    # Message to all users..
    send({'name': name}, room=room, broadcast=True, namespace='/game', include_self=False)


@socketio.on('hit', namespace='/game')
def on_hit_game(data):

    room = data['room']
    name = data['name']

    hit_code = data['hit']
    if hit_code in active_hits:
        active_hits.remove(hit_code)
        # score = rooms.hit(name, room)
        send({'name':name, 'score':score}, room=room, namespace="/game")  
        

if __name__ == "__main__":
    socketio.run(app)


