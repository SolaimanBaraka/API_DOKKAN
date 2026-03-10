from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id          = Column(Integer, primary_key=True, index=True)
    wiki_id     = Column(String(50), unique=True, index=True, nullable=True)

    # Identificacin
    name        = Column(String(255), nullable=False, index=True)
    title       = Column(String(255), nullable=True)       # Ej: "Super Saiyan Goku"
    full_name   = Column(String(512), nullable=True)       # title + name

    # Clasificacin
    rarity      = Column(String(10),  nullable=True)       # N, R, SR, SSR, UR, LR
    type        = Column(String(10),  nullable=True)       # AGL, TEQ, INT, STR, PHY
    cost        = Column(Integer,     nullable=True)       # Coste del equipo

    # Stats base (nivel max sin awakening)
    hp_max      = Column(Integer, nullable=True)
    atk_max     = Column(Integer, nullable=True)
    def_max     = Column(Integer, nullable=True)

    # Stats EZA (Extreme Z-Awakening) si aplica
    hp_eza      = Column(Integer, nullable=True)
    atk_eza     = Column(Integer, nullable=True)
    def_eza     = Column(Integer, nullable=True)

    # Habilidades
    leader_skill    = Column(Text, nullable=True)
    super_attack    = Column(Text, nullable=True)
    ultra_super_attack = Column(Text, nullable=True)
    passive_skill   = Column(Text, nullable=True)
    active_skill    = Column(Text, nullable=True)
    active_skill_condition = Column(Text, nullable=True)

    # Categoras y links (guardados como JSON string)
    categories      = Column(Text, nullable=True)   # JSON array
    link_skills     = Column(Text, nullable=True)   # JSON array

    # Transformaciones
    is_transformable    = Column(Boolean, default=False)
    transforms_to_id    = Column(Integer, nullable=True)

    # Meta
    is_eza          = Column(Boolean, default=False)
    is_lr           = Column(Boolean, default=False)
    is_dokkan_fest  = Column(Boolean, default=False)
    image_url       = Column(String(512), nullable=True)
    wiki_url        = Column(String(512), nullable=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # Fechas de lanzamiento
    jp_release_date  = Column(String(20), nullable=True)
    glb_release_date = Column(String(20), nullable=True)
