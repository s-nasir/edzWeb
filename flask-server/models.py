from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
 
# class UserCoach(db.Model):
#    __tablename__ = "usercoach"
#    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
#    email = db.Column(db.String(345), unique=True)
#    password = db.Column(db.Text(50), nullable=False)
#    phonenumber = db.Column(db.Integer(10), nullable=False)
#    experience = db.Column(db.Text(250), nullable=False)
