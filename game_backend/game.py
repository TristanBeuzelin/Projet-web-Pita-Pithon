from os import PathLike
from .map_generator import Generator
from .player import Player
from .monster import Monster

class Game:
    def __init__(self, width=96, height=32, *args):
        self._generator = Generator(width=width, height=height)
        self._generator.gen_level()
        self._generator.gen_tiles_level()
        # Génération des golds, potions, pièges
        self._generator.gen_treasure()
        self._generator.gen_potion()
        self._generator.gen_trap()
        # Attribut désignant si la porte est révélée ou pas
        self.door_revealed = False
        # Niveau de la partie
        self.level = 1
        self._map = self._generator.tiles_level
        self.height = self._generator.height
        self.width = self._generator.width
        # Création du premier joueur, on est par défaut en mode Solo.
        self.players = [Player()]
        self.players[0].initPos( self._map )
        self.mode = "Single"
        # Génération des monstres
        self._Monster = self._generator.gen_monster(self)
        self.fireballs = []

                
    def rename_player(self, name):
        """
        Permet de renommer le joueur lorsqu'on pass au mode multi.
        """
        self.players[0].name = name

    def add_player(self, name):
        """
        Permet d'ajouter des joueurs qui se connectent au mode multi.
        """
        flag = False
        for player in self.players:
            if player.name == name:
                flag = True
        if not flag:
            player = Player(name)
            player.initPos(self._map)
            self.players.append(player)
    
    def update_Monster(self):
        """
        Fonction de mise à jour de la position des monstres
        """
        data_list = []
        for monster in self._Monster:
            data = monster.move(self._map, self.players)
            data_list.append(data)
        return data_list

    def update_fireballs(self):
        """
        Fonction de calcul de la nouvelle position des boules de feu, et de leur interaction
        avec l'environnement. On veut qu'elles détruisent tout sur leur passage et qu'elles
        infligent des dégâts aux monstres et autres joueurs.
        """
        data = []
        fireball_damage_player = 10
        fireball_damage_monster = 20
        for i, fireball in enumerate(self.fireballs):
            dx = fireball[2][0]
            dy = fireball[2][1]
            new_x = fireball[0] + dx
            new_y = fireball[1] + dy
            x = fireball[0]
            y = fireball[1]
            
            if self._map[new_y][new_x] == ".":
            
                self._map[new_y][new_x] = "F"
                self._map[y][x] = "."
                data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"F"}, [dx, dy]])
                fireball[0] = new_x
                fireball[1] = new_y

            elif self._map[new_y][new_x] == "T":
            
                self._map[new_y][new_x] = "F"
                self._map[y][x] = "."
                data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"F"}, [dx, dy]])
                fireball[0] = new_x
                fireball[1] = new_y

            elif self._map[new_y][new_x] == "P":
            
                self._map[new_y][new_x] = "F"
                self._map[y][x] = "."
                data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"F"}, [dx, dy]])
                fireball[0] = new_x
                fireball[1] = new_y

            elif self._map[new_y][new_x] == "U":
                
                self._map[new_y][new_x] = "F"
                self._map[y][x] = "."
                data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"F"}, [dx, dy]])
                fireball[0] = new_x
                fireball[1] = new_y

            elif self._map[new_y][new_x] == "#":
                self.fireballs.pop(i)
                self._map[new_y][new_x] = "#"
                self._map[y][x] = "."
                data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"#"}, [0, 0]])

            for monster in self._Monster:
                if (new_x, new_y) == (monster._x, monster._y):
                    self.fireballs.pop(i)
                    self._map[y][x] = "."
                    data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{y}", "j":f"{x}", "content":"."}, [2, 0]])
                    monster.hurt(self, fireball_damage_monster)
                    if monster.dead():
                            data.append([{"i": f"{new_y}", "j":f"{new_x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"."}, [2, 0]])

            for player in self.players:
                if (new_x, new_y) == (player._x, player._y):
                    self.fireballs.pop(i)
                    self._map[y][x] = "."
                    data.append([{"i": f"{y}", "j":f"{x}", "content":"."}, {"i": f"{y}", "j":f"{x}", "content":"."}, [2, 0]])
                    player.hurt(self, fireball_damage_player)
                    if player.dead():
                        data.append([{"i": f"{new_y}", "j":f"{new_x}", "content":"."}, {"i": f"{new_y}", "j":f"{new_x}", "content":"."}, [2, 0]])
                    
        return data

    def getMap(self):
        return self._map

    def move(self, dx, dy, name):
        """
        Déplace le joueur qui l'a demandé
        """
        for obj in self.players:
            if obj.name == name:
                player = obj
        return player.move(dx, dy, self._map)


    def reset(self,json):
        """
        Réinitialisation de la partie, ou passage au niveau suivant.
        """
        next_level = json['next_level']
        if not next_level:
            for player in self.players:
                player.health_points = 100
                player.golds = 0
            self.level = 0
            self._Monster = []
        else:
            for player in self.players:
                player.golds = 0
            self.level += 1
        self._generator.tiles_level = []
        self._generator.level = []
        self._generator.room_list = []
        self._generator.corridor_list = []
        self._generator.tiles_level = []
        self._generator.gen_level()
        self._generator.gen_tiles_level()
        self._generator.gen_treasure()
        self._generator.gen_potion()
        self._generator.gen_trap()
        self._map = self._generator.tiles_level
        self.height = self._generator.height
        self.width = self._generator.width
        for player in self.players:
            player.initPos( self._map )
            player.complete = False
        self.door_revealed = False
        self._Monster = self._generator.gen_monster(self)