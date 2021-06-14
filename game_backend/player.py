

class Player:
    def __init__(self, name="Joueur_par_defaut", symbol="@"):
        self.name = name
        self._symbol = symbol
        self.health_points = 100
        self._x = None
        self._y = None
        self.golds = 0
        self._dx = None
        self._dy = None
        self.complete = False
        self.strength = 50

    def initPos(self, _map):
        '''Initialize the position of the monster randomly using the rejection method'''
        n_row = len(_map)

        y_init = n_row//2
        found = False
        while found is False:
            y_init += 1
            for i,c in enumerate(_map[y_init]):
                if c == ".":
                    x_init = i
                    found = True
                    break

        self._x = x_init
        self._y = y_init

        _map[self._y][self._x] = self._symbol

    def move(self, dx, dy, map):
        '''Move the player on the grid depending what's facing it, what it steps on and what direction it is supposed to go'''
        new_x = self._x + dx
        new_y = self._y + dy

        self._dx = dx
        self._dy = dy
        
        if map[new_y][new_x] == ".":
        
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = "."
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol}]
            self._x = new_x
            self._y = new_y
        # Cas où le joueur marche sur des golds.
        elif map[new_y][new_x] == "T":
           
            self.golds += 10
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = "."
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol}]
            self._x = new_x
            self._y = new_y
        # Cas où le joueur marche sur une potion.
        elif map[new_y][new_x] == "P":
           
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = "."
            self.health_points = min(self.health_points + 10, 100)
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol}]
            self._x = new_x
            self._y = new_y
        # Cas où le joueur marche sur un piège.
        elif map[new_y][new_x] == "U":
            
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = "."
            self.health_points = max(0,self.health_points - 20)
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol}]
            self._x = new_x
            self._y = new_y
        # Cas où le joueur passe la porte.
        elif map[new_y][new_x] == "D":
          
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = "."
            self.complete = True
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol}]
            self._x = new_x
            self._y = new_y

        else:
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol}, {"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol}]
        return data
    
    def dead(self):
        '''Return True if the player is dead'''
        return self.health_points <= 0

    def hurt(self,game,damage):
        '''Apply damage to the player thus reducing its health and eventually kill it if its health points go below zero'''
        self.health_points -= damage
        if self.dead():
            self.die(game)

    def die(self,game):
        '''Make the player die : remove it from the map and the game session'''
        game._map[self._y][self._x] = '.'
        game.players.remove(self)