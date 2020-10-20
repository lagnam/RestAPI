from datetime import datetime

from flask_restful import Resource, reqparse

from models.movie import MovieModel
from models.theatre import TheatreModel
from models.schedule import ScheduleModel


class MovieSchedule(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument(
        "theatre", type=str, required=True, help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen", type=str, required=True, help="screen name needs to be passed"
    )

    parser.add_argument(
        "time", type=str, required=True, help="time name needs to be passed"
    )

    parser.add_argument(
        "updated_time", type=str, required=True, help="time name needs to be passed"
    )

    def get(self, movie_name):
        movie = MovieModel.get_movie(movie_name)

        if not movie:
            return {"error": "No movie found with this name"}, 404

        movie_schedules = ScheduleModel.get_schedule(movie_id=movie.id)
        result = {}

        for schedule in movie_schedules:
            theatre = TheatreModel.get_theatre_by_id(theatre_id=schedule.theatre_id)
            if result.get(theatre.name):
                result[theatre.name].append(schedule.time.strftime("%H:%M"))
            else:
                result[theatre.name] = [schedule.time.strftime("%H:%M")]

        return result, 200

    def post(self, movie_name):
        data = MovieSchedule.parser.parse_args()
        theatre_id = TheatreModel.get_theatre(name=data["theatre"]).id
        movie_id = MovieModel.get_movie(movie_name).id
        movie_time = datetime.strptime(data["time"], "%H:%M").time()

        schedule = ScheduleModel(
            theatre_id=theatre_id,
            movie_id=movie_id,
            time=movie_time,
            screen=data["screen"],
        )
        schedule.save_to_db()

        return {
            "movie": movie_name,
            "theatre": data["theatre"],
            "time": schedule.time,
        }, 201

    def put(self, name):
        data = MovieSchedule.parser.parse_args()
        if not {"theatre", "time", "updated_time"}.issubset(set(data.keys())):
            return {
                "error": "Theatre, time and updated_time are required for update"
            }, 401

        movie = MovieModel.get_movie(name)
        theatre = TheatreModel.get_theatre(data["theatre"])

        if not movie:
            return {"error": f"No movie with the name {name}"}, 404
        elif not theatre:
            return {"error": f"No theatre with the name {data['theatre']}"}, 404

        schedule = ScheduleModel.get_schedule()

        if not schedule:
            return {"error": f"No schedule with the passed data"}, 404

        schedule["time"] = data["updated_time"]
        schedule.save_to_db()

        return None, 204

    def delete(self, name):
        theatre = TheatreModel.get_theatre(name)
        if not theatre:
            return {"error": f"No Theatre with the name {theatre}"}, 404

        theatre.delete_from_db()

        return None, 204


class TheatreSchedule(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "movie", type=str, required=True, help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen", type=int, required=True, help="screen name needs to be passed"
    )

    parser.add_argument(
        "time", type=str, required=True, help="time name needs to be passed"
    )

    def get(self, theatre_name):
        theatre = TheatreModel.get_theatre(theatre_name)

        if not theatre:
            return {"error": f"No theatre found with the name {theatre.name}"}, 404

        theatre_schedules = ScheduleModel.get_schedule(theatre_id=theatre.id)
        result = {}

        for schedule in theatre_schedules:
            movie = MovieModel.get_movie_by_id(movie_id=schedule.movie_id)
            if result.get(movie.name):
                result[movie.name].append(schedule.time.strftime("%H:%M"))
            else:
                result[movie.name] = [schedule.time.strftime("%H:%M")]

        return result, 200

    def post(self, theatre_name):
        data = MovieSchedule.parser.parse_args()
        theatre_id = TheatreModel.get_theatre(name=theatre_name)
        movie_id = MovieModel.get_movie(name=data["movie"])
        movie_time = datetime.strptime(data["time"], "%H:%M").time()

        schedule = ScheduleModel(
            theatre_id=theatre_id,
            movie_id=movie_id,
            time=movie_time,
            screen=data["screen"],
        )
        schedule.save_to_db()

        return {
            "movie": data["movie"],
            "theatre": theatre_name,
            "time": schedule.time,
        }, 201
