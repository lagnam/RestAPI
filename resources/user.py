import logging

from flask_restful import Resource, reqparse
from models.user import UserModel

logger = logging.getLogger(__name__)


class User(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("type", type=str, help="Movie genre needs to be passed")
    parser.add_argument("name", type=str, help="Movie genre needs to be passed")

    def get(self, name):
        user = UserModel.get_user(name=name)

        if user:
            return user.get_json(), 200

        return {"error": f"No user with the name {user}"}, 404

    def post(self, name):
        logger.info("Validating request data")
        if UserModel.get_user(name):
            return {"error": f"User already existing with the name {name}"}, 400

        data = User.parser.parse_args()
        if not data.get("type"):
            return {"error": "type of user is not passed"}, 400

        data["name"] = name
        user = UserModel(**data)
        user.save_to_db()

        return user.get_json(), 201

    def put(self, name):
        data = User.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        logger.info("Validating request data")
        user = UserModel.get_user(name)
        if not user:
            return {"error": f"No user with the name {name}"}, 404

        if len(data) == 0:
            return {"error": "No data passed to update"}, 400

        for k, v in data.items():
            setattr(user, k, v)
        user.save_to_db()

        return None, 204
