from flask import Flask, jsonify, request, render_template
from database import db
from models.user import User
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://admin:admin123@localhost:3306/flask-crud"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# View login
login_manager.login_view = "login"
# Session <- conexão ativa


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        # Login
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso!"})

    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})


@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"})

    return jsonify({"message": "Dados inválidos."}), 400


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = db.session.get(User, id_user)

    if user:
        return {"username": user.username}

    return jsonify({"message": "Usuário não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = db.session.get(User, id_user)
    if not user:
        return jsonify({"message": f"Usuário{id_user} NÃO encontrado."})
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if username and password:
        user.username = username
        user.password = password
        db.session.commit()
        return jsonify({"message": f"Usuário{id_user} atualizado com sucesso."})
    return jsonify({"message": "Dados de usuário inválido"})


@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = db.session.get(User, id_user)

    if id_user == current_user.id:
        return jsonify({"message": f"Deleção NÃO permitida."}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Úsuario {id_user} deletado com sucesso"})

    return jsonify({"message": f"Usuário{id_user} NÃO encontrado."}), 404


if __name__ == "__main__":
    app.run(debug=True)
