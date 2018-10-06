import gamelib
import random
import math
import warnings
from sys import maxsize

"""

Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.custom_strategy(game_state)

        game_state.submit_turn()
        
        
    def custom_strategy(self, game_state):
        """
        My custom strategy:
        General idea is to have a number pre-planned types of moves and use them based on the current state
        Plans:
        Defense
            build_wall
            reinforce_wall
            protect_corners
            boost_attackers
        Offsense
            target_weak_side
            EMP_blast
            brute_force_pings
        """
        
        
        # Dumb strategy for now, just testing to see if it works
        self.protect_corners(game_state)
        self.build_wall(game_state,'evens')
        self.reinforce_wall(game_state,'odds')
        self.build_wall(game_state,'odds')
        self.reinforce_wall(game_state,'evens')
        self.boost_attackers(game_state)
        
        if game_state.turn_number % 2 == 0:
            self.EMP_blast(game_state)
        else:
            self.brute_force_pings(game_state,'left')
            
            
            





    def build_wall(self, game_state, evens_or_odds=''):
        """
        Build a wall of filters near the front as the first line of protection
        """

        y = 11;
        x = [ i for i in range(3,25) if i not in [13,14]]
        wall_units = FILTER
        
        wall_locations = [(i,y) for i in x]
        if evens_or_odds:
            if evens_or_odds == 'evens':
                wall_locations = wall_locations[1::2]
            else:
                wall_locations = wall_locations[0::2]
        
        self.build_as_many_as_possible(game_state, wall_units, wall_locations)
        
    def reinforce_wall(self,game_state,evens_or_odds=''):
        """
        Put a row of destructors behind the wall to kill units
        """
        
        y = 10;
        x = [ i for i in range(3,25) if i not in [13,14]]
        wall_units = DESTRUCTOR
        
        wall_locations = [(i,y) for i in x]
        if evens_or_odds:
            if evens_or_odds == 'evens':
                wall_locations = wall_locations[1::2]
            else:
                wall_locations = wall_locations[0::2]
        self.build_as_many_as_possible(game_state, wall_units, wall_locations)
        
        
    def protect_corners(self,game_state,left_or_right=''):
        """
        Add more defenses to the corners where we may be weak
        """
        
        # First add some filters
        wall_units = FILTER
        wall_locations = [[1,13],[2,12],[25,12],[26,13]]
        
        if left_or_right:
            if left_or_right == 'left':
                wall_locations = wall_locations[0:2]
            else:
                wall_locations = wall_locations[2:4]
        self.build_as_many_as_possible(game_state, wall_units, wall_locations)
        
        # Then add some destructors
        wall_units = DESTRUCTOR
        wall_locations = [[1,12],[2,11],[25,11],[26,12]]
        
        if left_or_right:
            if left_or_right == 'left':
                wall_locations = wall_locations[0:2]
            else:
                wall_locations = wall_locations[2:4]
        self.build_as_many_as_possible(game_state, wall_units, wall_locations)
        
        
    def boost_attackers(self, game_state):
        """
        Add some encryptors to help our attackers
        """

        wall_units = ENCRYPTOR
        
        wall_locations = [[12,10],[15,10],[12,9],[15,9],[12,8],[15,8]]

        self.build_as_many_as_possible(game_state, wall_units, wall_locations)


    def build_as_many_as_possible(self, game_state, unit, locations):
        """
        Utility function to build as many units at the given locations as possilbe
        """
        count = 0
        for location in locations:
            if game_state.can_spawn(unit, location):
                game_state.attempt_spawn(unit, location)
                count = count + 1
        return count


    def EMP_blast(self, game_state):
        """
        Build as many EMPs as we can alternating sides
        """
        
        locations = [[8,5],[19,5]]
        n_to_build = game_state.number_affordable(EMP)
        for i in range(n_to_build):
            game_state.attempt_spawn(EMP, locations[i%2])
            
    def brute_force_pings(self, game_state, side):
        """
        Send as many pings as possible
        """

        if side == 'left':
            location = [11,2]
        else:
            location = [16,2]
            
        n_to_build = game_state.number_affordable(PING)
        for i in range(n_to_build):
            game_state.attempt_spawn(PING, location)
            





    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Build the some defenses. Calling this method first prioritises
        resources to build and repair the wall before spending them 
        on anything else.
        """
        self.build_initial_defence(game_state)

        """
        Then build additional defenses.
        """
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_attackers(game_state)

    def build_initial_defence(self, game_state):
        """
        We use Filter firewalls because they are cheap

        First, we build a line accross
        """
        firewall_locations = [[4,10],[5,10],[6,10],[7,10],[8,10],[9,10],[10,10],[11,10],[12,10],[15,10],[16,10],[17,10],[18,10],[19,10],[20,10],[21,10],[22,10],[23,10]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        """
        Build some with destructors
        """
        firewall_locations = [[2,12],[25,12],[3,11],[24,11]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    def build_defences(self, game_state):
        """
        First lets protect ourselves a little with destructors:
        """
        firewall_locations = [[12, 9], [15, 9],[12, 8], [15, 8],[12, 7], [15, 7]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        """
        Then lets boost our offense by building some encryptors to shield 
        our information units. Lets put them near the front because the 
        shields decay over time, so shields closer to the action 
        are more effective.
        """
        firewall_locations = [[11, 9], [16, 9],[11, 8], [16, 8],[11, 7], [16, 7]]
        for location in firewall_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

        

    def deploy_attackers(self, game_state):
        """
        First lets check if we have 10 bits, if we don't we lets wait for 
        a turn where we do.
        """
        if (game_state.get_resource(game_state.BITS) < 10):
            return
        
        """
        First lets deploy an EMP long range unit to destroy firewalls for us.
        """
        if game_state.can_spawn(EMP, [1, 12]):
            game_state.attempt_spawn(EMP, [1, 12])
        if game_state.can_spawn(EMP, [26, 12]):
            game_state.attempt_spawn(EMP, [26, 12])

        """
        Now lets send out 3 Pings to hopefully score, we can spawn multiple 
        information units in the same location.
        """
        if game_state.can_spawn(PING, [11, 2], 3):
            game_state.attempt_spawn(PING, [11,2], 3)

        """
        NOTE: the locations we used above to spawn information units may become 
        blocked by our own firewalls. We'll leave it to you to fix that issue 
        yourselves.

        Lastly lets send out Scramblers to help destroy enemy information units.
        A complex algo would predict where the enemy is going to send units and 
        develop its strategy around that. But this algo is simple so lets just 
        send out scramblers in random locations and hope for the best.

        Firstly information units can only deploy on our edges. So lets get a 
        list of those locations.
        """
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        """
        Remove locations that are blocked by our own firewalls since we can't 
        deploy units there.
        """
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        """
        While we have remaining bits to spend lets send out scramblers randomly.
        """
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(PING) and len(deploy_locations) > 0:
           
            """
            Choose a random deploy location.
            """
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(PING, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
