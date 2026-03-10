from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id          = Column(Integer, primary_key=True, index=True)
    wiki_id     = Column(String(100), unique=True, index=True, nullable=True)

    name        = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Tipo de banner
    type        = Column(String(50), nullable=True)
    # Ej: dokkan_fest, legendary_summon, new_year, anniversary, step_up, etc.

    # Fechas
    start_date  = Column(String(50), nullable=True)
    end_date    = Column(String(50), nullable=True)
    is_active   = Column(Boolean, default=False, index=True)

    # Personajes destacados (JSON array de card IDs o nombres)
    featured_cards  = Column(Text, nullable=True)
    # Todos los personajes del pool (JSON array)
    pool_cards      = Column(Text, nullable=True)

    # Coste por summon
    single_cost     = Column(Integer, nullable=True)    # Dragon Stones por single
    multi_cost      = Column(Integer, nullable=True)    # Dragon Stones por multi (x10)

    # Tasas de rareza (JSON)
    rates           = Column(Text, nullable=True)
    # Ej: {"SSR": "7.5%", "SR": "22.5%", "R": "70%"}

    image_url       = Column(String(512), nullable=True)
    wiki_url        = Column(String(512), nullable=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
