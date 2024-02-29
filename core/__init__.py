from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from settings import settings


db = SQLAlchemy()
migrate = Migrate()
jwt=JWTManager()
mail=Mail()


class Development:
    SQLALCHEMY_DATABASE_URI = settings.database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True

class Testing:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TESTING = True
    
class Production:
    SQLALCHEMY_DATABASE_URI = settings.database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = False   

config_mode = {
    "debug": Development,
    "testing": Testing,
    "production": Production
}


def init_app(mode='debug'):
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
    app.config.from_object(config_mode[mode])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['JWT_SECRET_KEY'] = settings.jwt_key
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=465
    app.config['MAIL_USE_SSL']= True
    app.config['MAIL_USERNAME']=settings.email_username
    app.config['MAIL_PASSWORD']=settings.email_password
    app.config.from_mapping(
        CELERY=dict(
        broker_url="redis://127.0.0.1:6379/0",
        result_backend="redis://127.0.0.1:6379/0",
        broker_connection_retry_on_startup=True,
        redbeat_redis_url = "redis://localhost:6379/0",
        redbeat_lock_key = None,
        enable_utc=False,
        beat_max_loop_interval=5,
        beat_scheduler='redbeat.schedulers.RedBeatScheduler'
        ),
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    with app.app_context():
        db.create_all()
    return app