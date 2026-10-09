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
    environment: str = "development"
    frontend_url: str = "http://localhost:5175"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    stock_reservation_minutes: int = 30
    prices_include_tax: bool = True
    default_tax_rate: float = 0.19
    tax_rates: str = "CY:0.19,DE:0.19,FR:0.20,IT:0.22,ES:0.21,GR:0.24,NL:0.21,BE:0.21,AT:0.20,PT:0.23,IE:0.23,LU:0.17,MT:0.18"
    cors_origins: str = "http://localhost:5173,http://localhost:5175,http://127.0.0.1:5175"


settings = Settings()
