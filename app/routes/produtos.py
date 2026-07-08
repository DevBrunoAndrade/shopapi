from flask import Blueprint, request, jsonify
import psycopg2
from flask_jwt_extended import jwt_required
from app.config import DATABASE_URL

produtos_bp = Blueprint("produtos", __name__)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@produtos_bp.route("/", methods=["GET"])
def listar_produtos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.nome, p.descricao, p.preco, p.estoque, c.nome 
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    produtos = cur.fetchall()
    cur.close()
    conn.close()

    resultado = []
    for p in produtos:
        resultado.append({
            "id": p[0],
            "nome": p[1],
            "descricao": p[2],
            "preco": float(p[3]),
            "estoque": p[4],
            "categoria": p[5]
        })
    return jsonify(resultado), 200

@produtos_bp.route("/", methods=["POST"])
@jwt_required()
def criar_produto():
    data = request.get_json()
    nome = data.get("nome")
    descricao = data.get("descricao")
    preco = data.get("preco")
    estoque = data.get("estoque", 0)
    categoria_id = data.get("categoria_id")

    if not nome or not preco:
        return jsonify({"erro": "Nome e preço são obrigatórios"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (nome, descricao, preco, estoque, categoria_id)
        )
        produto_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Produto criado!", "id": produto_id}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@produtos_bp.route("/<int:id>", methods=["GET"])
def buscar_produto(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.nome, p.descricao, p.preco, p.estoque, c.nome 
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = %s
    """, (id,))
    p = cur.fetchone()
    cur.close()
    conn.close()

    if not p:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify({
        "id": p[0],
        "nome": p[1],
        "descricao": p[2],
        "preco": float(p[3]),
        "estoque": p[4],
        "categoria": p[5]
    }), 200