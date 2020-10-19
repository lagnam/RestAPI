from datetime import datetime

from flask_restful import Resource, reqparse

from models.movie import MovieModel
from models.theatre import TheatreModel
from models.schedule import ScheduleModel


class MovieSchedule(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument(
        "theatre",
        type=str,
        required=True,
        help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen",
        type=str,
        required=True,
        help="screen name needs to be passed"
    )

    parser.add_argument(
        "time",
        type=str,
        required=True,
        help="time name needs to be passed"
    )

    def get(self, movie_name):
        movie = MovieModel.get_movie(movie_name)

        if not movie:
            return {"error": "No movie found with this name"}, 404

        movie_schedules = ScheduleModel.get_movie_schedule(movie_id=movie.id)
        result = {}

        for schedule in movie_schedules:
            theatre = TheatreModel.get_theatre_by_id(theatre_id=schedule.theatre_id)
            result[theatre.name] = schedule.time.strftime("%H:%M")

        return result, 200

    def post(self, movie_name):
        data = MovieSchedule.parser.parse_args()
        theatre_id = TheatreModel.get_theatre(name=data["theatre"]).id
        movie_id = MovieModel.get_movie(movie_name).id
        movie_time = datetime.strptime(data["time"], "%H:%M").time()

        schedule = ScheduleModel(theatre_id=theatre_id, movie_id=movie_id, time=movie_time, screen=data["screen"])
        schedule.save_to_db()

        return None, 201


class TheatreSchedule(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "movie",
        type=str,
        required=True,
        help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen",
        type=int,
        required=True,
        help="screen name needs to be passed"
    )

    parser.add_argument(
        "time",
        type=str,
        required=True,
        help="time name needs to be passed"
    )

    def get(self, theatre_name):
        theatre = TheatreModel.get_theatre(theatre_name)

        if not theatre:
            return {"error": f"No theatre found with the name {theatre.name}"}, 404

        theatre_schedules = ScheduleModel.get_theatre_schedule(theatre_id=theatre.id)
        result = {}

        for schedule in theatre_schedules:
            movie = MovieModel.get_movie_by_id(movie_id=schedule.movie_id)
            result[movie.name] = schedule.time.strftime("%H:%M")

        return result, 200

    def post(self, theatre_name):
        data = MovieSchedule.parser.parse_args()
        theatre_id = TheatreModel.get_theatre(name=theatre_name)
        movie_id = MovieModel.get_movie(name=data["movie"])
        movie_time = datetime.strptime(data["time"], "%H:%M").time()

        schedule = ScheduleModel(theatre_id=theatre_id, movie_id=movie_id, time=movie_time, screen=data["screen"])
        schedule.save_to_db()

        return None, 201