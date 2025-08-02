from . import db
from flask_login import UserMixin # New import
from werkzeug.security import generate_password_hash, check_password_hash # New import
from . import login_manager # New import

# This function is required by Flask-Login to load a user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# New User class
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Existing Post class (no changes needed)
class Post(db.Model):
    drivers = db.Column(db.JSON) 
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    text = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    city = db.Column(db.String(100))
    emotion = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'text': self.text,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'emotion': self.emotion
        }