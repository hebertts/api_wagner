from flask import Flask, request, jsonify

app = Flask(__name__)

items = []

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    items.append(data)
    return jsonify({"message": "Item adicionado com sucesso!", "item": data}), 201

@app.route("/items/<int:index>", methods=["PUT"])
def update_item(index):
    if index < 0 or index >= len(items):
        return jsonify({"error": "Item não encontrado"}), 404
    data = request.get_json()
    items[index] = data
    return jsonify({"message": "Item atualizado!", "item": data})

@app.route("/items/<int:index>", methods=["DELETE"])
def delete_item(index):
    if index < 0 or index >= len(items):
        return jsonify({"error": "Item não encontrado"}), 404
    deleted = items.pop(index)
    return jsonify({"message": "Item removido!", "item": deleted})

if __name__ == "__main__":
    app.run(debug=True)
