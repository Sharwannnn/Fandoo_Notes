from pydantic_settings  import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.Fundoo', extra='ignore')

    database_url: str
    base_url: str
    email_backend:str
    jwt_key: str
    jwt_algo: str
    email_username: str
    email_password: str

settings = Settings()


