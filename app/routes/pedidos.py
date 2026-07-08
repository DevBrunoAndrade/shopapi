from flask import Blueprint, request, jsonify
import psycopg2
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config import DATABASE_URL

pedidos_bp = Blueprint("pedidos", __name__)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@pedidos_bp.route("/", methods=["POST"])
@jwt_required()
def finalizar_pedido():
    usuario_id = get_jwt_identity()

    try:
        conn = get_db()
        cur = conn.cursor()

        # Busca itens do carrinho
        cur.execute("""
            SELECT c.produto_id, c.quantidade, p.preco, p.estoque, p.nome
            FROM carrinho c
            JOIN produtos p ON c.produto_id = p.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
        itens = cur.fetchall()

        if not itens:
            return jsonify({"erro": "Carrinho vazio"}), 400

        # Calcula total
        total = sum(item[1] * float(item[2]) for item in itens)

        # Cria o pedido
        cur.execute(
            "INSERT INTO pedidos (usuario_id, total) VALUES (%s, %s) RETURNING id",
            (usuario_id, total)
        )
        pedido_id = cur.fetchone()[0]

        # Insere os itens do pedido e atualiza estoque
        for item in itens:
            produto_id, quantidade, preco, estoque, nome = item

            if estoque < quantidade:
                conn.rollback()
                return jsonify({"erro": f"Estoque insuficiente para {nome}"}), 400

            cur.execute("""
                INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, produto_id, quantidade, preco))

            cur.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s",
                        (quantidade, produto_id))

        # Limpa o carrinho
        cur.execute("DELETE FROM carrinho WHERE usuario_id = %s", (usuario_id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "mensagem": "Pedido realizado com sucesso!",
            "pedido_id": pedido_id,
            "total": total
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@pedidos_bp.route("/", methods=["GET"])
@jwt_required()
def listar_pedidos():
    usuario_id = get_jwt_identity()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.total, p.status, p.criado_em
        FROM pedidos p
        WHERE p.usuario_id = %s
        ORDER BY p.criado_em DESC
    """, (usuario_id,))
    pedidos = cur.fetchall()

    resultado = []
    for p in pedidos:
        cur.execute("""
            SELECT pr.nome, pi.quantidade, pi.preco_unitario
            FROM pedido_itens pi
            JOIN produtos pr ON pi.produto_id = pr.id
            WHERE pi.pedido_id = %s
        """, (p[0],))
        itens = cur.fetchall()

        resultado.append({
            "pedido_id": p[0],
            "total": float(p[1]),
            "status": p[2],
            "criado_em": str(p[3]),
            "itens": [{"produto": i[0], "quantidade": i[1], "preco_unitario": float(i[2])} for i in itens]
        })

    cur.close()
    conn.close()
    return jsonify(resultado), 200