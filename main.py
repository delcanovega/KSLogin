from flask import Flask, render_template
from flask import request
from time import time
from humbledb import Mongo, Document

app = Flask(__name__)

class DataDoc(Document):
    config_database = 'kslogin'
    config_collection = 'data'

class WordsDoc(Document):
    config_database = 'kslogin'
    config_collection = 'words'

@app.route("/")
def index():
    # Pequeno 'about'
    # Accesos a /train y /login
    # Iniciar base de datos
    words = ['Hipnotizar', 'Caballo', 'Hipopotamo', 'Elefante', 'Hipotalamo',
             'Camion', 'Radiador', 'Estercolero', 'KeyStrokeLogin', 'Perro',
             'Cantimplora', 'Estuche', 'Taquilla', 'Coquilla', 'Casillero',
             'Cuaderno', 'Portafolios', 'Portaminas', 'Comecocos', 'Agua',
             'Paraguero', 'Pinguino', 'Pantalones', 'Mocasines', 'Tirantes',
             'Mochila', 'Maletin', 'Escritorio', 'Pizarra', 'Contaminacion']

    return "Work in progress"

@app.route("/train")
def train():
    # Mostrar el nombre de los usuarios existentes
    # Acceso a /train/<username> (?)
    # Registrar nuevo usuario
    return render_template("train.html")

@app.route("/train/<username>", methods=["GET", "POST"])
def train_user(username):
    if request.method == 'POST':
        values = DataDoc()
        values["collected"] = request.form['collected']
        values["asked"] = request.form['asked']
        values["ellapsed"] = time() - float(request.form['timestamp'])
        if values["collected"] == "DONE":
            return render_template("training_done.html")
        # Extraer features
        values["mistakes"] = compare_input(values["asked"], values["collected"])
        values["user"] = username
        # Almacenar features en mongodb
        with Mongo:
            DataDoc.insert(values)
        # El clasificador se creara y entrenara en /login
        # Reiniciar values para seguir entrenando
        values["timestamp"] = time()
        values["ellapsed"] = 0
        values["route"] = "/train/" + username
        return render_template("training_form.html", vs = values)
    if request.method == 'GET':
        values = {}
        values["asked"] = "Perro"
        # Iniciar timestamp
        values["timestamp"] = time()
        values["ellapsed"] = 0
        values["route"] = "/train/" + username
        # Formulario que te pida escribir una palabra (o frase)
        return render_template("training_form.html", vs = values)

def compare_input(target, word):
    mistakes = 0
    for i in range(0, len(word)):
        if (i < len(target) and target[i] != word[i]):
            mistakes = mistakes + 1
        if (i >= len(target)):
            mistakes = mistakes + (len(word)-i)
            break
    return mistakes

def concatenate(time, mistakes, user):
    ss = ""
    ss += time
    ss += ";"
    ss += mistakes
    ss += ";"
    ss += user
    ss += "\n"
    return ss

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        # Crear el clasificador y entrenarlo con los datos mas actualizados
        # (extraidos de mongodb)
        # Formulario que pida nombre de usuario y una palabra (o frase)
        # Iniciar timestamp
        # return render_template("login_form.html")
        return "GET"
    if request.method == 'POST':
        # Comprobar que coincidencia del usuario con mongodb
        # Extraer features de la frase
        # Usar el clasificador para autenticar
        return "POST"

if __name__ == "__main__":
    app.run(debug = True)
