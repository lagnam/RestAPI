from datetime import datetime
import logging

from db import db
from exceptions import *

logger = logging.getLogger(__name__)


class ScheduleModel(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'))
    screen = db.Column(db.Integer)
    # date = db.Column(db.Date)
    time = db.Column(db.Time)

    def __init__(self, movie_id, theatre_id, screen, time):
        self.movie_id = movie_id
        self.theatre_id = theatre_id
        self.screen = screen
        # self.date = date
        self.time = datetime.strptime(time, "%H:%M").time()

    def save_to_db(self):
        logger.info("saving object to db")
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        logger.info("deleting object from db")
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_schedule(cls, **kwargs):
        try:
            if kwargs.get("time"):
                kwargs["time"] = datetime.strptime(kwargs["time"], "%H:%M").time()
        except ValueError:
            logger.exception("Invalid time passed")
            raise InvalidTimeException("Invalid time format")
        query_result = cls.query.filter_by(**kwargs).order_by(ScheduleModel.time).all()
        return query_result
