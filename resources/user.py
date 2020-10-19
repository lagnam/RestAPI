from flask_restful import Resource, reqparse
from models.user import UserModel


class User(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'type',
        type=str,
        help="Movie genre needs to be passed"
    )

    parser.add_argument(
        'updated_name',
        type=str,
        help="Movie genre needs to be passed"
    )

    def get(self, name):
        user = UserModel.get_user(name=name)

        if user:
            return user.get_json(), 200

        return {"error": f"No user with the name {user}"}, 404

    def post(self, name):
        if UserModel.get_user(name):
            return {"error": f"User already existing with the name {name}"}, 400

        data = User.parser.parse_args()

        if not data.get("type"):
            return {"error": "type of user is not passed"}, 401

        user = UserModel(name, **data)
        user.save_to_db()

        return user.get_json(), 201

    def put(self, name):
        data = User.parser.parse_args()
        user = UserModel.get_user(name)

        if not data.get("updated_name"):
            return {"error": "updated_name parameter not passed"}, 401

        if len(data) == 0:
            return {"error": "No data passed to update"}, 401
        elif list(data.keys()) not in list(user.__dict__.keys()):
            return {"error": f"Passed parameters doesn't match with the expected parameters:{list(movie.__dict__.keys())}"}, 401

        if not user:
            return {"error": f"No user with the name {name}"}, 404

        user.__dict__.update(data)
        user.save_to_db()

        return None, 204

    def delete(self, name):
        user = UserModel.get_movie(name)
        if not user:
            return {"error": f"No Movie with the name {name}"}, 404

        user.delete_from_db()

        return None, 204

