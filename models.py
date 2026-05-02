from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    transcript = db.Column(db.Text)
    skill_score = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)