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
    description = "REST API for Notes",
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

@api.route('/notes')
class NotesApi(Resource):
    """
    This resource handles the notes creation.

    Method Decorators:
        - authorize_user: Decorator to authorize user access.

    Methods:
        - POST: Create a new note with the provided title, description, reminder, and color.

    Request Body:
        - JSON object with the following fields:
            - title: string, required. The title of the note.
            - description: string, required. The description of the note.
            - reminder: string, optional. The reminder date/time for the note (format: YYYY-MM-DD HH:MM).
            - color: string, required. The color of the note.

    Responses:
        - 201: If the note is successfully created. Returns a success message, status code 201,
               and the created note data.
        - 400: If any unexpected error occurs during the creation process. Returns an error message and status code 400.
    """
    method_decorators = (authorize_user,)  
    @api.expect(api.model("register",{"title": fields.String(),"description": fields.String(),"reminder": fields.String(),"color": fields.String(),
            },))
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
        
    """
    This resource handles the retrieval of all notes registered by the user.

    Method Decorators:
        - authorize_user: Decorator to authorize user access.

    Methods:
        - GET: Retrieve notes for the specified user.

    Parameters:
        - user_id: int, required. The unique identifier of the user whose notes are to be retrieved.

    Responses:
        - 200: If notes are found for the user. Returns a success message, status code 200,
               and a list of note data.
        - 400: If the user ID is not provided or if no notes are found for the user. Returns an error message and status code 400.
        - 500: If any unexpected error occurs during the retrieval process. Returns an error message and status code 500.
    """
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
class NoteApiModification(Resource):
    """
    This resource handles the retrieval of a specific note.

    Method Decorators:
        - authorize_user: Decorator to authorize user access.

    Methods:
        - GET: Retrieve the note with the specified ID for the specified user.

    Parameters:
        - user_id: int, required. The unique identifier of the user.
        - note_id: int, required. The unique identifier of the note to be retrieved.

    Responses:
        - 200: If the note is found for the user. Returns a success message, status code 200,
               and the note data.
        - 400: If the user ID is not provided or if the note is not found for the user. Returns an error message and status code 400.
        - 500: If any unexpected error occurs during the retrieval process. Returns an error message and status code 500.
    """
    method_decorators = (authorize_user,)
    def get(self,*args,**kwargs):
        try:
            user_id = kwargs.get('user_id')
            if not user_id:
                return {'message':'userid not provided','status':400},400
            note=Notes.query.filter_by(user_id=user_id, id=kwargs.get('note_id')).all()
            if notes:
                return {'message':'notes found','status':200,'data':note.json},200
            return {'message':'Notes not found','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500
    
    """
    This resource handles the deletion of a specific note.

    Methods:
        - DELETE: Delete the note with the specified ID.

    Parameters:
        - note_id: int, required. The unique identifier of the note to be deleted.

    Responses:
        - 201: If the note is successfully deleted. Returns a success message and status code 201.
        - 400: If the note with the specified ID is not found. Returns an error message and status code 400.
        - 500: If any unexpected error occurs during the deletion process. Returns an error message and status code 500.
    """  
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

    
    
    """
    This resource handles the modification of a note identified by its ID.

    Methods:
        - PUT: Modify the note with the specified ID.

    Parameters:
        - note_id: int, required. The unique identifier of the note to be modified.

    Request Body:
        - title: str, required. The title of the note.
        - description: str, required. The description of the note.
        - reminder: str, optional. The reminder associated with the note.
        - color: str, optional. The color code associated with the note.

    Responses:
        - 200: If the note is successfully updated. Returns a success message and status code 200.
        - 400: If the note with the specified ID is not found or if there is a validation error in the request body. Returns an error message and status code 400.
        - 500: If any unexpected error occurs during the modification process. Returns an error message and status code 500.
    """
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
        
        
@api.route('/archive')
class ArchiveApi(Resource):
    """
    This resource handles archiving and unarchiving notes.

    Methods:
        - PUT: Archive or unarchive a note.

    Request Body:
        - note_id: int, required. The ID of the note to be archived or unarchived.

    Responses:
        - 200: If the note is successfully archived or unarchived. Returns a success message, status code 200, and the updated note data.
        - 404: If the note with the specified ID is not found. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    method_decorators = (authorize_user,)
    @api.expect(api.model('PutArchive', {"note_id":fields.Integer()}))
    def put(self,*args, **kwargs):
        try:
            data = request.json
            note=Notes.query.filter_by(note_id=data['note_id'],user_id=data['user_id']).first()
            if not note:
                return {"message":"Note not found","status": 404 },404
            note.is_archieve = True if not note.is_archieve else False
            db.session.commit()
            if not note.is_archieve:
                return {"message":" Note is unarchived","status":200,"data" :note.json},200
            return {"message" : "Note is archived","status": 200,"data" : note.json},200
        except ValueError as e:
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status" :500},500

    """
    This resource retrieves archived notes for a given user.

    Methods:
        - GET: Retrieve archived notes for the specified user.

    Parameters:
        - user_id: int, required. The ID of the user whose archived notes are to be retrieved.

    Responses:
        - 200: If archived notes are successfully retrieved. Returns a success message, status code 200, and the list of archived notes' data.
        - 404: If no archived notes are found for the specified user. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    def get(self,*args,**kwargs):
        try:
            user_id=kwargs["user_id"]
            notes=Notes.query.filter_by(user_id=user_id,is_archive=True, is_trash=False).all()
            if not notes:
                return {"message":"Notes not found","status": 404 },404
            return {"message":"Retrieved archive notes","status":200,"data":[note.json for note in notes]},200
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status" :500},500 


@api.route('/trash')
class TrashApi(Resource):
    """
    This resource handles moving notes to and from the trash.

    Methods:
        - PUT: Move a note to or restore it from the trash.

    Request Body:
        - note_id: int, required. The ID of the note to be moved to or restored from the trash.

    Responses:
        - 200: If the note is successfully moved to or restored from the trash. Returns a success message and status code 200.
        - 404: If the note with the specified ID is not found. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    method_decorators = (authorize_user,)
    @api.expect(api.model('PutTrash', {"note_id":fields.Integer()}))
    def put(self,*args, **kwargs):
        try:
            data = request.json
            note=Notes.query.filter_by(note_id=data['note_id'],user_id=data['user_id']).first()
            if not note:
                return {"message":"Note not found","status": 404 },404
            note.is_trash = True if not note.is_trash else False
            db.session.commit()
            if not note.is_trash:
                return {"message":" Note is restored successfully","status":200},200
            return {"message" : "Note moved to Trash","status": 200},200
        except ValueError as e:
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status" :500},500

    """
    This resource retrieves notes that are currently in the trash for a given user.

    Methods:
        - GET: Retrieve notes that are currently in the trash for the specified user.

    Parameters:
        - user_id: int, required. The ID of the user whose trashed notes are to be retrieved.

    Responses:
        - 200: If trashed notes are successfully retrieved. Returns a success message, status code 200, and the list of trashed notes' data.
        - 404: If no trashed notes are found for the specified user. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    def get(self,*args,**kwargs):
        try:
            user_id=kwargs["user_id"]
            notes=Notes.query.filter_by(user_id=user_id,is_trash=True, is_archive=False).all()
            if not notes:
                return {"message":"Notes not found","status": 404 },404
            return {"message":"Notes found","status":200,
                    "data":[note.json for note in notes]},200
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status" :500},500
      

@api.route("/collaborate")
class CollaborateApi(Resource):
    """
    This resource handles collaboration on notes, allowing users to share notes with other users.

    Methods:
        - POST: Share a note with other users.

    Request Body:
        - note_id: int, required. The ID of the note to be shared.
        - user_ids: list of int, required. The IDs of the users with whom the note will be shared.

    Responses:
        - 200: If the note is successfully shared. Returns a success message and status code 200.
        - 403: If sharing is not allowed with the same user. Returns an error message and status code 403.
        - 404: If the note or any of the specified users are not found. Returns an error message and status code 404.
        - 409: If there's an integrity error, such as duplicate entry. Returns an error message and status code 409.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
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
        
    """
    This resource handles removing collaborators from a note.

    Methods:
        - DELETE: Remove collaborators from a note.

    Request Body:
        - note_id: int, required. The ID of the note from which collaborators will be removed.
        - user_ids: list of int, optional. The IDs of the collaborators to be removed.
        - user_id: int, required. The ID of the user performing the operation.

    Responses:
        - 200: If collaborators are successfully removed from the note. Returns a success message and status code 200.
        - 403: If trying to remove oneself as a collaborator. Returns an error message and status code 403.
        - 404: If the note or any of the specified users are not found, or if a specified user is not a collaborator on the note. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
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
        
        
    """
    This resource retrieves all notes associated with a user, including notes owned by the user and notes shared with the user.

    Methods:
        - GET: Retrieve all notes associated with a user.

    Parameters:
        - user_id: int, required. The ID of the user whose notes are to be retrieved.

    Responses:
        - 200: If notes associated with the user are successfully retrieved. Returns a success message, status code 200, and the list of notes.
        - 400: If user ID is not provided. Returns an error message and status code 400.
        - 404: If the user is not found or if no notes are associated with the user. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
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

    
    

        

        
        
    