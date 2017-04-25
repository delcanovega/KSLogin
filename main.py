from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Pequeño 'about'
    # Accesos a /train y /login
    # Donaciones
    return "Work in progress"

@app.route("/train")
def train():
    # Mostrar el nombre de los usuarios existentes
    # Acceso a /train/<username> (?)
    # Registrar nuevo usuario
    return render_template("train.html")

@app.route("/train/<username>", methods=["GET", "POST"])
def train_user(username):
    if request.method == 'GET':
        # Formulario que te pida escribir una palabra (o frase)
        # Iniciar timestamp
    if request.method == 'POST':
        # Extraer features
        # Almacenar features en mongodb
        # El clasificador se creará y entrenará en /login

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        # Crear el clasificador y entrenarlo con los datos más actualizados
        # (extraidos de mongodb)
        # Formulario que pida nombre de usuario y una palabra (o frase)
        # Iniciar timestamp
        # return render_template("login_form.html")
    if request.method == 'POST':
        # Comprobar que coincidencia del usuario con mongodb
        # Extraer features de la frase
        # Usar el clasificador para autenticar

if __name__ == "__main__":
    app.run(debug = True)
