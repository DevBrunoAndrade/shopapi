# ShopAPI – API REST de E-commerce

API REST desenvolvida com Python + Flask + PostgreSQL para gerenciamento de uma loja virtual.

## Stack
- Backend: Python + Flask
- Banco de Dados: PostgreSQL
- Autenticação: JWT (Flask-JWT-Extended)
- Segurança: bcrypt

## Funcionalidades
- Cadastro e login de usuários com JWT
- Listagem e cadastro de produtos
- Carrinho de compras
- Finalização de pedidos com controle de estoque

## Como rodar localmente
1. Clone o repositório
2. Crie o ambiente virtual: `python -m venv venv`
3. Ative: `venv\Scripts\activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e preencha as variáveis
6. Execute: `python run.py`
7. Acesse: `http://127.0.0.1:5000`

## Endpoints
| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | /auth/register | Cadastrar usuário | ❌ |
| POST | /auth/login | Login | ❌ |
| GET | /produtos/ | Listar produtos | ❌ |
| POST | /produtos/ | Criar produto | ✅ |
| GET | /produtos/:id | Buscar produto | ❌ |
| GET | /carrinho/ | Ver carrinho | ✅ |
| POST | /carrinho/ | Adicionar ao carrinho | ✅ |
| DELETE | /carrinho/:id | Remover do carrinho | ✅ |
| POST | /pedidos/ | Finalizar pedido | ✅ |
| GET | /pedidos/ | Histórico de pedidos | ✅ |