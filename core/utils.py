from . import mail
from flask_mail import Message
from settings import settings
import redis
import json

def send_mail(user, email, token):
    msg = Message('Hello from the other side!', 
                  sender=settings.email_username, 
                  recipients=[email])
    msg.body = f"Hey {user}, sending you this email from my Flask app, Click to verify" \
                f" http://127.0.0.1:5000/api/user/verify?token={token}"
    mail.send(msg)
    return "Message sent!"


class RedisUtils:
    redis = redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
    @classmethod
    def get(cls, key):
        return cls.redis.hgetall(key)
    @classmethod
    def delete(cls, key, field):
        cls.redis.hdel(key, field)
    @classmethod
    def save(cls, key, field, value):
        cls.redis.hset(key, field, value)
        
        