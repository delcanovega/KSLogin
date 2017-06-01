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

class WordsDoc(Document):
    config_database = 'kslogin'
    config_collection = 'words'

@app.route("/")
def index():
    # Pequeno 'about'
    return render_template("index.html")

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
        if values["collected"] == "DONE":
            return render_template("training_done.html")

        # Extraer features
        values["asked"] = request.form['asked']
        values["presd_k"] = request.form['presd_k']
        values["avg_key_dw"] = request.form['avg_key_dw']
        values["avg_flight"] = request.form['avg_flight']
        values["uses_mayus"] = request.form['uses_mayus']
        print values["presd_k"]
        values["over_keys"] = int(values["presd_k"]) - len(values["asked"])
        values["mistakes"] = compare_input(values["asked"], values["collected"])
        values["user"] = username

        # Almacenar features en mongodb
        with Mongo:
            DataDoc.insert(values)

        # Reiniciar values para seguir entrenando
        #values["presd_k"] = 0
        #values["avg_key_dw"] = 0
        #values["avg_flight"] = 0
        values["uses_mayus"] = 0
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
        #values["presd_k"] = 0
        #values["avg_key_dw"] = 0
        #values["avg_flight"] = 0
        values["uses_mayus"] = 0
        values["route"] = "/train/" + username
        # Formulario que te pida escribir una palabra (o frase)

        return render_template("training_form.html", vs = values)

def compare_input(target, word):
    mistakes = 0
    for i in range(0, min(len(word), len(target))):
        if (target[i] != word[i]):
            mistakes = mistakes + 1
    mistakes += max(len(word), len(target)) - min(len(word), len(target))

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
                ss += str(d["presd_k"])
                ss += ","
                ss += str(d["avg_key_dw"])
                ss += ","
                ss += str(d["avg_flight"])
                ss += ","
                ss += str(d["uses_mayus"])
                ss += ","
                ss += str(d["over_keys"])
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
        headers = ["user", "asked", "collected", "presd_k", "avg_key_dw",
                   "avg_flight", "uses_mayus", "over_keys", "mistakes"]
        data = pd.read_csv(location, names=headers)
        data = data.fillna(0)

        # Crear el clasificador y entrenarlo con los datos mas actualizados
        # (extraidos de mongodb)
        clf = generate_clf(data)
        joblib.dump(clf, 'rf_clf.pkl')

        values = {}
        values["presd_k"] = 0
        values["avg_key_dw"] = 0
        values["avg_flight"] = 0
        values["uses_mayus"] = 0
        with Mongo:
            js = WordsDoc.find_one(skip=randint(0, WordsDoc.count()))
            values["asked"] = js["value"]

        # Formulario que pida nombre de usuario y una palabra (o frase)
        return render_template("login_form.html", vs = values)

    if request.method == 'POST':
        # Extraer features
        v = {}
        v["collected"] = request.form['collected']
        v["asked"] = request.form['asked']
        v["presd_k"] = request.form['presd_k']
        v["avg_key_dw"] = request.form['avg_key_dw']
        v["avg_flight"] = request.form['avg_flight']
        v["uses_mayus"] = request.form['uses_mayus']
        v["over_keys"] = int(v["presd_k"]) - len(v["asked"])
        v["mistakes"] = compare_input(v["asked"], v["collected"])
        v["user"] = request.form['username']

        # Usar el clasificador para autenticar
        clf = joblib.load('rf_clf.pkl')

        req = np.array([v["avg_key_dw"], v["avg_flight"], v["uses_mayus"],
                        v["over_keys"], v["mistakes"]])
        req = req.reshape(1, -1)

        # Comprobar que coincidencia del usuario
        if clf.predict(req) == v["user"]:
            return "Login succesful"
        else:
            return "Access denied"
        return "POST"

def generate_clf(data):
    feature_cols = ['avg_key_dw', 'avg_flight', 'uses_mayus', 'over_keys', 'mistakes']
    X = data[feature_cols]
    y = data['user']

    clf = RandomForestClassifier(n_estimators=10)
    clf = clf.fit(X, y)

    return clf

if __name__ == "__main__":
    app.run(debug = True)
