from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120),nullable = False)
    email = db.Column(db.String(120),nullable = False)
    username = db.Column(db.String(120),nullable = False)
    password = db.Column(db.Text,nullable = False)



    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.filter_by(id = id).first()
    
    @classmethod
    def is_active(cls, username):
        user = cls.query.filter_by(username=username).first()
        if user:
            return user.active
        return None
    

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()






