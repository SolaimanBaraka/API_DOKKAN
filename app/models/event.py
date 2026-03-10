from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    wiki_id     = Column(String(100), unique=True, index=True, nullable=True)

    name        = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Tipo de evento
    type        = Column(String(50), nullable=True)
    # Ej: story, dokkan, training, strike, special, boss_rush, world_tournament

    # Fechas (en texto para flexibilidad con formatos del juego)
    start_date  = Column(String(50), nullable=True)
    end_date    = Column(String(50), nullable=True)
    is_active   = Column(Boolean, default=False, index=True)

    # Dificultades disponibles (JSON array)
    difficulties = Column(Text, nullable=True)  # ["Normal","Hard","Super2","Z-Hard"]

    # Recompensas (JSON array de objetos)
    rewards     = Column(Text, nullable=True)

    # Stamina necesario
    stamina_cost = Column(Integer, nullable=True)

    image_url   = Column(String(512), nullable=True)
    wiki_url    = Column(String(512), nullable=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
