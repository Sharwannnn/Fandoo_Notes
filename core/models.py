from core import db
from passlib.hash import pbkdf2_sha256
from datetime import datetime,timedelta,timezone
from flask_jwt_extended import create_access_token
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped


collaborators = db.Table(
    "collaborators",
    db.metadata,
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("note_id", db.ForeignKey("notes.note_id")),
    db.Column("access_type", db.String(20), default='read-only'),
    UniqueConstraint("user_id", "note_id", name="unique_user_note")
)

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    email=db.Column(db.String(150),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    location=db.Column(db.String(100),nullable=False)
    is_verified=db.Column(db.Boolean, default=False)
    note=db.relationship('Notes',back_populates='user')
    label=db.relationship('Label',back_populates='user')
    c_notes = db.relationship('Notes',secondary=collaborators, back_populates='c_users')

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
    c_users = db.relationship('User',secondary=collaborators,back_populates="c_notes")
    
    def __init__(self, title, description, color, user_id, reminder=None, **kwargs):
  
        self.title = title
        self.description = description
        self.color = color
        self.user_id = user_id
        self.is_archieve = False
        self.is_trash = False
        
        if reminder:
            self.set_reminder(reminder)
            
    def set_reminder(self, reminder):
        # Set the time zone to 'Asia/Kolkata'
        asia_kolkata_timezone = timezone(timedelta(hours=5, minutes=30))
        reminder = reminder.replace(tzinfo=asia_kolkata_timezone)

        # Assign the reminder time to the Notes object
        self.reminder = reminder

    def __str__(self) -> str:
        return f'{self.title}-{self.id}'

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
        

class Label(db.Model):
    __tablename__='labels'
    label_id=db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    name=db.Column(db.String(50), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user=db.relationship("User", back_populates="label")
    
    
    
    @property
    def json(self):
        return {
            "label_id":self.label_id,
            "name":self.name,
            "user_id":self.user_id,
        }