from flask_restful import Resource, reqparse
from models.theatre import TheatreModel
from models.schedule import ScheduleModel


class Theatre(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("screens", type=int, help="Movie genre needs to be passed")

    parser.add_argument("location", type=str, help="Movie genre needs to be passed")

    parser.add_argument("name", type=str, help="Movie genre needs to be passed")

    def get(self, name):
        theatre = TheatreModel.get_theatre(name=name)

        if theatre:
            return theatre.get_json(), 200

        return {"error": f"No Movie with the name {name}"}, 404

    def post(self, name):
        data = Theatre.parser.parse_args()

        if not (data.get("screens") and data.get("location")):
            return {
                "error": "screes/location parameters are required for creating a theatre"
            }, 401
        elif data.get("screens") <= 0:
            return {"error": "Pass a valid screens number"}, 401

        movie = TheatreModel(name, data["screens"], data["location"])
        movie.save_to_db()

        return movie.get_json(), 200

    def put(self, name):
        data = Theatre.parser.parse_args()

        if len(data) == 0:
            return {"error": "No data passed to update"}, 401
        elif not set(data.keys()).issubset(set(theatre.__dict__.keys())):
            return {
                "error": f"Passed parameters doesn't match with the expected parameters:{list(theatre.__dict__.keys())}"
            }, 401

        theatre = TheatreModel.get_theatre(name)
        if not theatre:
            return {"error": f"No theatre with the name {name}"}, 404

        schedules = ScheduleModel.get_schedule(theatre_id=theatre.id)

        if data.get("screens"):
            if theatre.screens > data["screens"]:
                screens = []
                for schedule in schedules:
                    if schedule.screen not in screens and data["screens"] < schedule.screen:
                        screens.append(schedule.screen)

                if screens:
                    return {
                        "error": f"Delete schedule of theatre screens {screens}  before reducing the screens"
                    }, 404
            elif data["screens"] <= 0:
                return {"error": "Pass a valid screens number"}, 401

        theatre.__dict__.update(data)
        theatre.save_to_db()

        return None, 204

    def delete(self, name):
        theatre = TheatreModel.get_theatre(name)

        if not theatre:
            return {"error": f"No Theatre with the name {theatre}"}, 404

        schedules = ScheduleModel.get_schedule(theatre_id=theatre.id)
        if len(schedules) > 0:
            return {
                "error": f"Delete schedule of all the screens before deleting the theatre"
            }, 404

        theatre.delete_from_db()

        return None, 204
