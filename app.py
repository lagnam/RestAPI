from flask import Flask
from flask_restful import Api

from resources import user, movie, theatre, schedule

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
api = Api(app)


api.add_resource(movie.Movie, "/movie/<string:name>")
api.add_resource(theatre.Theatre, "/theatre/<string:name>")
api.add_resource(user.User, "/user/<string:name>")
api.add_resource(schedule.TheatreSchedule, "/schedule/theatre/<string:theatre_name>")
api.add_resource(schedule.MovieSchedule, "/schedule/movie/<string:movie_name>")


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    from db import db

    db.init_app(app)
    app.run(port=5000, debug=True)
