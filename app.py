from flask import Flask, render_template, flash , redirect, session, request
from flask_socketio import SocketIO
from game_backend import Game
from form import LoginForm
from time import time
import json
import pickle


app = Flask(__name__)
app.config['SECRET_KEY'] = "123"
socketio = SocketIO(app)

# Chargement de la partie.
# Charge la partie sauvegardée si il y en a une.
# En crée une nouvelle sinon.
# On déclare game en global pour pouvoir l'utiliser dans les socketio.on
global game
try:
    with open('save', 'rb') as data:
        game = pickle.load(data)
except:
    game = Game()

# Déclaration des intervalles de temps de mouvement et d'attaque des monstres.
# On les déclare en global pour les mêmes raisons que game.
# Ces variables conditionnent grandement la difficulté du jeu.
# Elles permettent aussi d'éviter l'overload de requêtes d'attaque et/ou de mouvement.
# On le voit dans la suite.
global move_time
move_time = time()
global attack_time
attack_time = time()

# Fonction qui construit la liste à passer ensuite en JSON pour acutaliser les stats des joueurs.
# Sert dans les socket.emit('actualize')
def data_actualize_construct(game):
    data = []
    data.append([player.golds for player in game.players])
    data.append([player.health_points for player in game.players])
    data.append([player.complete for player in game.players])
    data.append([player.name for player in game.players])
    return data

# Page d'accueil qui sert à choisir le mode de jeu.
@app.route("/")
def accueil():
    return render_template("choice.html")

@app.route("/single")
def index():
    """
    Page de jeu solo. On déclare game en global pour se servir de la même variable que celle déclarée avant.
    Si l'on passe du multi au single, on regarde si il ya une partie sauvegardée, sinon on en crée une nouvelle.
    Nous imposons un nom de session single par défaut. Ce n'est pas forcément indispensable.
    Les arguments passés dans le render servent ensuite dans le html via Jinja2.
    On passe la carte, sa taille, les stats du joueur et le niveau de la partie.
    """
    global game
    if game.mode == "Multi":
        try:
            with open('save', 'rb') as data:
                game = pickle.load(data)
        except:
            game = Game()
    maping = game.getMap()
    session['username'] = 'Tristan'
    return render_template("index.html", mapdata= maping, n_row=len(maping), n_col=len(maping[0]), golds=str(game.players[0].golds), HP=str(game.players[0].health_points), level=game.level)

@app.route("/multilog", methods=['GET', 'POST'])
def login():
    """
    Page de login dans le mode multi. On rentre notre pseudo dans un form du html qui le transmet à la fonction login
    La session prend alors pour nom celui rentré. C'est ce qui permet ensuite d'identifier le joueur qui lance une action.
    Si ce form est validé, le joueur est redirigé vers la page de jeu.
    """
    form = LoginForm()
    if form.validate_on_submit():
        session['username'] = request.form['username']
        return redirect("/multi")
    return render_template("login.html", form=form)

@app.route("/multi")
def multi():
    """
    Page de jeu multijoueur. On prend cette fois en compte le cas du passage du mode single au multi.
    Si c'est le cas, on lance une nouvelle partie et on renomme la session avec le pseudo choisi avant.
    Si un joueur est déjà présent dans la partie, on ajoute le nouveau et on actualise les stats des joueurs.
    """
    global game
    if game.mode == 'Single':
        game = Game()
        game.rename_player(session['username'])
        game.mode = 'Multi'
    else:
        game.add_player(session['username'])
        data = data_actualize_construct(game)
        socketio.emit('actualize'), data
    maping = game.getMap()
    return render_template("index.html", mapdata= maping, n_row=len(maping), n_col=len(maping[0]), golds=" ".join(str(player.golds) for player in game.players), HP=" ".join(str(player.health_points) for player in game.players), level=game.level, username=" ".join(player.name for player in game.players))

# Il y a à partir d'ici les fonctions qui se lancent seulement sur requête socket provenant du JavaScript.

