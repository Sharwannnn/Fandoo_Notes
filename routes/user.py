from core import db,init_app
from core.models import User    
from flask import request
from schemas.user_schemas import UserValidator
from pydantic import ValidationError
from flask import jsonify
import json
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
from core.utils import send_mail
from flask_restx import Api,Resource,fields
from core.tasks import celery_send_mail
from sqlalchemy.exc import IntegrityError


app = init_app()

api = Api(
    app = app,
    prefix = "/api",
    doc = "/docs",
    description = "REST API for User Registrations and Notes",
    title = "Fundoo Notes API",
    default = "Notes Operations",
    default_label = "Register_user",      
)


@app.route('/')
def index():
   return {'message':'Fundoo Notes'}

@api.route("/register")
class UserApi(Resource):
     
    @api.expect(api.model("register_user",{"username": fields.String(),"password": fields.String(),"email": fields.String(),"location": fields.String(),},))
    def post(self):
        try:
            Serializer = UserValidator(**request.get_json())
            user=User(**Serializer.model_dump())
            db.session.add(user)
            db.session.commit()
            token=user.token(aud='toVerify')
            # celery_send_mail.delay(user.username, user.email, token)
            return {"message":"user registered", "status": 201, 'data': user.to_json}, 201
        except ValidationError as e:
            return {"message" : f'Invalid {"".join(json.loads(e.json())[0]["loc"])}', 'status': 400}, 400
        except IntegrityError as e:
            return {"message": "Duplicate Username/Email", 'status':409}, 409
        except Exception as e:
            return {"message" : str(e), 'status': 400}, 400


@api.route('/register/<int:id>')
class UserDeleteAPI(Resource):
        
    def delete(self, *args, **kwargs):
        try:
            user = User.query.filter_by(**kwargs).first()
            if not user:
                return {'message': 'user not found', 'status': 400}, 400
            db.session.delete(user)
            db.session.commit()
            return {'message': "User is sucessfully deleted", "status": 201}, 201
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500


@api.route("/verify")
class UserVerifyAPI(Resource):
    @api.doc(params = {"token": "JWT token"})
    def get(self):
        try:
            token = request.args.get("token")
            if not token:
                return {'message': 'Token not provided', 'status': 400}, 400
            
            payload = decode_token(token)
            user = User.query.filter_by(id=payload['sub']).first()
            if not user:
                return {'message': 'User not found', 'status': 404}, 404
            
            if user.is_verified:
                return {'message': 'User already verified', 'status': 400}, 400
            
            user.is_verified = True
            db.session.commit()
            return {'message': 'User verified successfully', 'status': 200}, 200
        except JWTDecodeError:
            return {'message': 'Unable to decode token', 'status': 400}, 400
        except Exception as e:
            return {'message': str(e), 'status': 500}, 500


@api.route("/login")
class LoginApi(Resource):
    @api.expect(api.model("register",{"username": fields.String(),"password": fields.String(),},))   
    def post(self):
        try:
            data=request.get_json()
            user = User.query.filter_by(username=data["username"]).first()
            if user and user.verify_password(data["password"]):
                token=user.token(aud='toLogin', exp=60)
                return {"message":"login successful", "status": 200, 'token': token}, 200
            return {"message" : "Username or password is invalid", "status": 401}, 401
        except ValidationError as e:
            return {"message":f'Invalid {"".join(json.loads(e.json())[0]["loc"])}', 'status':400}, 400
        except Exception as e:
            return {"message":"Something was wrong", 'status':400}, 400