from .GameManager import GameManager
from collections import defaultdict
import collections #for default dictionary
class LobbyManager:

	GameManagerDict = defaultdict(GameManager)

	def createGame(self, hostSID, gameCode):
		newGame = GameManager(gameCode, hostSID)
		self.GameManagerDict[gameCode] = newGame

	def removeGame(self, gameCode):
		self.GameManagerDict.pop(gameCode, None)

	def checkHostDisconnect(self, sid):
		for game in self.GameManagerDict.values():
			if sid == game.host:
				roomCode = game.gameCode
				self.removeGame(game.gameCode)
				return roomCode
		return 0

	def getGameManager(self, gameCode):
		if gameCode in self.GameManagerDict.keys():
			return self.GameManagerDict[gameCode]
		else:
			return 0

	#Adds the player to the GameManager for the room
	def addPlayer(self, gameCode, playerObj):
		if gameCode in self.GameManagerDict.keys():
			self.GameManagerDict[gameCode].addPlayer(playerObj)

	def removePlayer(self, sid):
		for game in self.GameManagerDict.values():
			if game.removePlayer(sid):
				return game.host
		return 0

	def getNameFromSID(self, sid):
		for game in self.GameManagerDict.values():
			tempName = game.getNameFromSID(sid)
			if tempName != "":
				return tempName
		return ""

	#checks if the game with the code exists
	def getHostSID(self, gameCode):
		if gameCode in self.GameManagerDict.keys():
			return self.GameManagerDict[gameCode].host
		return 0

	def roomValidation(self, gameCode, name):
		if self.checkDupGameCode(gameCode) == 0:
			return 1
		elif self.checkNumOfPlayers(gameCode):
			return 2
		elif self.checkDupUsername(gameCode, name):
			return 3
		return 0

	#check if the code given alrdy exists
	def checkDupGameCode(self, gameCode):
		if gameCode in self.GameManagerDict.keys():
			return 1 #return 1 if it does exist
		return 0 #0 if it does not

	#checks for dup username in the speciifc room
	def checkDupUsername(self, gameCode, name):
		for player in self.GameManagerDict[gameCode].activePlayers:
			if player.username == name:
				return player.sid #because I'm going to use this checkExistingPlayer
		return 0

	def checkNumOfPlayers(self, gameCode):
		if len(self.GameManagerDict[gameCode].activePlayers) > 7:
			return 1 #return 1 if it's full
		return 0

	#returns the state of the game if the username exists
	def checkExistingPlayer(self, gameCode="", name="", newSid=""):
		if (gameCode == "" or name == "" or newSid == ""):
			return 0
		if gameCode in self.GameManagerDict.keys():
			game = self.GameManagerDict[gameCode]
			for player in self.GameManagerDict[gameCode].activePlayers:
				if player.username == name:
					player.sid = newSid
					return 1
		return 0