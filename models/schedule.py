from db import db


class ScheduleModel(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    theatre_id = db.Column(db.Integer)
    screen = db.Column(db.Integer)
    # date = db.Column(db.Date)
    time = db.Column(db.Time)

    def __init__(self, movie_id, theatre_id, screen, time):
        self.movie_id = movie_id
        self.theatre_id = theatre_id
        self.screen = screen
        # self.date = date
        self.time = time

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_schedule(cls, **kwargs):
        query_result = cls.query.filter_by(**kwargs).order_by(ScheduleModel.time).all()
        return query_result
