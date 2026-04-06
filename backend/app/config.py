from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MONGODB_URI: str = ""
    DB_NAME: str = "cardionova"
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"       # ← ignores unknown vars like MONGO_URI, MODEL_PATH etc.
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
