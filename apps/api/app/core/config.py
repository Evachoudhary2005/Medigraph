from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MediGraph"
    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"

    database_url: str = "sqlite:///./medigraph.db"

    jwt_secret: str = "change-me"
    jwt_alg: str = "HS256"
    jwt_expire_minutes: int = 60

settings = Settings()