import logging

from flask_restful import Resource, reqparse
from models.theatre import TheatreModel
from models.schedule import ScheduleModel

logger = logging.getLogger(__name__)


class Theatre(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("screens", type=int, help="Movie genre needs to be passed")

    parser.add_argument("location", type=str, help="Movie genre needs to be passed")

    parser.add_argument("name", type=str, help="Movie genre needs to be passed")

    def get(self, name):
        theatre = TheatreModel.get_theatre(name=name)

        if theatre:
            return theatre.get_json(), 200

        return {"error": f"No theatre with the name {name}"}, 404

    def post(self, name):
        data = Theatre.parser.parse_args()

        logger.info("Validating request data")
        if not (data.get("screens") and data.get("location")):
            return {
                "error": "screes/location parameters are required for creating a theatre"
            }, 400
        elif data.get("screens") <= 0:
            return {"error": "Pass a valid screens number"}, 400

        movie = TheatreModel(name, data["screens"], data["location"])
        movie.save_to_db()

        return movie.get_json(), 201

    def put(self, name):
        data = Theatre.parser.parse_args()
        data = {k: v for k, v in data.items() if v is not None}

        logger.info("Validating request data")
        theatre = TheatreModel.get_theatre(name)
        if not theatre:
            return {"error": f"No theatre with the name {name}"}, 404

        if len(data) == 0:
            return {"error": "No data passed to update"}, 400

        schedules = ScheduleModel.get_schedule(theatre_id=theatre.id)

        if data.get("screens") is not None:
            if data["screens"] <= 0:
                return {"error": "Pass a valid screens number"}, 400
            elif theatre.screens > data["screens"]:
                screens = []
                for schedule in schedules:
                    if schedule.screen not in screens and data["screens"] < schedule.screen:
                        screens.append(schedule.screen)

                if screens:
                    return {
                        "error": f"Delete schedule of theatre screens {screens}  before reducing the screens"
                    }, 400

        for k, v in data.items():
            setattr(theatre, k, v)
        theatre.save_to_db()

        return None, 204

    def delete(self, name):
        theatre = TheatreModel.get_theatre(name)

        logger.info("Validating request data")
        if not theatre:
            return {"error": f"No Theatre with the name {theatre}"}, 404

        schedules = ScheduleModel.get_schedule(theatre_id=theatre.id)
        if len(schedules) > 0:
            return {
                "error": f"Delete schedule of all the screens before deleting the theatre"
            }, 400

        theatre.delete_from_db()

        return None, 204
