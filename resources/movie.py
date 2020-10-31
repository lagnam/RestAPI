from flask_restful import Resource, reqparse
from models.movie import MovieModel
from models.schedule import ScheduleModel


class Movie(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("genre", type=str, help="Movie genre needs to be passed")

    parser.add_argument("name", type=str, help="Movie genre needs to be passed")

    def get(self, name):
        movie = MovieModel.get_movie(name=name)

        if movie:
            return movie.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Movie.parser.parse_args()

        if not data.get("genre"):
            return {"error": "Genre parameter not passed"}, 400

        if MovieModel.get_movie(name):
            return {"error": f"Movie already exists with the name {name}"}, 400

        data = {k:v for k,v in data.items() if v is not None}
        movie = MovieModel(name, **data)
        movie.save_to_db()

        return movie.get_json(), 201

    def put(self, name):
        data = Movie.parser.parse_args()
        movie = MovieModel.get_movie(name)

        if not movie:
            return {"error": f"No movie with the name {name}"}, 404

        data = {k: v for k, v in data.items() if v is not None}

        if len(data) == 0:
            return {"error": "No data passed to update"}, 400

        for k, v in data.items():
            setattr(movie, k, v)
        movie.save_to_db()

        return None, 204

    def delete(self, name):
        movie = MovieModel.get_movie(name)

        if not movie:
            return {"error": f"No Movie with the name {name}"}, 404

        schedules = ScheduleModel.get_schedule(movie_id=movie.id)
        if len(schedules) > 0:
            return {
                "error": f"Delete schedule of the movie before deleting it"
            }, 400

        movie.delete_from_db()

        return None, 204
