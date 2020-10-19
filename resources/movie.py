from flask_restful import Resource, reqparse
from models.movie import MovieModel


class Movie(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'genre',
        type=str,
        help="Movie genre needs to be passed"
    )

    parser.add_argument(
        'updated_name',
        type=str,
        help="Movie genre needs to be passed"
    )

    def get(self, name):
        movie = MovieModel.get_movie(name=name)

        if movie:
            return movie.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Movie.parser.parse_args()

        if not data.get("genre"):
            return {"error": "Genre parameter not passed"}, 401

        if MovieModel.get_movie(name):
            return {"error": f"Movie already exists with the name {name}"}, 401

        movie = MovieModel(name, **data)
        movie.save_to_db()

        return movie.get_json(), 200

    def put(self, name):
        data = Movie.parser.parse_args()
        movie = MovieModel.get_movie(name)

        if len(data) == 0:
            return {"error": "No data passed to update"}, 401
        elif list(data.keys()) not in list(movie.__dict__.keys()):
            return {"error": f"Passed parameters doesn't match with the expected parameters:{list(movie.__dict__.keys())}"}, 401

        if not movie:
            return {"error": f"No movie with the name {name}"}, 404

        movie.__dict__.update(data)
        movie.save_to_db()

        return None, 204

    def delete(self, name):
        movie = MovieModel.get_movie(name)
        if not movie:
            return {"error": f"No Movie with the name {name}"}, 404

        movie.delete_from_db()

        return None, 204
