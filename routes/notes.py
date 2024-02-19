from core import db,init_app
from flask_restx import Api,Resource
from flask import request
from core.models import Notes
from pydantic import ValidationError
import json
from schemas.notes_schemas import NotesValidator
from flask_jwt_extended import decode_token


app=init_app()
api=Api(app=app,prefix='/api/notes')

@api.route('/notes')
class NotesApi(Resource):

    def post(self):
        try:
            Serializer=NotesValidator(**request.get_json())
            notes=Notes(**Serializer.model_dump())
            db.session.add(notes)
            db.session.commit()
            return {'message':"note created", "status": 201}, 201
        except Exception as e:
            return {'message':str(e), 'status':400},400
        
    

    def get(self):
        try:
            notes=Notes.query.filter_by().all()
            if notes:
                return {'message':[note.json for note in notes],'status':200},200
            return {'message':'Notes not found','status':400},400
        except Exception as e:
            return {'message':'something went wrong','status':500},500
        
@api.route('/notes/<int:note_id>')
class noteapi(Resource):

    def get(self,note_id):
        try:
            note=Notes.query.get(note_id)
            if not note:
                return {'message':'note not found','status':'400'},400
            return {'message':'note found','note':note.note_id,'status':'200'},200
        except Exception as e:
            return {'message':str(e),'status':400},400
        
    def delete(self,note_id):
        try:
            note=Notes.query.get(note_id)
            db.session.delete(note)
            db.session.commit()
            return {'message':"notes deleted", "status": 201}, 201
        except Exception as e:
            return {'message':str(e), 'status':400},400

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