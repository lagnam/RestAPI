from flask_restful import Resource, reqparse
from models.theatre import TheatreModel


class Theatre(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'screens',
        type=int,
        help="Movie genre needs to be passed"
    )

    parser.add_argument(
        'location',
        type=str,
        help="Movie genre needs to be passed"
    )

    parser.add_argument(
        'updated_name',
        type=str,
        help="Movie genre needs to be passed"
    )

    def get(self, name):
        theatre = TheatreModel.get_theatre(name=name)

        if theatre:
            return theatre.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Theatre.parser.parse_args()

        if not (data.get("screens") and data.get("location")):
            return {"error": "screes/location parameters are required for creating a theatre"}, 401

        movie = TheatreModel(name, data["screens"], data["location"])
        movie.save_to_db()

        return movie.get_json(), 200

    def put(self, name):
        data = Theatre.parser.parse_args()
        theatre = TheatreModel.get_theatre(name)

        if len(data) == 0:
            return {"error": "No data passed to update"}, 401
        elif list(data.keys()) not in list(theatre.__dict__.keys()):
            return {"error": f"Passed parameters doesn't match with the expected parameters:{list(theatre.__dict__.keys())}"}, 401

        if not theatre:
            return {"error": f"No theatre with the name {name}"}, 404

        theatre.__dict__.update(data)
        theatre.save_to_db()

        return None, 204

    def delete(self, name):
        theatre = TheatreModel.get_theatre(name)
        if not theatre:
            return {"error": f"No Theatre with the name {theatre}"}, 404

        theatre.delete_from_db()

        return None, 204
