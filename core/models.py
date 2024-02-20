from core import db
from passlib.hash import pbkdf2_sha256
from datetime import datetime,timedelta
from flask_jwt_extended import create_access_token


class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    email=db.Column(db.String(150),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    is_verified=db.Column(db.Boolean, default=False)
    note=db.relationship('Notes',back_populates='user')

    def __init__(self,username,password,email,location,**kwargs):
        self.username=username
        self.password=pbkdf2_sha256.hash(password)
        self.email=email
        self.location=location

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    
    @property
    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "location": self.location
    }

    
    def token(self, aud='default', exp=60):
        return create_access_token(identity=self.id, 
                                   additional_claims={'exp':datetime.utcnow()+timedelta(minutes=exp), 
                                                      'aud': aud})
    
class Notes(db.Model):
    __tablename__='notes'
    note_id=db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    title=db.Column(db.String(50),nullable=True)
    description=db.Column(db.Text,nullable=False)
    color=db.Column(db.String(20))
    reminder=db.Column(db.DateTime,default=None,nullable=True)
    is_archieve=db.Column(db.Boolean,default=False)
    is_trash=db.Column(db.Boolean,default=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id',ondelete="CASCADE"),nullable=False)
    user=db.relationship('User',back_populates="note")

    @property
    def json(self):
        return {
            "note_id": self.note_id,
            "title":self.title,
            "description":self.description,
            "color":self.color,
            "reminder":self.reminder,
            "is_archieve":self.is_archieve,
            "is_trash":self.is_trash,
            "user_id":self.user_id,}