from db import db


class MovieModel(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    genre = db.Column(db.String(40))

    def __init__(self, name, genre):
        self.name = name
        self.genre = genre

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_movie(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_movie_by_id(cls, movie_id):
        return cls.query.filter_by(id=movie_id).first()

    def get_json(self):
        return {"name": self.name, "genre": self.genre}
