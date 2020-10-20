from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    type = db.Column(db.String(40))

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_user(cls, name):
        return cls.query.filter_by(name=name).first()

    def get_json(self):
        return {"name": self.name, "type": self.type}