@socketio.on("move")
def on_move_msg(json, methods=["GET", "POST"]):
    """
    Fonction qui se lance à la requête move.
    On construit cette fois une liste data qui contient les informations de position des joueurs,
    la carte mise à jour et les stats des joueurs mises à jour selon où ils ont marché.
    Cette liste est ensuite transmise au JavaScript via un socket.emit
    """
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
    """
    Requête door qui signifie que le joueur a amassé assez d'or pour révéler la porte secrète.
    On vérifie qu'elle n'est pas déjà révélée et on met à jour la carte avec la position de la porte.
    Cette position est envoyée vers le JavaScript.
    """
    if not game.door_revealed:
        x, y = game._generator.gen_door()
        game._map[y][x] = "D"
        game.door_revealed = True
        socketio.emit("door_response",[x,y])

@socketio.on("reset")
def reset(json):
    """
    Requête de réinitialisation de la partie.
    """
    game.reset(json)
    socketio.emit("reset_response")

@socketio.on("quit")
def quit():
    """
    Requête d'arrêt d'une partie solo.
    On effectue ici une sauvegarde de game via le module pickle qui serialise l'objet 
    pour pouvoir l'écrire dans un fichier externe 'save'.
    """
    with open('save', 'wb') as data:
        pickle.dump(game, data)
    socketio.emit("quit_response")
    return


@socketio.on("monster_move")
def monster_move():
    """
    Requête de mouvement des monstres. On impose que les monstres effectuent un mouvement
    toutes les 0.2 secondes au minimum. Cette condition n'est pas indispensable en solo, mais elle l'est
    en multi. En effet, la présence de plusieurs joueurs, donc plusieurs sessions implique qu'il y
    ait plusieurs codes JavaScript qui envoient des reqûetes de mouvement en même temps. 
    Toutes ces requêtes sont reçues par app.py qui les traite et renvoie le même nombre à chaque code JavaScript,
    et ainsi de suite. Le nombre de requêtes croit alors exponentiellement et entraîne un overload 
    (et des monstres qui se atteignent la vitesse de la lumière).
    Il est donc nécessaire d'imposer cette contrainte de temps via le module time.
    """
    global move_time
    if time()-move_time > 0.2:
        move_time = time()
        data_list = game.update_Monster()
        N = len(data_list)
        socketio.emit("monster_response", json.dumps([N,data_list]))

@socketio.on("monster_attack")
def monster_attack():
    """
    Requête d'attaque des monstres. On rencontre ici la même problématique qu'avec monster_move.
    On impose donc que les monstres attaquent toutes les 1.5 secondes au minimum.
    Cette attaque ne réussit que si le monstre est près du joueur.
    """
    global attack_time
    if time()-attack_time > 1.5:
        attack_time = time()
        for monster in game._Monster:
            for player in game.players:
                if monster.is_near_player(player):
                    player.health_points -= 10
                    data = data_actualize_construct(game)
                    socketio.emit('actualize', data)

@socketio.on("player_attack")
def player_attack():
    """
    Requête d'attaque des joueurs. On identifie d'abord quel joueur a lancé l'attaque,
    ensuite l'attaque ne réussit que si le joueur est face à un autre joueur ou face à un monstre.
    Si le joueur/monstre attaqué voit des HP tomber à 0, on le fait disparaître de la partie et on
    actualise la page via le socket.emit('actualize', data).
    """
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
            data = data_actualize_construct(game)
            socketio.emit('actualize', data)
    for i, other_player in enumerate(game.players):
        if [player._x + player._dx, player._y + player._dy] == [other_player._x,other_player._y]:
            other_player.health_points -= player.strength
            if other_player.health_points <= 0:
                other_player.die(game._map)
                game.players.remove(other_player)
                socketio.emit("player_die",[other_player._y, other_player._x, '.'])
            data = data_actualize_construct(game)
            socketio.emit('actualize', data)

if __name__=="__main__":
    socketio.run(app, port=5001, debug=True)

