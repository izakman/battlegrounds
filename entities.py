
import geolocation

class Entity(object):
    
    def __init__(self, location, radius, team):
        self.location = location
        self.radius = radius
        self.team = team
    
    def checkHasEntered(self, player):
        ''' Check whether a player has entered the entity's radius.  If so it activates the enitity. '''
        #print "--- Check if %s entered %s%s" % (player.name, self.etype, self.ID)
        dist = geolocation.distanceBetweenPoints(self.location, player.location)
        if (dist <= self.radius):
            #print " -- %s entered %s" % (player.name, self.etype)
            self.playerEntered(player)


class Mine(Entity):
    
    def __init__(self, layedBy):
        super(Mine, self).__init__(layedBy.location, 20, layedBy.team)
        self.layedBy = layedBy
        self.etype = 'mine'
        
    def playerEntered(self, player):
        #print " --- %s(%s) entered %s(%s)" % (player.name, player.team, self.etype, self.team)
        if (player.ID != self.layedBy.ID) and (player.team != self.team):
            self.layedBy.hitPlayer(player, 'mine', 2)
            self.game.removeEntity(self) # mine has expoded, remove it from the game


class Flag(Entity):
    
    def __init__(self, location, team=None):
        super(Flag, self).__init__(location, 5, team)
        self.etype = 'flag'
    
    def playerEntered(self, player):
        pass





#if __name__ == '__main__':
#    #players have been tested
#    from models_players import *
#    
#    print 'Testing Entities'
#    
#    player1 = newPlayer('gunner', 'bob')
#    player2 = newPlayer('engineer', 'sam')
#    
#    player2.updateLocation([1,1])
#    mine1 = Mine(player2)
#    print mine1.location
#    print mine1.layedBy.name
#    player2.updateLocation([2,2])
#    mine2 = Mine(player2)
#    print mine2.location
#    print mine2.layedBy.name
#    
    
    
    