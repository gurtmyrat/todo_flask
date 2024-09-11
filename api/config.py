from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODE: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SECRET_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".db.env"

settings = Settings()

#print("DATABASE_URL:", settings.DATABASE_URL)
#print("SECRET_KEY:", settings.SECRET_KEY)