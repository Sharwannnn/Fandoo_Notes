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
from flask_restx import Api,Resource

app = init_app()
api=Api(app=app,prefix='/api/user')

@app.route('/')
def index():
    return {'message':'Fundoo Notes'}

@api.route("/register", methods=['POST'])
class UserApi(Resource):
    
    def post(self):
        try:
            Serializer = UserValidator(**request.get_json())
            user=User(**Serializer.model_dump())
            db.session.add(user)
            db.session.commit()
            token=user.token(aud='toVerify')
            send_mail(user.username, user.email, token)
            return {"message":"user registered", "status": 201, 'data': user.to_json}, 201
        except ValidationError as e:
            return {"message" : f'Invalid {"".join(json.loads(e.json())[0]["loc"])}', 'status': 400}, 400
        except Exception as e:
            return {"message" : str(e), 'status': 400}, 400


    def get(self):
        try:
            token = request.args.get('token')
            if not token:
                return {'msg': 'Token not found', 'status': 404}, 404
            payload = decode_token(token)
            user = User.query.filter_by(id=payload['sub']).first()
            if not user:
                return {'msg': 'User not found', 'status': 404}, 404
            user.is_verified = True
            db.session.commit()
            return {'message': 'User verified successfully', 'status': 200}, 200
        except JWTDecodeError:
            return {"message":"Unable to decode token","status": 400}, 400
        except Exception:
            return {"message":"Something went wrong","status": 400}, 400


@api.route("/login")
class LoginApi(Resource):
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