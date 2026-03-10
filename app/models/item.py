from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id          = Column(Integer, primary_key=True, index=True)
    wiki_id     = Column(String(100), unique=True, index=True, nullable=True)

    name        = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Categora del item
    category    = Column(String(50), nullable=True, index=True)
    # Ej: recovery, training, awakening, summon, dragon_stone, orb, z_sword, etc.

    # Efecto del item
    effect      = Column(Text, nullable=True)

    # Se puede usar en batalla?
    usable_in_battle = Column(Boolean, default=False)
    max_stack   = Column(Integer, nullable=True)    # Cuntos se pueden guardar

    # Cmo obtenerlo? (JSON array)
    how_to_obtain = Column(Text, nullable=True)

    image_url   = Column(String(512), nullable=True)
    wiki_url    = Column(String(512), nullable=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
