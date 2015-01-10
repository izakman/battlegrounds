
import geolocation

def newGame(gameType, gameID):
    if   gameType == 'deathmatch':   return Deathmatch(gameID)
    elif gameType == 'teamdeathmatch': return TeamDeathmatch(gameID)

class Game(object):

    def __init__(self, gameID):
        self.gameID = gameID
        self.pID = 0
        self.eID = 0
        self.players = {}
        self.killed = {}
        self.entities = {}
        self.score = 0
        self.started = False
        self.finished = False
    
    def addPlayer(self, player):
        ''' Add a player to the game. '''
        player.ID = self.pID
        player.game = self
        self.pID += 1
        self.players[player.ID] = player
            
    def getPlayer(self, playerID):
        ''' Return a player via their ID. '''
        return self.players.get(playerID)
    
    def getKilled(self, playerID):
        return self.killed.get(playerID)
        
    def addEntity(self, entity):
        ''' Add an entity to the game. '''
        entity.ID = self.eID
        entity.game = self
        self.eID += 1
        self.entities[entity.ID] = entity
    
    def removeEntity(self, entity):
        ''' Remove an entity. '''
        del self.entities[entity.ID]
    
    def playerKilled(self, player, by):
        self.updateScores(player)
        self.killed[player.ID] = player
        del self.players[player.ID]
    
    def playerRevived(self, player):
        self.players[player.ID] = player
        del self.killed[player.ID]
    
    def playersWithin(self, loc, radius):
        ''' Returns a list of lists that contain the players within the
            given radius and the distance between them and specified location. '''
        targetList = []
        for targetPlayer in self.players.values():
            distToTarget = geolocation.distanceBetweenPoints(loc, targetPlayer.location)
            if distToTarget <= radius:
                targetList.append([targetPlayer, distToTarget])
        return targetList
        
    def checkLocationOf(self, player):
        ''' Check if the player has entered the range of an entity.''' 
        for entity in self.entities.values():
            entity.checkHasEntered(player)
    
    def getPlayerScores(self):
        scores = {}
        for player in self.players.values():
            scores[player.ID] = player.score
        return scores


class Deathmatch(Game):
    
    def __init__(self, gameID):
        super(Deathmatch, self).__init__(gameID)
        self.gameType = 'deathmatch'
        self.scoreToWin = 3
    
    def checkForWin(self):
        for player in self.players.values():
            if player.score >= self.scoreToWin:
                self.gameOver(player)
    
    def gameOver(self, winner):
        self.finished = True
        for player in self.players.values():
            if player.ID != winner.ID:
                player.addMessageToSend({'type':'gameover', 'winner':winner.ID, 'finalscores':self.getPlayerScores()})
    
    def updateScores(self, player):
        player.score += 1
    
    def getPlayerOpponents(self, player):
        opponents = self.players.copy().values()
        opponents.remove(player)
        return opponents
    
    def getOpponentsInRange(self, player, actionRange):
        playersInRange = self.playersWithin(player.location, actionRange)
        opponents = []
        for target in playersInRange:
            if target[0] != player:
                opponents.append(target)
        return opponents
    

class TeamDeathmatch(Deathmatch):
    
    def __init__(self, gameID):
        super(TeamDeathmatch, self).__init__(gameID)
        self.gameType = 'teamdeathmatch'
        self.scoreToWin = 5
        self.score = {'red': 0, 'blue': 0}
        self.teams = {'red': [], 'blue': []}
    
    def addPlayer(self, player):
        ''' Add a player to the game. '''
        super(TeamDeathmatch, self).addPlayer(player)
        self.addPlayerToTeam(player)
    
    def addPlayerToTeam(self, player):
        playerTeam = self.teams[player.team]
        for teammate in playerTeam:
            teammate.teammates[player.ID] = player
            player.teammates[teammate.ID] = teammate
        playerTeam.append(player)
        print player.name +" added to "+ player.team +" team"
    
    def checkForWin(self):
        if self.score['red'] == self.scoreToWin:
            self.gameOver('red')
        elif self.score['blue'] == self.scoreToWin:
            self.gameOver('blue')
    
    def gameOver(self, winningTeam):
        self.finished = True
        for player in self.players.values():
            player.addMessageToSend({'type':'gameover', 'winner':winningTeam, 'finalscores':self.getPlayerScores()})
    
    def updateScores(self, player):
        player.score += 1
        self.score[player.team] += 1
    
    def getPlayerOpponents(self, player):
        players = self.players.copy().values()
        opponents = set(players).difference(player.teammates)
        opponents.remove(player)
        return opponents

    def getOpponentsInRange(self, player, actionRange):
        playersInRange = self.playersWithin(player.location, actionRange)
        opponents = []
        for target in playersInRange:
            if (target[0] not in player.teammates.values()) and (target[0] != player):
                opponents.append(target)
        return opponents
    


