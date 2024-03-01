from pydantic_settings  import BaseSettings, SettingsConfigDict
from logging.config import dictConfig

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.Fundoo', extra='ignore')

    database_url: str
    base_url: str
    email_backend:str
    jwt_key: str
    jwt_algo: str
    email_username: str
    email_password: str
    
    redis_host:str
    redis_port:int
    redis_db:int
    
dictConfig(
{
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s]: %(filename)s: %(levelname)s: %(lineno)d: %(message)s",
            "datefmt": "%m/%d/%Y %I:%M:%S %p",
            "style": "%",
        },
        "console": {"format": "%(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "console",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "fundoo.log",
            "formatter": "default",
        },
    },
    # "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "": {"level": "DEBUG", "handlers": ["file", "console"], "propagate": True}
    },
}
)

settings = Settings()


