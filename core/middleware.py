from flask import request
from flask_jwt_extended import decode_token
from jwt import PyJWTError
from .models import User
def authorize_user(function):
    def wrapper(*args,**kwargs):
        try:
            token=request.headers.get('Authorization')
            if not token:
                return {'message':'Token not found','status':404},404
            payload=decode_token(token)
            user=User.query.get(payload.get('sub'))
            if not user:
                return {'message':'user not found','status':404},404
            if request.method in ['PUT','POST']:
                request.json.update(user_id=user.id)
            else:
                kwargs.update(user_id=user.id)
        except PyJWTError as e:
            return {'message':'Invalid Token','status':401},401
        return function(*args,**kwargs)
    
    wrapper.__name__= function.__name__
    return wrapper