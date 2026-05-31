from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Document Analyzer"
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: Optional[str] = None
    
    # Embedding Settings
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/legal_analyzer"
    
    # Auth
    JWT_SECRET_KEY: str = "change_this_in_production_extremely_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
