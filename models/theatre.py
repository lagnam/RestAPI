from db import db


class TheatreModel(db.Model):
    __tablename__ = "theatres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    screens = db.Column(db.Integer)
    location = db.Column(db.String(40))

    def __init__(self, name, screens, location):
        self.name = name
        self.screens = screens
        self.location = location

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_theatre(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_theatre_by_id(cls, theatre_id):
        return cls.query.filter_by(id=theatre_id).first()

    def get_json(self):
        return {"name": self.name, "screens": self.screens, "location": self.location}
