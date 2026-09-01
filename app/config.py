import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER: str = os.getenv("DATABASE_USERNAME", "postgres")
    DB_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")
    DB_HOST: str = os.getenv("DATABASE_HOSTNAME", "localhost")
    DB_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DB_NAME: str = os.getenv("DATABASE_NAME", "tasktracker")

    DATABASE_URL: str = os.getenv(
        "SQLALCHEMY_DATABASE_URL", 
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()