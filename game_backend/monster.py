import random
from .player import Player



def dist(pos1,pos2): #Return the absolute distance 
    return abs(pos2[1] - pos1[1]) + abs(pos2[0] - pos1[0])

def neighborhood(map,i,j,l_close): #Return available neighbor position
    l = [(i,j+1),(i,j-1),(i+1,j),(i-1,j)]
    return [point for point in l if map[point[1]][point[0]] not in ['#','S'] and point not in l_close.keys()]

def search_min(l_open): #Return the point with the best quality
    nodes = list(l_open.keys())
    best_node = nodes[0]
    for node in nodes:
        if l_open[node][2] < l_open[best_node][2]:
            best_node = node
    return best_node
    

def move_to_player(map,node,l_open,l_close,start,end): #Search a path between start and end using A* algorithm
    if node != end and l_open != {}:
        neighbors = neighborhood(map,node[0],node[1],l_close)
        for new_node in neighbors:
            newG = dist(new_node,start)
            newH = dist(new_node,end)
            newF = newG + newH
            nodes_open = list(l_open.keys())
            if new_node in nodes_open:
                info = l_open[new_node]
                if newH < info[2]:
                    l_open[new_node] = [node,newG,newH,newF]
            else:
                l_open[new_node] = [node,newG,newH,newF]
        best_node = search_min(l_open)
        l_close[best_node] = l_open[best_node]
        l_open.pop(best_node)
        return move_to_player(map,best_node,l_open,l_close,start,end)
    else:
        if node == end:
            node = end
            path = [end]
            while node != start:
                node = l_close[node][0]
                path.append(node)
            return True,path
        else:
            return False           


    
    

class Monster:
    def __init__(self,level, symbol="X"):
        self._symbol = symbol
        self.health_points = 100
        self._x = None
        self._y = None
        self.strength = 5
        self.view_hero = []
        self._dx = None
        self._dy = None
        self.step_on = "."
        self.previous_step_on = "."

    def distance(self, player):
        return abs(self._y - player._y) + abs(self._x - player._x)

    def initPos(self, _map, height, width, players):
        for player in players:
            found = False
            while found is False:
                y_init = random.randint(0,height-1)  
                x_init = random.randint(0, width-1)
                if _map[y_init][x_init] == "." and (abs(y_init - player._y) + abs(x_init - player._x) > 7):
                    found = True
                    break

        self._x = x_init
        self._y = y_init

        _map[self._y][self._x] = self._symbol


    def attack(self,player):
        return 0


    
    def is_near_player(self,player):
        return self.distance(player) == 1

    def getdxdy(self,map,players):
        dx, dy = 0, 0
        close_players = [player for player in players if self.distance(player) < 7]
        if close_players == []:
            dx,dy = random.choice([[0,0],[0,1],[0,0],[0,-1],[0,0],[1,0],[0,0],[-1,0],[0,0]])
        else:
            paths = []
            for player in close_players:
                start = (self._x,self._y)
                end = (player._x,player._y)
                startG = 0
                startH = dist(start,end)
                l_open = {start : [start,startG,startH,startH]}
                l_close = {}
                b,path = move_to_player(map,start,l_open,l_close,start,end)
                if b:
                    paths.append(path)
            if paths != []:
                L = [len(pathh) for pathh in paths]
                path = paths[L.index(min(L))]
                dx,dy = path[-2][0] - path[-1][0],path[-2][1] - path[-1][1]
            else:
                dx,dy = random.choice([[0, 0], [0, 1], [0, 0], [0, -1], [0, 0], [1, 0], [0, 0], [-1, 0], [0, 0]])
        return dx,dy

    def move(self, map, players):
        dx,dy = self.getdxdy(map, players)
        
        new_x = self._x + dx
        new_y = self._y + dy

        if map[new_y][new_x] == ".":
            
            self.previous_step_on = self.step_on
            self.step_on = "."
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = self.previous_step_on
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self.previous_step_on}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol},[dy,dx]]
            self._x = new_x
            self._y = new_y
            self._dx = dx
            self._dy = dy
            
        elif map[new_y][new_x] == "T":
          
            self.previous_step_on = self.step_on
            self.step_on = "T"
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = self.previous_step_on
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self.previous_step_on}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol},[dy,dx]]
            self._x = new_x
            self._y = new_y
            self._dx = dx
            self._dy = dy
            
        elif map[new_y][new_x] == "P":
            
            self.previous_step_on = self.step_on
            self.step_on = "P"
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = self.previous_step_on
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self.previous_step_on}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol},[dy,dx]]
            self._x = new_x
            self._y = new_y
            self._dx = dx
            self._dy = dy

        elif map[new_y][new_x] == "U":
           
            self.previous_step_on = self.step_on
            self.step_on = "U"
            map[new_y][new_x] = self._symbol
            map[self._y][self._x] = self.previous_step_on
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self.previous_step_on}, {"i": f"{new_y}", "j":f"{new_x}", "content":self._symbol},[dy,dx]]
            self._x = new_x
            self._y = new_y
            self._dx = dx
            self._dy = dy

        elif map[new_y][new_x] == "@" or map[new_y][new_x] == "X":
    
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol}, {"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol},[dy,dx]]
            self._dx = dx
            self._dy = dy

        else:
            data = [{"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol}, {"i": f"{self._y}", "j":f"{self._x}", "content":self._symbol},[self._dy,self._dx]]
       
        return data


    def die(self,map):
        map[self._y][self._x] = self.step_on
        