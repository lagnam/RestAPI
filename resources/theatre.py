from flask_restful import Resource, reqparse
from models.theatre import TheatreModel


class Theatre(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'screens',
        type=int,
        required=True,
        help="Movie genre needs to be passed"
    )

    parser.add_argument(
        'location',
        type=str,
        required=True,
        help="Movie genre needs to be passed"
    )

    def get(self, name):
        theatre = TheatreModel.get_theatre(name=name)

        if theatre:
            return theatre.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Theatre.parser.parse_args()

        movie = TheatreModel(name, data["screens"], data["location"])
        movie.save_to_db()

        return movie.get_json(), 200
