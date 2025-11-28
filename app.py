from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flasgger import Swagger
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



# ---------------- CONFIGURAÇÕES ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///items.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "x"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# ---------------- SWAGGER 2.0 TEMPLATE ----------------
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API de Itens",
        "version": "1.0",
        "description": "Exemplo de API com JWT e Flasgger (Swagger 2.0)"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization header. Ex: "Bearer {token}"'
        }
    },
    "security": [{"Bearer": []}],
}

Swagger(app, template=swagger_template)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# ---------------- MODELO ----------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "preco": self.preco}


with app.app_context():
    db.create_all()


# ---------------- ROTAS DE AUTENTICAÇÃO ----------------
@app.route("/login", methods=["POST"])
def login():
    """
    Login para gerar token JWT
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [username, password]
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token gerado com sucesso
      400:
        description: Requisição inválida
      401:
        description: Credenciais inválidas
    """
    # tenta ler JSON de forma segura; se não tiver, tenta form-data
    data = request.get_json(silent=True)
    if not data and request.form:
        data = request.form.to_dict()

    if not data:
        return jsonify({"error": "Requisição inválida: envie JSON ou form-data com username e password"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username e password são obrigatórios"}), 400

    # Usuário fixo de exemplo (ideal: buscar no banco)
    if username == "admin" and password == "123":
        token = create_access_token(identity=username)
        return jsonify(access_token=token), 200

    return jsonify({"error": "Credenciais inválidas"}), 401


# ---------------- CRUD DE ITENS ----------------

@app.route("/items", methods=["GET"])
@jwt_required()
def get_items():
    """
    Retorna todos os itens cadastrados
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de itens
    """
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route("/items", methods=["POST"])
@jwt_required()
def add_item():
    """
    Adiciona um novo item
    ---
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [nome, preco]
          properties:
            nome:
              type: string
            preco:
              type: number
    responses:
      201:
        description: Item criado com sucesso
      400:
        description: Dados inválidos
    """
    data = request.get_json(silent=True)
    if not data and request.form:
        data = request.form.to_dict()

    if not data or "nome" not in data or "preco" not in data:
        return jsonify({"error": "Dados inválidos"}), 400

    item = Item(nome=data["nome"], preco=float(data["preco"]))
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item adicionado com sucesso!", "item": item.to_dict()}), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_item(item_id):
    """
    Atualiza um item existente
    ---
    security:
      - Bearer: []
    parameters:
      - in: path
        name: item_id
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            nome:
              type: string
            preco:
              type: number
    responses:
      200:
        description: Item atualizado
      404:
        description: Item não encontrado
    """
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404

    data = request.get_json(silent=True)
    if not data and request.form:
        data = request.form.to_dict()

    if data is None:
        data = {}

    item.nome = data.get("nome", item.nome)
    if "preco" in data:
        item.preco = float(data.get("preco", item.preco))
    db.session.commit()

    return jsonify({"message": "Item atualizado!", "item": item.to_dict()})


@app.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_item(item_id):
    """
    Remove um item
    ---
    security:
      - Bearer: []
    parameters:
      - in: path
        name: item_id
        type: integer
    responses:
      200:
        description: Item removido com sucesso
      404:
        description: Item não encontrado
    """
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removido!", "item": item.to_dict()})


# ---------------- EXECUÇÃO ----------------
if __name__ == "__main__":
    app.run(debug=True)