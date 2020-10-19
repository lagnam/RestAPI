from flask_restful import Resource, reqparse
from models.user import UserModel


class User(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'type',
        type=str,
        required=True,
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

        movie = UserModel(name, **data)
        movie.save_to_db()

        return movie.get_json(), 200



