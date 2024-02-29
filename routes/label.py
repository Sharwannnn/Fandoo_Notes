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
class LabelRegisterApi(Resource):
    """
    This resource handles the creation of labels.

    Methods:
        - POST: Create a new label.

    Request Body:
        - name: str, required. The name of the label.

    Responses:
        - 201: If the label is successfully created. Returns a success message, status code 201, and the created label data.
        - 400: If there is an error during label creation. Returns an error message and status code 400.
    """
    method_decorators = (authorize_user,)
    @api.expect(api.model("register",{"name": fields.String(),},))
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
    """
    This resource retrieves information about a specific label.

    Methods:
        - GET: Retrieve information about a specific label.

    Parameters:
        - label_id: int, required. The ID of the label to retrieve.

    Responses:
        - 200: If the label is found and successfully retrieved. Returns a success message, status code 200, and the label data.
        - 404: If the label with the specified ID is not found. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    method_decorators = (authorize_user,)

    def get(self,*args,**kwargs):
        try:
            label = Label.query.filter_by(**kwargs).first()
            if not label:
                return {'message': 'Label not found', 'status': 404}, 404
            return {'message': 'Label found', 'status': 200, 'data': label.json}, 200
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500

    
    """
    This resource handles the modification of a label.

    Methods:
        - PUT: Modify a label.

    Parameters:
        - label_id: int, required. The ID of the label to be modified.

    Request Body:
        - name: str, optional. The new name for the label.

    Responses:
        - 200: If the label is successfully updated. Returns a success message and status code 200.
        - 404: If the label with the specified ID is not found. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    @api.expect(api.model("register",{"name": fields.String(),},))
    def put(self,label_id, *args, **kwargs):
        try:
            label = Label.query.get(label_id=label_id, user_id=request.json.get('user_id'))
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
    

    """
    This resource handles the deletion of a label.

    Methods:
        - DELETE: Delete a label.

    Parameters:
        - label_id: int, required. The ID of the label to be deleted.

    Responses:
        - 200: If the label is successfully deleted. Returns a success message and status code 200.
        - 404: If the label with the specified ID is not found. Returns an error message and status code 404.
        - 500: If any unexpected error occurs during the process. Returns an error message and status code 500.
    """
    def delete(self,*args,**kwargs):
        try:
            label = Label.query.filter_by(**kwargs).first()
            if not label:
                return {'message': 'Label not found', 'status': 404}, 404
            db.session.delete(label)
            db.session.commit()
            return {'message': 'Label deleted successfully', 'status': 200}, 200
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500