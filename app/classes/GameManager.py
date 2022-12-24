import random
import sys

class GameManager:
	def __init__(self, gameCode, hostSID):
		#------House keeping-----#
		self.gameCode = gameCode #To join the game and the roomid for emit
		self.host = hostSID #Host client
		self.activePlayers = [] #Player Object
		self.dcPlayers = [] #Index

	#the playerObj is created in flaskapp under playerJoin
	def addPlayer(self, playerObj):
		self.activePlayers.append(playerObj)

	#remove player if they leave lobby
	def removePlayer(self, playerSID):
		for player in self.activePlayers:
			if player.sid == playerSID:
				#remove them from the lobby
				if self.state == 1:
					self.activePlayers.remove(player)
				#mark them as DC
				else:
					self.dcPlayers.append(self.activePlayers.index(player))
				return 1 #return 1 if we found a player
		return 0

	def getActivePlayersSIDs(self):
		activeSIDs  = []
		for player in self.activePlayers:
			activeSIDs.append(player.sid)
		return activeSIDs

	def getNameFromSID(self, playerSID):
		for player in self.activePlayers:
			if player.sid == playerSID:
				return player.username
		return ""
