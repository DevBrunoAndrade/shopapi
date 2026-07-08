from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import JWT_SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

    jwt = JWTManager(app)

    # Registra as rotas
    from app.routes.auth import auth_bp
    from app.routes.produtos import produtos_bp
    from app.routes.carrinho import carrinho_bp
    from app.routes.pedidos import pedidos_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(produtos_bp, url_prefix="/produtos")
    app.register_blueprint(carrinho_bp, url_prefix="/carrinho")
    app.register_blueprint(pedidos_bp, url_prefix="/pedidos")

    return app