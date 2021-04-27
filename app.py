from flask import Flask, render_template, flash , redirect, session, request
from flask_socketio import SocketIO
from game_backend import Game
from form import LoginForm
from time import time
import json 


app = Flask(__name__)
app.config['SECRET_KEY'] = "123"
socketio = SocketIO(app)
game = Game()
global move_time
move_time = time()
print(move_time)

@app.route("/")
def accueil():
    return render_template("choice.html")

@socketio.on("choice")
def choice(json):
    choice = json['response']
    if choice == 'single':
        return redirect("/game")
    elif choice == 'multi':
        return redirect("/game")

@app.route("/single")
def index():
    maping = game.getMap()
    session['username'] = 'Joe'
    return render_template("index.html", mapdata= maping, n_row=len(maping), n_col=len(maping[0]), golds=[player.golds for player in game.players], HP=[player.health_points for player in game.players], level=game.level, username=str(session['username']))

@app.route("/multilog", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['username'] = request.form['username']
        return redirect("/multi")
    return render_template("login.html", form=form)

@app.route("/multi")
def multi():
    maping = game.getMap()
    if len(game.players) == 1 and game.players[0].name == 'Joe':
        game.rename_player(session['username'])
    else:
        game.add_player(session['username'])
    return render_template("index.html", mapdata= maping, n_row=len(maping), n_col=len(maping[0]), golds=[player.golds for player in game.players], HP=[player.health_points for player in game.players], level=game.level, username=[player.name for player in game.players])

@socketio.on("move")
def on_move_msg(json, methods=["GET", "POST"]):
    dx = json['dx']
    dy = json['dy']
    
    data = game.move(dx,dy, session['username'])
    ### Ajout ###
    data.append([player.golds for player in game.players])
    data.append([player.health_points for player in game.players])
    data.append(game.width)
    data.append(game.height)
    data.append([player.complete for player in game.players])
    data.append([dx,dy])

    
    socketio.emit("response", data)
    ######


@socketio.on("door")
def door():
    if not game.door_revealed:
        x, y = game._generator.gen_door()
        game._map[y][x] = "D"
        game.door_revealed = True
        socketio.emit("door_response",[x,y])

@socketio.on("reset")
def reset(json):
    game.reset(json)
    socketio.emit("reset_response")


@socketio.on("monster_move")
def monster_move():
    global move_time
    print(time()-move_time)
    if time()-move_time > 0.2:
        move_time = time()
        data_list = game.update_Monster()
        N = len(data_list)
        socketio.emit("monster_response", json.dumps([N,data_list]))


@socketio.on("player_attack")
def player_attack():
    for obj in game.players:
        if obj.name == session['username']:
            player = obj
    for i,monster in enumerate(game._Monster):
        if [player._x + player._dx, player._y + player._dy] == [monster._x,monster._y]:
            monster.health_points -= player.strength
            if monster.health_points <= 0:
                monster.die(game._map)
                game._Monster.remove(monster)
                socketio.emit("monster_die",[monster._y,monster._x,monster.step_on])
    for i, other_player in enumerate(game.players):
        if [player._x + player._dx, player._y + player._dy] == [other_player._x,other_player._y]:
            other_player.health_points -= player.strength
            if other_player.health_points <= 0:
                other_player.die(game._map)
                game.players.remove(other_player)
                socketio.emit("player_die",[other_player._y, other_player._x, '.'])

if __name__=="__main__":
    socketio.run(app, port=5001, debug=True)


