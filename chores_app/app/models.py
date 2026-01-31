from datetime import datetime
from .extensions import db

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.String(1024))
    history = db.Column(db.String(10240))

    def __repr__(self):
        return f"<Task {self.id} {self.title}>"
