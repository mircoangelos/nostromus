from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://nostromus:nostromuspass@localhost:5432/nostromus"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Keycloak
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "react-keycloak"
    KEYCLOAK_CLIENT_ID: str = "FE-keycloak"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Environment
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
