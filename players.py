
import entities
import geolocation

def newPlayer(classType, playerName, team):
    if   classType == 'gunner':   return Gunner(playerName, team)
    elif classType == 'engineer': return Engineer(playerName, team)
    elif classType == 'recon':    return Recon(playerName, team)
    elif classType == 'medic':    return Recon(playerName, team)

class Player(object):
    
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.messagesToBeSent = []
        self.health = 3
        self.killed = False
        self.teammates = {}
        self.location = None
        self.score = 0
        self.kills = 0
        self.deaths = 0
      
    def updateLocation(self, location):
        ''' Update the player's location. '''
        self.location = tuple(location)
        for entity in self.game.entities.values():
            entity.checkHasEntered(self)
    
    def addMessageToSend(self, message):
        ''' Adds a message to the players message queue. '''
        self.messagesToBeSent.append(message)
    
    def clearMessages(self):
        self.messagesToBeSent = list()
    
    def useKnife(self):
        pass
    
    def hitPlayer(self, target, weapon, damage):
        ''' Player hit an opponent with the given weapon. '''
        self.addMessageToSend({'type':'hit', 'data':{'target':target.ID, 'weapon':weapon}})
        target.wasHit(self, weapon, damage)
        print " >>> "+ self.name +" hit "+ target.name +" with a "+ weapon
        if target.killed:
            self.addMessageToSend({'type':'kill', 'data':{'target':target.ID, 'weapon':weapon}})
    
    def missed(self, weapon):
        self.addMessageToSend({'type':'missed', 'weapon':weapon})
        print " --- "+ self.name +" missed with a "+ weapon
    
    def wasHit(self, by, weapon, damage):
        ''' Player was hit by an opponent. '''
        self.health -= damage
        print "   > "+ self.name +"s health is now "+ str(self.health)
        if self.health <= 0:
            self.wasKilled(by, weapon)
        else:
            self.addMessageToSend({'type':'wasdamaged', 'data':{'by':by.ID, 'weapon':weapon, 'damage':damage}})
    
    def wasKilled(self, oppnt, weapon):
        print " xxx "+ oppnt.name +" killed "+ self.name
        oppnt.kills += 1
        self.killed = True
        self.deaths += 1
        print " xxx set %s to killed" % self
        self.game.playerKilled(self, oppnt)
        print " xxx removed %s from game" % self
        self.addMessageToSend({'type':'waskilled', 'data':{'by':oppnt.ID, 'weapon':weapon}})
        print " xxx sent waskilled"
    
    def wasRevived(self):
        print " +++ "+ self.name +" was revived"
        self.killed = False
        self.health = 3
        self.game.playerRevived(self)
        
    def __repr__(self):
        return "%s[%d:%s]" % (self.name, self.ID, self.classType)
    
    def __str__(self):
        return self.name



class Gunner(Player):
    def __init__(self, name, team):
        super(Gunner, self).__init__(name, team)
        self.classType = 'gunner' 
               
    def doAction(self, action, data=None):
        if action == 'gun':
            print data['bearing']
            self.shootGun(60, 20, data['bearing'])
        elif action == 'knife':
            self.useKnife(self.game, self)
            print self.name + ' Hack, Slash'
    
    def shootGun(self, gunRange, field, bearing):
        targetList = self.game.getOpponentsInRange(self, gunRange)
        if targetList:  # now build a list of the players within the field
            print "   ..targets found"
            targetsInField = []
            for target in targetList:
                targetPlayer = target[0]
                if geolocation.withinField(self.location, targetPlayer.location, bearing, field):
                    targetsInField.append(target)
            if targetsInField:
                print "   ..targets in field"
                targetsInField.sort(key=lambda target: target[1]) # sort on the distance to player
                targetHit = targetsInField[0] # get the closest player in field
                self.hitPlayer(targetHit[0], 'gun', 1)
            else:
                self.missed('gun')
        else:
            self.missed('gun')
    

class Engineer(Player):
    def __init__(self, name, team):
        super(Engineer, self).__init__(name, team)
        self.classType = 'engineer'
        
    def doAction(self, action, data=None):
        if action == 'mine':
            self.plantMine()
            print self.name + ' Mine Planted'
        elif action == 'knife':
            self.useKnife()
            print self.name + ' Hack, Slash'
    
    def plantMine(self):
        mine = entities.Mine(self)
        self.game.addEntity(mine)
        self.addMessageToSend({'type':'planted', 'data':{'loc':mine.location}})


class Recon(Player):
    def __init__(self, name, team):
        super(Recon, self).__init__(name, team)
        self.classType = 'recon'
        
    def doAction(self, action, data=None):
        if action == 'scan':
            self.scanPlayers(30)
            print self.name + ' Scanned Area'
        elif action == 'knife':
            self.useKnife()
            print self.name + ' Hack, Slash'
    
    def scanPlayers(self, scanRange):
        targetList = self.game.getOpponentsInRange(self, scanRange)
        print targetList
        if targetList:
            scannedPlayers = {}
            for target in targetList:
                targetPlayer = target[0]
                scannedPlayers[targetPlayer.ID] = targetPlayer.location
            self.addMessageToSend({'type':'scan', 'targets':scannedPlayers})
            if self.teammates: #if player has teammates
                for player in self.teammates.values():
                    player.addMessageToSend({'type':'scan', 'targets':scannedPlayers})
        else:
            self.missed('scan')
    
#    def scanMines(self, scanRange):
#        targetList = self.game.entitiesWithin(self.location, scanRange)
#        if targetList:
#            self.objectsScanned('mine', targetList)
#        else:
#            self.missed('scan')
            

class Medic(Player):
    
    def __init__(self, name, team):
        super(Medic, self).__init__(name, team)
        self.classType = 'medic'

    def doAction(self, action, data=None):
        if action == 'heal':
            target = self.game.getPlayer(data['playerID'])
            self.heal(target)
            print self.name + ' Scanned Area'
        elif action == 'knife':
            self.useKnife()
            print self.name + ' Hack, Slash'
    
    def heal(self, player):
        player.health = 3
        print "   + "+ self.name +" healed "+ player.name
        self.addMessageToSend({'type':'healed', 'playerID':player.ID})
        player.addMessageToSend({'type':'wasHealed', 'playerID':self.ID})
    
    
