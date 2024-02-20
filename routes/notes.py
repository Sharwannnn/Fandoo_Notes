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
        
    def put(self,*args,**kwargs):
        try:
            data=request.json
            note=Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
            if not note:
                return {'message':'note not found','status':'404'},404
                
            serializer=NotesValidator(**request.get_json())
            updated_data=serializer.model_dump()
            [setattr(note,key,value) for key, value in updated_data.items()]
            db.session.commit()
        except ValidationError as e:
            return {'message':'there is an validation error','status':400},400
        except Exception as e:
            return {'message':str(e),'status':500},500
        
@api.route('/notes/<int:note_id>')
class noteapi(Resource):

    method_decorators = (authorize_user,)

    def get(self,*args,**kwargs):
        try:
            note=Notes.query.filter_by(**kwargs).first()
            if not note:
                return {'message':'note not found','status':'400'},400
            return {'message':'note found','status':'200','note':note.json},200
        except Exception as e:
            return {'message':str(e),'status':500},500
        
    def delete(self,*args,**kwargs):
        try:
            note=Notes.query.filter_by(**kwargs).first()
            if not note:
                return {'message':'note not found','status':404},404
            db.session.delete(note)
            db.session.commit()
            return {'message':"notes deleted", "status": 204}, 204
        except Exception as e:
            return {'message':str(e), 'status':500},400

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
        
        
@api.route('/archive')
class ArchiveApi(Resource):

    method_decorators = (authorize_user,)

    def put(self, note_id):
        try:
            note = Notes.query.get(note_id)
            if not note:
                return {'message': 'note not found', 'status': 400}, 400
            note.archived = True
            db.session.commit()
            return {'message': 'note archived successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': 'something went wrong', 'status': 500}, 500


@api.route('/trash')
class TrashApi(Resource):

    method_decorators = (authorize_user,)

    def put(self, note_id):
        try:
            note = Notes.query.get(note_id)
            if not note:
                return {'message': 'note not found', 'status': 400}, 400
            note.trashed = True
            db.session.commit()
            return {'message': 'note moved to trash successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': 'something went wrong', 'status': 500}, 500