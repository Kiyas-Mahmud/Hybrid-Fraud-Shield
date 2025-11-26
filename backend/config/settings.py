from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "fraud_detection"
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Card Data Encryption
    ENCRYPTION_KEY: str
    
    MODEL_PATH: str = "../model"
    ML_MODELS_PATH: str = "../Fusion_API/artifacts/ml"
    DL_MODELS_PATH: str = "../Fusion_API/artifacts/dl"
    HYBRID_MODELS_PATH: str = "../Fusion_API/artifacts/hybrid"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
