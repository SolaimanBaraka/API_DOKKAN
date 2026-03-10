"""
app/config.py

Configuracin central de la aplicacin.
Lee variables de entorno (o .env) y expone un objeto `settings`.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()  # carga .env si existe


class Settings:
    # Entorno
    APP_ENV: str        = os.getenv("APP_ENV", "development")

    # Base de datos
    POSTGRES_HOST: str  = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int  = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str    = os.getenv("POSTGRES_DB", "dokkan")
    POSTGRES_USER: str  = os.getenv("POSTGRES_USER", "dokkan")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "dokkan")

    # API
    API_HOST: str       = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int       = int(os.getenv("API_PORT", 8000))

    # Scheduler
    SYNC_TIME_UTC: str  = os.getenv("SYNC_TIME_UTC", "03:00")
    SYNC_RARITIES: list = os.getenv("SYNC_RARITIES", "LR,UR").split(",")
    SYNC_MAX_CARDS: int = int(os.getenv("SYNC_MAX_CARDS", 300))
    SYNC_ENABLED: bool  = os.getenv("SYNC_ENABLED", "true").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        """URL de conexin segn el entorno."""
        if self.APP_ENV == "production":
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        # Development  SQLite local
        return "sqlite:///./dokkan.db"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_sqlite(self) -> bool:
        return not self.is_production


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
