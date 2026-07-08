from flask import Blueprint, request, jsonify
import psycopg2
import bcrypt
from flask_jwt_extended import create_access_token
from app.config import DATABASE_URL

auth_bp = Blueprint("auth", __name__)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    if not nome or not email or not senha:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        if not bcrypt.checkpw(senha.encode("utf-8"), usuario[2].encode("utf-8")):
            return jsonify({"erro": "Senha incorreta"}), 401

        token = create_access_token(identity=str(usuario[0]))
        return jsonify({"token": token, "nome": usuario[1]}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 