from datetime import datetime

from flask_restful import Resource, reqparse

from models.movie import MovieModel
from models.theatre import TheatreModel
from models.schedule import ScheduleModel
from exceptions import *


class MovieSchedule(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument(
        "theatre", type=str, help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen", type=int, help="screen name needs to be passed"
    )

    parser.add_argument(
        "time", type=str, help="time name needs to be passed"
    )

    parser.add_argument(
        "updated_time", type=str, help="updated_time name needs to be passed"
    )

    def get(self, movie_name):
        data = MovieSchedule.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        if "screen" in data or "time" in data:
            return {"error": "Display of only theatre schedule is allowed"}, 400
        elif len(data) > 1 or (len(data) == 1 and "theatre" not in data):
            return {"error": "theatre is only accepted as a valid parameter"}, 400

        movie = MovieModel.get_movie(movie_name)

        if not movie:
            return {"error": "No movie found with this name"}, 404

        if data.get("theatre"):
            theatre = TheatreModel.get_theatre(name=data["theatre"])
            if not theatre:
                return {"error": "No theatre found with this name"}, 404
            movie_schedules = ScheduleModel.get_schedule(movie_id=movie.id, theatre_id=theatre.id)
        else:
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
        data = {k: v for k, v in data.items() if v is not None}

        if not all(key in data for key in ['time', 'theatre', 'screen']):
            return {"error": "['time', 'theatre', 'screen'] parameters required for creating a schedule"}, 400
        elif data["screen"] <= 0:
            return {"error": "Invalid screen number"}, 400
        theatre = TheatreModel.get_theatre(name=data["theatre"])
        movie = MovieModel.get_movie(movie_name)

        if not movie:
            return {"error": f"No movie found with the name {movie_name}"}, 404
        elif not theatre:
            return {"error": f"No theatre found with the name {data['theatre']}"}, 404
        elif theatre.screens < data["screen"]:
            return {"error": f"No such screen in theatre:{theatre}"}, 400

        try:
            movie_schedule = ScheduleModel.get_schedule(
                theatre_id=theatre.id,
                movie_id=movie.id,
                time=data["time"],
                screen=data["screen"],
            )

            if movie_schedule:
                return {"error": "Schedule already exists"}, 400

            schedule = ScheduleModel(
                theatre_id=theatre.id,
                movie_id=movie.id,
                time=data["time"],
                screen=data["screen"],
            )
        except InvalidTimeException as e:
            return {"error": "Invalid time format"}, 400

        schedule.save_to_db()

        return {
            "movie": movie_name,
            "theatre": data["theatre"],
            "time": schedule.time.strftime("%H:%M"),
        }, 201

    def put(self, movie_name):
        data = MovieSchedule.parser.parse_args()

        if any(True for key, val in data.items() if val is None):
            return {
                "error": f"{list(data.keys())} are required for updating schedule time"
            }, 400

        movie = MovieModel.get_movie(movie_name)
        theatre = TheatreModel.get_theatre(name=data["theatre"])

        if not movie:
            return {"error": f"No movie with the name {movie_name}"}, 404
        elif not theatre:
            return {"error": f"No theatre found with the name {data['theatre']}"}, 404
        elif data["screen"] <= 0:
            return {"error": "Invalid screen number"}, 400
        elif theatre.screens < data["screen"]:
            return {"error": f"No such screen in theatre:{theatre}"}, 400

        try:
            result = ScheduleModel.get_schedule(
                movie_id=movie.id,
                theatre_id=theatre.id,
                screen=data["screen"],
                time=data["time"]
            )
            if not result:
                return {"error": f"No schedule with the passed data"}, 404
            schedule = result[0]
        except InvalidTimeException as e:
            return {"error": "Invalid time format"}, 400

        try:
            schedule.time = datetime.strptime(data['updated_time'], "%H:%M").time()
        except ValueError:
            return {"error": "Invalid time format"}, 400

        schedule.save_to_db()

        return None, 204

    def delete(self, movie_name):
        data = MovieSchedule.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        if "theatre" not in data:
            return {"error": "theatre is required for deleting the schedule"}, 400
        elif "time" in data and "screen" not in data:
            return {"error": "screen is required for deleting a specific time schedule"}, 400
        elif data.get("updated_time"):
            return {"error": "Invalid parameter updated_time is passed"}, 400

        movie = MovieModel.get_movie(movie_name)
        theatre = TheatreModel.get_theatre(name=data["theatre"])
        if not movie:
            return {"error": f"No movie with the name {movie_name}"}, 404
        elif not theatre:
            return {"error": f"No theatre found with the name {data['theatre']}"}, 404
        elif data.get("screen") is not None:
            if data["screen"] <= 0:
                 return {"error": "Invalid screen number"}, 400
            elif theatre.screens < data["screen"]:
                 return {"error": f"No such screen in theatre:{theatre}"}, 404

        del data["theatre"]
        data["theatre_id"] = theatre.id
        try:
            schedules = ScheduleModel.get_schedule(movie_id=movie.id, **data)
            if not schedules:
                return {"error": f"No schedule with the passed data"}, 404
        except InvalidTimeException as e:
            return {"error": "Invalid time format"}, 400

        for schedule in schedules:
            schedule.delete_from_db()

        return None, 204
