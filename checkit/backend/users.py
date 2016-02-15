from checkit.server.api import get_db

db = get_db()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys}
