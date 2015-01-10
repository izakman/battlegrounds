
import cherrypy
from cherrypy import tools

# For HTML Templates
#from mako.template import Template
#from mako.lookup import TemplateLookup
#myhtml = TemplateLookup(directories=['html'])

# Our modules
import games
import players

class GameHandler:
    def __init__(self, game):
        self.game = game
    
    @cherrypy.expose
    def index(self):
        return "Game running..."
        
    @cherrypy.expose
    @tools.json_in(on = True)
    @tools.json_out(on = True)
    def add_player(self):
        ''' Add a player to the game and send a message back in the response with the ID of the player. '''
        request = cherrypy.request.json
        player = players.newPlayer(request['class'], request['name'], request.get('team'))
        self.game.addPlayer(player)
        return {'id':player.ID}
    
    @cherrypy.expose
    @tools.json_in(on = True)
    @tools.json_out(on = True)
    def has_game_started(self):
        ''' Players run this to check if the game has started. '''
        if len(self.game.players) > 0: # number of players before game is ready
            request = cherrypy.request.json
            playersInGame = []
            for player in self.game.players.values():
                if player.ID != request['id']:
                    playersInGame.append({'id':player.ID, 'name':player.name, 'team':player.team})
            self.game.started = True
            return {'ready':True, 'gametype':self.game.gameType, 'playersInGame':playersInGame}
        else:
            return {'ready':False}
            
    @cherrypy.expose
    @tools.json_in(on = True)
    @tools.json_out(on = True)
    def revive_player(self):
        request = cherrypy.request.json
        player = self.game.getKilled(request['id'])
        if player != None:
            player.wasRevived()
    
    @cherrypy.expose
    @tools.json_in(on = True)
    @tools.json_out(on = True)
    def player_request(self):
        ''' Main handler for incomming messages from players. '''
        request = cherrypy.request.json              # save json request
        player = self.game.getPlayer(request['id'])  # retrieve player that made the request
        if player != None:
            player.updateLocation(request['loc'])        # save players location
            # Handle messages if included.
            if 'messages' in request:
                self.handleMessages(request['messages'], player)
                ###print request['messages']
            # Return server messages that need to be sent to the player.
            teammates = self.prepareTeammates(player.teammates)
            serverMessages = player.messagesToBeSent
            player.clearMessages()
            if serverMessages:
                return {'teammates':teammates, 'messages':serverMessages}
            else:
                return {'teammates':teammates}
        return {}
            
    def prepareTeammates(self, teammates):
        fTeammates = {}
        for pID, player in teammates.items():
            pLocation = player.location
            if pLocation:
                fTeammates[pID] = pLocation
        return fTeammates
    
    def handleMessages(self, messages, player):
        for message in messages:
            player.doAction(message['type'], message.get('data')) # use get() to avoid handling an exception if there is no data.


class GameServer:
    
    @cherrypy.expose
    def index(self):
        return "This is the GameServer"
    
#     @cherrypy.expose
#     def newGame(self, gameID, gameOptions):
#         ''' Adds a new game. '''
#         # Add a new GameHandler to the url tree for a game with the given options/
#         setattr(root, gameID, GameHandler(gameID, gameOptions))
#         return "Added Game: %s" % gameID


#######################
#class JsonTester:
#    def __init__(self):
#        self.message = {'first':4.0012, 'second':30498}
#    
#    @cherrypy.expose
#    def index(self):
#        page = myhtml.get_template("jsontest.html")
#        return page.render()
    
#######################



if __name__ == '__main__':
    # For handling static files.
    import os.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extraconf = {'/':       {'tools.staticdir.root': current_dir},
                 '/static': {'tools.staticdir.on':   True,
                             'tools.staticdir.dir': 'static'}}

    # Set global site config.
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 8010
                            })
                               
    # Set up URL structure
    root = GameServer()
    root.test_game = GameHandler(games.newGame('teamdeathmatch', 'test_game'))
#    root.json_test = JsonTester()
    
    # Run the server.
    cherrypy.quickstart(root, '/', config=extraconf)


