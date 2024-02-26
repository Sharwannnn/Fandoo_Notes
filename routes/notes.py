from core import db
from core import init_app
from flask_restx import Api,Resource
from flask import request
from core.models import Notes
from pydantic import ValidationError
import json
from schemas.notes_schemas import NotesValidator
from flask_jwt_extended import decode_token
from core.middleware import authorize_user
from core.utils import RedisUtils

app=init_app()
api=Api(app=app,prefix='/api')

@api.route('/notes')
class NotesApi(Resource):

    method_decorators = (authorize_user,)

    def post(self,*args,**kwargs):
        try:
            Serializer=NotesValidator(**request.get_json())
            notes=Notes(**Serializer.model_dump())
            db.session.add(notes)
            db.session.commit()
            RedisUtils.save(f'user_{notes.user_id}', f'notes_{notes.note_id}', json.dumps(notes.json))
            return {'message':"note created", "status": 201,'data':notes.json}, 201
        except Exception as e:
            return {'message':str(e), 'status':400},400
        
    

    def get(self,*args,**kwargs):
        try:
            user_id = kwargs.get('user_id')
            if not user_id:
                return {'message':'userid not provided','status':400},400
            
            notes=Notes.query.filter_by(user_id=user_id).all()
            if notes:
                return {'message':'notes found','status':200,'data':[note.json for note in notes]},200
            return {'message':'Notes not found','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500

        
@api.route('/notes/<int:note_id>')
class noteapi(Resource):

    method_decorators = (authorize_user,)

    def get(self,*args,**kwargs):
        try:
            note=Notes.query.filter_by(**kwargs).first()
            if not note:
                return {'message':'Note not found','status':400},400
            return {'message':'Note found','status':200,'note':note.json},200
        except Exception as e:
            return {'message':str(e),'status':500},500
        
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

    def put(self,note_id):
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
    # @api.expect(api.model('AddColaborators', {"id":fields.Integer(),"user_ids":fields.List(fields.Integer)}))
    def post(*args, **kwargs):
        try:
            data=request.json
            if data['user_id'] in data["user_ids"]:
                return {"message":"Sharing not allowed on the same user","status":403},403
            note=Notes.query.filter_by(note_id=data["id"],user_id=data["user_id"]).first()
            if not note:
                return {"message":"Note not found","status":404},404
            try:
                users_to_add = [User.query.filter_by(id=id).first() for id in data["user_ids"]]
                existing_collaborators=set(note.c_users)
                users_to_add=[user for user in users_to_add if user not in existing_collaborators]
                note.c_users.extend(users_to_add)
                db.session.commit()
                added_users=[user.id for user in users_to_add]
                if added_users:
                    return {"message":f"Note_{note.note_id} shared with users {','.join(map(str,added_users))}", "status": 201},201
                return {"message" : "Note can't be shared with the users who already have access","status":403},403
            except sqlalchemy.exc.IntegrityError as e:
                    return {"message":str(e),"status":409},409
        except Exception as e:
            return {"message":str(e),"status" :500},500
