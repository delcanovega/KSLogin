# Libraries for the webapp
from flask import Flask, render_template, make_response
from flask import request
# Database
from humbledb import Mongo, Document
# Utilities
from time import time
from random import randint
# Machine learning
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

app = Flask(__name__)

class DataDoc(Document):
    config_database = 'kslogin'
    config_collection = 'data'

class UsersDoc(Document):
    config_database = 'kslogin'
    config_collection = 'users'

class WordsDoc(Document):
    config_database = 'kslogin'
    config_collection = 'words'

@app.route("/")
def index():
    # Pequeno 'about'
    # Accesos a /train y /login
    return "Work in progress"

@app.route("/initdb")
def init_db():
    # Iniciar base de datos
    words = ['Hipnotizar', 'Caballo', 'Hipopotamo', 'Elefante', 'Hipotalamo',
             'Camion', 'Radiador', 'Estercolero', 'KeyStrokeLogin', 'Perro',
             'Cantimplora', 'Estuche', 'Taquilla', 'Coquilla', 'Casillero',
             'Cuaderno', 'Portafolios', 'Portaminas', 'Comecocos', 'Agua',
             'Paraguero', 'Pinguino', 'Pantalones', 'Mocasines', 'Tirantes',
             'Mochila', 'Maletin', 'Escritorio', 'Pizarra', 'Contaminacion']
    for w in words:
        doc = WordsDoc()
        doc["value"] = w
        with Mongo:
            WordsDoc.insert(doc)
    return "Database initialized"

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
        with Mongo:
            js = WordsDoc.find_one(skip=randint(0,WordsDoc.count()))
            values["asked"] = js["value"]
        return render_template("training_form.html", vs = values)
    if request.method == 'GET':
        values = {}
        with Mongo:
            js = WordsDoc.find_one(skip=randint(0,WordsDoc.count()))
            values["asked"] = js["value"]
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

@app.route("/dump")
def dump():
    with Mongo:
        data = DataDoc.find()
        ss = ""
        for d in data:
            try:
                ss += d["user"]
                ss += ","
                ss += d["asked"]
                ss += ","
                ss += d["collected"]
                ss += ","
                ss += str(d["ellapsed"])
                ss += ","
                ss += str(d["mistakes"])
                ss += "\n"
            except Exception as e:
                pass
        output = make_response(ss)
        output.headers["Content-Disposition"] = "attatchment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
    return output

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        location = r'/home/jdelcano/Downloads/export.csv'
        headers = ["User", "Asked", "Collected", "Ellapsed", "Mistakes"]
        data = pd.read_csv(location, names=headers)
        # Crear el clasificador y entrenarlo con los datos mas actualizados
        # (extraidos de mongodb)
        clf = generate_clf(data)
        joblib.dump(clf, 'rf_clf.pkl')
        # Formulario que pida nombre de usuario y una palabra (o frase)
        # Iniciar timestamp
        values = {}
        values["timestamp"] = time()
        values["ellapsed"] = 0
        with Mongo:
            js = WordsDoc.find_one(skip=randint(0,WordsDoc.count()))
            values["asked"] = js["value"]
        return render_template("login_form.html", vs = values)
    if request.method == 'POST':
        values = {}
        values["collected"] = request.form['collected']
        values["asked"] = request.form['asked']
        values["ellapsed"] = time() - float(request.form['timestamp'])
        values["mistakes"] = compare_input(values["asked"], values["collected"])
        values["user"] = request.form['username']
        req = np.array([values["mistakes"], values["ellapsed"]/len(values["collected"])])
        req = req.reshape(1, -1)
        clf = joblib.load('rf_clf.pkl')
        if clf.predict(req) == values["user"]:
            return "Login succesful"
        else:
            return "Access denied"
        # Comprobar que coincidencia del usuario
        # Extraer features de la frase
        # Usar el clasificador para autenticar
        return "POST"

def generate_clf(data):
    data['SPC'] = data.apply (lambda row: get_spc(row),axis=1)
    feature_cols = ['Mistakes', 'SPC']
    X = data[feature_cols]
    y = data['User']

    clf = RandomForestClassifier(n_estimators=50)
    clf = clf.fit(X, y)
    return clf

# SPC: seconds per character
def get_spc(row):
    return row[3]/len(row[1])

if __name__ == "__main__":
    app.run(debug = True)
