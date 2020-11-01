from datetime import datetime
import logging

from flask_restful import Resource, reqparse

from models.movie import MovieModel
from models.theatre import TheatreModel
from models.schedule import ScheduleModel
from exceptions import *

logger = logging.getLogger(__name__)


class TheatreSchedule(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "movie", type=str, help="theatre name needs to be passed"
    )

    parser.add_argument(
        "screen", type=int, help="screen name needs to be passed"
    )

    parser.add_argument(
        "time", type=str, help="time name needs to be passed"
    )

    parser.add_argument(
        "updated_time", type=str, help="time name needs to be passed"
    )

    def get(self, theatre_name):
        data = TheatreSchedule.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        logger.info("Validating request data")
        if "screen" in data or "time" in data:
            return {"error": "Display of only theatre schedule is allowed"}, 400
        elif len(data) > 1 or (len(data) == 1 and "movie" not in data):
            return {"error": "movie is only accepted as a valid parameter"}, 400

        theatre = TheatreModel.get_theatre(theatre_name)
        if not theatre:
            return {"error": f"No theatre found with the name {theatre_name}"}, 404
        elif data.get("movie"):
            movie = MovieModel.get_movie(name=data["movie"])
            if not movie:
                return {"error": f"No movie found with the name{data['movie']}"}, 404
            theatre_schedules = ScheduleModel.get_schedule(movie_id=movie.id, theatre_id=theatre.id)
        else:
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
        data = TheatreSchedule.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        logger.info("Validating request data")
        if not all(key in data for key in ['time', 'movie', 'screen']):
            return {"error": "['time', 'theatre', 'screen'] parameters required for creating a schedule"}, 400
        elif data["screen"] <= 0:
            return {"error": "Invalid screen number"}, 400

        theatre = TheatreModel.get_theatre(name=theatre_name)
        movie = MovieModel.get_movie(name=data["movie"])

        if not theatre:
            return {"error": f"No theatre found with the name {theatre_name}"}, 404
        elif not movie:
            return {"error": f"No movie found with the name {data['movie']}"}, 404
        elif theatre.screens < data["screen"]:
            return {"error": f"No such screen in theatre:{theatre}"}, 400

        try:
            result = ScheduleModel.get_schedule(
                theatre_id=theatre.id,
                movie_id=movie.id,
                screen=data["screen"],
                time=data["time"]
            )

            if result:
                logger.info("schedule not found")
                return {"error": f"No schedule with the passed data"}, 400

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
            "movie": data["movie"],
            "theatre": theatre_name,
            "time": schedule.time.strftime("%H:%M"),
        }, 201

    def put(self, theatre_name):
        data = TheatreSchedule.parser.parse_args()

        logger.info("Validating request data")
        if any(True for key, val in data.items() if val is None):
            return {
                       "error": f"{list(data.keys())} are required for updating schedule time"
                   }, 400

        theatre = TheatreModel.get_theatre(theatre_name)
        movie = MovieModel.get_movie(data["movie"])
        if not theatre:
            return {"error": f"No theatre found with the name {theatre_name}"}, 404
        elif not movie:
            return {"error": f"No movie with the name {data['movie']}"}, 404
        elif data["screen"] <= 0:
            return {"error": "Invalid screen number"}, 400
        elif theatre.screens < data["screen"]:
            return {"error": f"No such screen in theatre:{theatre}"}, 400

        try:
            result = ScheduleModel.get_schedule(
                theatre_id=theatre.id,
                movie_id=movie.id,
                screen=data["screen"],
                time=data["time"]
            )
            if not result:
                logger.info("schedule not found")
                return {"error": f"No schedule with the passed data"}, 404

            schedule = result[0]
        except InvalidTimeException:
            return {"error": "Invalid time format in updated_time"}, 400

        try:
            schedule.time = datetime.strptime(data['updated_time'], "%H:%M").time()
        except ValueError:
            return {"error": "Invalid time format"}, 400

        schedule.save_to_db()

        return None, 204

    def delete(self, theatre_name):
        data = TheatreSchedule.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        logger.info("Validating request data")
        if "time" in data and "movie" not in data and "screen" not in data:
            return {"error": "movie or screen not specified"}, 400

        theatre = TheatreModel.get_theatre(theatre_name)
        if not theatre:
            return {"error": f"No movie with the name {theatre_name}"}, 404
        elif data.get("movie"):
            movie = MovieModel.get_movie(data["movie"])
            if not movie:
                return {"error": f"No movie with the name {data['movie']}"}, 404
            del data["movie"]
            data["movie_id"] = movie.id
        elif data.get("updated_time"):
            return {"error": "Invalid parameter updated_time is passed"}, 400

        if data.get("screen") is not None:
            if data["screen"] <= 0:
                 return {"error": "Invalid screen number"}, 400
            elif theatre.screens < data["screen"]:
                 return {"error": f"No such screen in theatre:{theatre}"}, 404

        try:
            schedules = ScheduleModel.get_schedule(theatre_id=theatre.id, **data)
        except InvalidTimeException:
            return {"error": "Invalid time is passed"}, 400

        if not schedules:
            logger.info("schedule not found")
            return {"error": f"Schedule not found"}, 404

        for schedule in schedules:
            schedule.delete_from_db()

        return None, 204
