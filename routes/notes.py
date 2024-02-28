from core import db
from core import init_app
from flask_restx import Api,Resource,fields
from flask import request
from core.models import Notes, User
from pydantic import ValidationError
import json
from schemas.notes_schemas import NotesValidator
from flask_jwt_extended import decode_token
from core.middleware import authorize_user
from core.utils import RedisUtils
from redbeat import RedBeatSchedulerEntry as Task
from celery.schedules import crontab
from core.tasks import celery as c_app
from datetime import datetime,timedelta,timezone
import sqlalchemy

app=init_app()

api = Api(
    app = app,
    prefix = "/api",
    doc = "/docs",
    security = "apiKey",
    description = "REST API for User Registrations and Notes",
    title = "Fundoo Notes API",
    default = "Notes Operations",
    default_label = "Register",
    authorizations = {
        "apiKey": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "required": True
        }
    },
      
)

# api=Api(app=app,prefix='/api')
@api.route('/notes')
class NotesApi(Resource):

    method_decorators = (authorize_user,)
    
    @api.expect(
        api.model(
            "register",
            {
                "title": fields.String(),
                "description": fields.String(),
                "reminder": fields.String(),
                "color": fields.String(),
            },
        )
    )
    
    def post(self,*args,**kwargs):
        try:
            Serializer=NotesValidator(**request.get_json())
            notes=Notes(**Serializer.model_dump())
            db.session.add(notes)
            db.session.commit()
            
            reminder=notes.reminder
            if reminder:
                reminder_task = Task(name=f'user_{notes.user_id} - note_{notes.note_id}',
                task='core.tasks.celery_send_mail',
                schedule = crontab(
                    minute=reminder.minute,
                    hour=reminder.hour,
                    day_of_month=reminder.day,
                    month_of_year=reminder.month),
                app = c_app,
                args = [notes.user.username, notes.user.email,notes.user.token()])
            
                reminder_task.save()
            
            RedisUtils.save(f'user_{notes.user_id}', f'notes_{notes.note_id}', json.dumps(notes.json))
            return {'message':"note created", "status": 201,'data':notes.json}, 201
        except Exception as e:
            return {'message':str(e), 'status':400},400
        
    

    def get(self,*args,**kwargs):
        try:
            user_id = kwargs.get('user_id')
            if not user_id:
                return {'message':'userid not provided','status':400},400
            user=User.query.filter_by(id=user_id).first()
            shared_notes=[note.json for note in user.c_notes]
            notes=Notes.query.filter_by(user_id=user_id).all()
            if notes:
                shared_notes.extend([note.json for note in notes])
                return {'message':'notes found','status':200,'data':[note.json for note in notes]},200
            return {'message':'Notes not found','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500

        
@api.route('/notes/<int:note_id>')
class noteapi(Resource):

    method_decorators = (authorize_user,)
    def get(self,*args,**kwargs):
        try:
            user_id = kwargs.get('user_id')
            if not user_id:
                return {'message':'userid not provided','status':400},400
            user=User.query.filter_by(id=user_id).first()
            shared_notes=[note.json for note in user.c_notes]
            notes=Notes.query.filter_by(user_id=user_id).all()
            if notes:
                shared_notes.extend([note.json for note in notes])
                return {'message':'notes found','status':200,'data':[note.json for note in notes]},200
            return {'message':'Notes not found','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500
        
    def delete(self, *args, **kwargs):
        try:
            note = Notes.query.filter_by(**kwargs).first()
            # print(note)
            if not note:
                return {'message': 'note not found', 'status': 400}, 400
            db.session.delete(note)
            db.session.commit()
            RedisUtils.delete(f'user_{note.user_id}', f'notes_{note.note_id}')
            return {'message': "note is sucessfully deleted", "status": 201}, 201
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500

    
    @api.expect(api.model("register",{"title": fields.String(),"description": fields.String(),"reminder": fields.String(),"color": fields.String(),},))
    def put(self,note_id, *args, **kwargs):
        try:
            note=Notes.query.get(note_id)
            if not note:
                return {'message':'note not found','status':400},400
            Serializer = NotesValidator(**request.get_json())
            updated_data=Serializer.model_dump()
            for key,value in updated_data.items():
                setattr(note,key,value)

            db.session.commit()
            return {'message':'note updated successfully','status':200},200
        except ValidationError as e:
            err=json.loads(e.json)
            return {'message':'wrong','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500
        
        
@api.route('/archive/<int:note_id>')
class ArchiveApi(Resource):

    method_decorators = (authorize_user,)

    def put(self, note_id):
        try:
            note = Notes.query.get(note_id)
            if not note:
                return {'message': 'note not found', 'status': 400}, 400
            note.is_archieve = True
            db.session.commit()
            return {'message': 'note archived successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': 'something went wrong', 'status': 500}, 500


@api.route('/trash/<int:note_id>')
class TrashApi(Resource):

    method_decorators = (authorize_user,)

    def put(self, note_id):
        try:
            note = Notes.query.get(note_id)
            if not note:
                return {'message': 'note not found', 'status': 400}, 400
            note.is_trash = True
            db.session.commit()
            return {'message': 'note moved to trash successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': 'something went wrong', 'status': 500}, 500
      
      

@api.route("/collaborate")
class CollaborateApi(Resource):
    method_decorators = (authorize_user,)
    @api.expect(api.model("register",{"note_id": fields.Integer(),"user_ids": fields.List(fields.Integer)},))
    def post(*args, **kwargs):
        try:
            data=request.json
            if data['user_id'] in data["user_ids"]:
                return {"message":"Sharing not allowed on the same user","status":403},403
            note=Notes.query.filter_by(note_id=data["note_id"],user_id=data["user_id"]).first()
            if not note:
                return {"message":"Note not found","status":404},404    
            for user_id in data["user_ids"]:
                user = User.query.filter_by(id=user_id).first()
                if not user:
                    return {"message":"User not found","status":404},404
                note.c_users.append(user)
            db.session.commit()
            return {"message" : "Note shared successfully","status":200 },200
        except sqlalchemy.exc.IntegrityError as e:
                return {"message":str(e),"status":409},409
        except Exception as e:
            return {"message":str(e),"status" :500},500
        

    def delete(self, **kwargs):
        try:
            data = request.json
            note_id = data.get('note_id')
            user_ids = data.get("user_ids", [])
            user_id = data.get('user_id')

            if user_id in user_ids:
                return {"message": "Cannot remove yourself", "status": 403}, 403

            note = Notes.query.filter_by(note_id=note_id).first()
            if not note:
                return {"message": "Note not found", "status": 404}, 404

            for user_id in user_ids:
                user = User.query.get(user_id)
                if user in note.c_users:
                    note.c_users.remove(user)
                else:
                    return {"message": f"User {user_id} not a collaborator", "status": 404}, 404

            db.session.commit()
            return {"message": "Collaborators removed successfully", "status": 200}, 200
        except Exception as e:
            return {"message": str(e), "status": 500}, 500
        
        
    
    def get(self,**kwargs):
        try:
            user_id = kwargs.get('user_id')
            if not user_id:
                return {'message': 'User ID not provided', 'status': 400}, 400

            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found', 'status': 404}, 404

            # Notes owned by the user
            user_notes = [note.json for note in user.note]

            # Notes shared to user
            shared_notes = [note.json for note in user.c_notes]
            all_notes = user_notes + shared_notes

            if all_notes:
                return {'message': 'Notes found', 'status': 200, 'data': all_notes}, 200
            else:
                return {'message': 'No notes found', 'status': 404}, 404

        except Exception as e:
            return {'message': str(e), 'status': 500}, 500

    
    

        

        
        
    