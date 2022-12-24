from flask import Flask, render_template
from flask import request, session, jsonify, make_response
from flask_socketio import send, emit, join_room, leave_room
from flask_socketio import SocketIO
from app.classes.LobbyManager import LobbyManager
from app.classes.Player import Player
from app.classes.Forms import LoginForm
import string
import random
HOST = '0.0.0.0.0'
PORT = 5000
# app = Flask(__name__)
socketio = SocketIO()
#Variables for testing
clients = []
players = 0
host = None

#This is the main flask application that will handle all the html rendering/routing.
flask_app = Flask('flaskapp')
#This secret key is used for authentication purposes, mainly needed for WtForms
flask_app.config['SECRET_KEY'] = "dango-game-show"
#Assign variables to config object
flask_app.config['debug'] = 0
flask_app.config['players'] = players
flask_app.config['host'] = host
flask_app.config['LobbyManager'] = LobbyManager()

#Initialize the socketIO object
socketio.init_app(flask_app, cors_allowed_origins="*")
if __name__ == '__main__':
	socketio.run(flask_app)

@socketio.on('connect')
def handle_connect():
	clients.append(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
	clients.remove(request.sid)
	#check if it was a host that disconnected
	gameCode = flask_app.config['LobbyManager'].checkHostDisconnect(request.sid)
	if gameCode:
		emit('serverMsg', 'return', room=gameCode)
		return

	#check if a player inside a game disconnected
	userName = flask_app.config['LobbyManager'].getNameFromSID(request.sid)
	if userName != "":
		hostSID = flask_app.config['LobbyManager'].removePlayer(request.sid)
		emit('playerLeave', userName, room=hostSID)

#Emits an event to all clients to a subset list of clients
def tellGroup(event, group):
	for clientid in group:
		socketio.emit(event, room=clientid)

#Emits an event with some associated data to a subset list of clients
def tellGroupWithData(event, data, group):
	for clientid in group:
		socketio.emit(event, {'data' : data}, room=clientid)

def randCode(size = 4):
	chars = string.ascii_uppercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))

#Routes
@flask_app.route('/')
def main():
	return render_template('index.html')

@flask_app.route('/index', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@flask_app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

#Join Game Form Page
@flask_app.route('/join', methods=['GET', 'POST'])
def join():
	form = LoginForm()
	return render_template('join.html', title='Home', form=form)

#Validate form values .
@flask_app.route('/login', methods=['GET', 'POST'])
def login():
	#Populate a new form with the input
	form = LoginForm(request.values)
	#Validate the input based off of the LoginForm class
	if form.validate_on_submit():
		checkValid = flask_app.config['LobbyManager'] .roomValidation(form.room_code.data, form.name.data)
		if checkValid == 0:
			resp = make_response(render_template('client_canvas.html', username=form.name.data, room_code=form.room_code.data))
			return resp
		return jsonify(error=checkValid)
	#Rerender the index html with error messages for the respective fields
	return jsonify(error=4) #error4 is didn't fill out correctly

#Create a game
@flask_app.route('/create', methods=['GET', 'POST'])
def create():
	gameCode = randCode()
	while (flask_app.config['LobbyManager'].checkDupGameCode(gameCode)):
		gameCode = randCode()
	return render_template('host_canvas.html', code=gameCode)

#Displays a client canvas for a player who needs to draw
@flask_app.route('/client_draw', methods=['GET', 'POST'])
def displayDrawingPhase():
		data = request.get_json()
		return render_template('client_canvas.html', username=data['username'], room_code=data['room_code'])

#Socket On
@socketio.on('canvasData')
def displayDrawing(json):
	game = flask_app.config['LobbyManager'].getGameManager(json['masterRoomCode'])
	emit('playerDrawData', json, room=game.host)

@socketio.on('clearCanvas')
def displayDrawing(json):
	game = flask_app.config['LobbyManager'].getGameManager(json['masterRoomCode'])
	emit('clearCanvas', json, room=game.host)

@socketio.on('createGame')
def createGame(gameCode):
	flask_app.config['LobbyManager'].createGame(request.sid, gameCode)
	join_room(gameCode)
	return

@socketio.on('disconnectGame')
def dcGame(gameCode):
	flask_app.config['LobbyManager'].removeGame(gameCode)
	emit('serverMsg', 'return', room=gameCode)
	return
	#take all the people in the room back to the home screen
	#remove the game

@socketio.on('checkExistUser')
def checkExistUser(formData):
	gameState =  flask_app.config['LobbyManager'].checkExistingPlayer(formData['room_code'], formData['user'], request.sid)

	#if there are no registered user of that name yet
	if gameState == 0:
		emit('playerState', {'gameState': gameState}, room=request.sid)
		return
	elif gameState == 1:
		emit('drawingPhase', {'username':formData['user'], 'room_code':formData['room_code']})

@socketio.on('playerJoin')
def playerJoin(message):
	if flask_app.config['LobbyManager'].checkDupUsername(message['room_code'], message['username']):
			return
	newPlayer = Player(request.sid, message['username'])
	flask_app.config['LobbyManager'].addPlayer(message['room_code'], newPlayer)
	join_room(message['room_code'])
	hostSID = flask_app.config['LobbyManager'].getHostSID(message['room_code']);
	if hostSID == 0:
		return
	emit('playerJoinGame', {'username': message['username']}, room=hostSID)

@socketio.on('playerLeave')
def playerLeave(message):
	flask_app.config['LobbyManager'].removePlayer(request.sid)
