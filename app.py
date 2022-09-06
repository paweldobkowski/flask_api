from flask import Flask, request, jsonify
from flask_cors import CORS

from utilities import create_id
from models import db, User


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_table():
    db.create_all()

@app.route('/')
def main():
    d1 = {'endpoints': {
        '/add_user': 'for adding users (required: name, email) - METHOD = POST',
        '/users': 'query parameters are pageIndex (starts at 0) and pageSize, default are 0 and 5 - METHOD = GET',
        '/users/<id>': 'to get one user by id - METHOD = GET',
        '/delete_user': 'to delete user by id - METHOD = DELETE',
        '/edit_user': 'to edit the user by id (can edit id, name and email) - METHOD = POST'
    }}

    return jsonify(d1)

@app.route('/add_user', methods=['POST'])
def add_user():
    id = create_id(32)
    user = User(id=id, name=request.json['name'], email=request.json['email'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'id': user.id})

@app.route('/users')
def get_users():
    args = request.args
    pageIndex, pageSize = args.get("pageIndex", 0, type=int) + 1, args.get("pageSize", 5, type=int)

    users = User.query.paginate(page=pageIndex, per_page=pageSize)

    users_info = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users.items]
    pag_info = [{'total': users.total, 'pageIndex': pageIndex - 1, 'pageSize': pageSize, 'next': users.has_next, 'prev': users.has_prev, 'pageNumber': users.pages}]

    result = {
        'table': pag_info,
        'users': users_info,
    }

    return jsonify(result)

@app.route('/users/<id>')
def get_user(id):
    user = User.query.get_or_404(id)

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    id = request.json['id']

    user = User.query.get(id)
    if user is None:
        return jsonify({'error': 'user not found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'info': 'user deleted'})

@app.route('/edit_user', methods=['POST'])
def edit_user():
    id = request.json['id']

    user = User.query.get(id)
    if user is None:
        return jsonify({'error': 'user not found'})

    name = request.json['name']
    email = request.json['email']

    user.name = name
    user.email = email

    db.session.commit()

    return jsonify({'info': 'user updated'})

@app.route('/delete_all_users', methods=['DELETE'])
def delete_all_users():
    User.query.delete()
    db.session.commit()

    return jsonify({'info': 'all users deleted'})


if __name__ == '__main__':
    app.run(debug=True)
