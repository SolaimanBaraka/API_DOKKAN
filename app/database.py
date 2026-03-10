"""
app/database.py

Configuracin de SQLAlchemy.
SQLite en development, PostgreSQL en production.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Argumentos de conexin especficos por driver
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # Pool settings (ignorados por SQLite)
    pool_pre_ping=True,       # detecta conexiones cadas
    pool_size=10,             # conexiones en el pool
    max_overflow=20,          # conexiones extra permitidas
) if not settings.is_sqlite else create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas si no existen."""
    from app.models import card, event, banner, item  # noqa
    Base.metadata.create_all(bind=engine)
    print(f"[OK] BD inicializada [{settings.APP_ENV}]: {settings.DATABASE_URL[:60]}...")
