import logging

from db import db

logger = logging.getLogger(__name__)


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    type = db.Column(db.String(40))

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def save_to_db(self):
        logger.info("saving object to db")
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_user(cls, name):
        return cls.query.filter_by(name=name).first()

    def get_json(self):
        return {"name": self.name, "type": self.type}
