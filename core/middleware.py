from flask import request
from flask_jwt_extended import decode_token
from jwt import PyJWTError
from .models import User
def authorize_user(function):
    """
    This decorator authorizes users for accessing certain routes.

    Attributes:
        - function: The function to be decorated.

    Returns:
        - function: The wrapped function with authorization logic.

    Authorization Logic:
        - Checks for the presence of a token in the request headers.
        - Decodes the token to extract user information.
        - Retrieves the user from the database using the decoded user ID.
        - Updates the request data or keyword arguments with the user ID depending on the HTTP method.
        - Handles exceptions such as missing or invalid tokens.
    Responses:
        - 401: If the token is missing or invalid. Returns an error message and status code 401.
        - 404: If the user is not found in the database. Returns an error message and status code 404.
    """
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