from core import db
from core import init_app
from flask_restx import Api,Resource,fields
from flask import request
from core.models import Label
from pydantic import ValidationError
import json
from schemas.label_schemas import LabelValidator
from flask_jwt_extended import decode_token
from core.middleware import authorize_user

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


@api.route('/labels')
class LabelApi(Resource):

    method_decorators = (authorize_user,)
    
    @api.expect(
        api.model(
            "register",
            {
                "name": fields.String(),
            },
        )
    )

    def post(self, *args, **kwargs):
        try:
            serializer = LabelValidator(**request.get_json())
            label = Label(**serializer.model_dump())
            db.session.add(label)
            db.session.commit()
            return {'message': 'Label created', 'status': 201, 'data': label.json}, 201
        except Exception as e:
            return {'message': str(e), 'status': 400}, 400
        
        
    


@api.route('/labels/<int:label_id>')
class LabelApi(Resource):

    method_decorators = (authorize_user,)

    def get(self,*args,**kwargs):
        try:
            label = Label.query.filter_by(**kwargs).first()
            if not label:
                return {'message': 'Label not found', 'status': 404}, 404
            return {'message': 'Label found', 'status': 200, 'data': label.json}, 200
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500

    def put(self, label_id):
        try:
            label = Label.query.get(label_id)
            if not label:
                return {'message': 'Label not found', 'status': 404}, 404
            Serializer = LabelValidator(**request.get_json())
            updated_data = Serializer.model_dump()
            for key, value in updated_data.items():
                setattr(label, key, value)
            db.session.commit()
            return {'message': 'Label updated successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500

    def delete(self,*args,**kwargs):
        try:
            label = Label.query.filter_by(**kwargs).first()
            if not label:
                return {'message': 'Label not found', 'status': 404}, 404
            db.session.delete(label)
            db.session.commit()
            return {'message': 'Label deleted successfully', 'status': 204}, 204
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500