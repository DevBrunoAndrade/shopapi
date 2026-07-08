from flask import Blueprint, request, jsonify
import psycopg2
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config import DATABASE_URL

carrinho_bp = Blueprint("carrinho", __name__)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@carrinho_bp.route("/", methods=["GET"])
@jwt_required()
def ver_carrinho():
    usuario_id = get_jwt_identity()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, p.nome, p.preco, c.quantidade, (p.preco * c.quantidade) as subtotal
        FROM carrinho c
        JOIN produtos p ON c.produto_id = p.id
        WHERE c.usuario_id = %s
    """, (usuario_id,))
    itens = cur.fetchall()
    cur.close()
    conn.close()

    resultado = []
    total = 0
    for i in itens:
        subtotal = float(i[4])
        total += subtotal
        resultado.append({
            "carrinho_id": i[0],
            "produto": i[1],
            "preco": float(i[2]),
            "quantidade": i[3],
            "subtotal": subtotal
        })
    return jsonify({"itens": resultado, "total": total}), 200

@carrinho_bp.route("/", methods=["POST"])
@jwt_required()
def adicionar_ao_carrinho():
    usuario_id = get_jwt_identity()
    data = request.get_json()
    produto_id = data.get("produto_id")
    quantidade = data.get("quantidade", 1)

    if not produto_id:
        return jsonify({"erro": "produto_id é obrigatório"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        # Verifica se produto existe e tem estoque
        cur.execute("SELECT estoque FROM produtos WHERE id = %s", (produto_id,))
        produto = cur.fetchone()

        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404
        if produto[0] < quantidade:
            return jsonify({"erro": "Estoque insuficiente"}), 400

        # Verifica se já está no carrinho
        cur.execute("SELECT id, quantidade FROM carrinho WHERE usuario_id = %s AND produto_id = %s",
                    (usuario_id, produto_id))
        item = cur.fetchone()

        if item:
            # Atualiza quantidade
            cur.execute("UPDATE carrinho SET quantidade = %s WHERE id = %s",
                        (item[1] + quantidade, item[0]))
        else:
            # Adiciona novo item
            cur.execute("INSERT INTO carrinho (usuario_id, produto_id, quantidade) VALUES (%s, %s, %s)",
                        (usuario_id, produto_id, quantidade))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Produto adicionado ao carrinho!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@carrinho_bp.route("/<int:carrinho_id>", methods=["DELETE"])
@jwt_required()
def remover_do_carrinho(carrinho_id):
    usuario_id = get_jwt_identity()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM carrinho WHERE id = %s AND usuario_id = %s",
                    (carrinho_id, usuario_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Item removido do carrinho!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400