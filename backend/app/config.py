import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
    )
    # MySQL 连接（需安装 pymysql: pip install pymysql）
    # 格式: mysql+pymysql://user:pass@host:port/dbname
    database_url: str = "mysql+pymysql://root:root@localhost:3306/eshshop"
    secret_key: str = "change-this-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480


settings = Settings()
