from flask_restful import Resource, reqparse
from models.movie import MovieModel


class Movie(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        'genre',
        type=str,
        required=True,
        help="Movie genre needs to be passed"
    )

    def get(self, name):
        movie = MovieModel.get_movie(name=name)

        if movie:
            return movie.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Movie.parser.parse_args()

        movie = MovieModel(name, **data)
        movie.save_to_db()

        return movie.get_json(), 200
