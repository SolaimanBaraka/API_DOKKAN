from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json


class CardBase(BaseModel):
    name: str
    title: Optional[str] = None
    full_name: Optional[str] = None
    rarity: Optional[str] = None
    type: Optional[str] = None
    cost: Optional[int] = None


class CardCreate(CardBase):
    wiki_id: Optional[str] = None
    hp_max: Optional[int] = None
    atk_max: Optional[int] = None
    def_max: Optional[int] = None
    hp_eza: Optional[int] = None
    atk_eza: Optional[int] = None
    def_eza: Optional[int] = None
    leader_skill: Optional[str] = None
    super_attack: Optional[str] = None
    ultra_super_attack: Optional[str] = None
    passive_skill: Optional[str] = None
    active_skill: Optional[str] = None
    active_skill_condition: Optional[str] = None
    eza_leader_skill: Optional[str] = None
    eza_passive_skill: Optional[str] = None
    eza_super_attack: Optional[str] = None
    categories: Optional[str] = None
    link_skills: Optional[str] = None
    awakening_medals: Optional[str] = None
    is_transformable: bool = False
    transforms_to_id: Optional[int] = None
    transformation_conditions: Optional[str] = None
    is_eza: bool = False
    is_lr: bool = False
    is_dokkan_fest: bool = False
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    wiki_url: Optional[str] = None


class CardSummary(CardBase):
    """Respuesta reducida para listados."""
    id: int
    is_lr: bool
    is_eza: bool
    is_dokkan_fest: bool
    is_transformable: bool
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None

    model_config = {"from_attributes": True}


class CardDetail(CardCreate):
    """Respuesta completa para detalle de carta."""
    id: int
    categories_list: Optional[List[str]] = None
    link_skills_list: Optional[List[str]] = None
    awakening_medals_list: Optional[List[dict]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        # Convertir JSON strings a listas/objetos
        if isinstance(obj.categories, str):
            try:
                instance.categories_list = json.loads(obj.categories)
            except Exception:
                instance.categories_list = []
        if isinstance(obj.link_skills, str):
            try:
                instance.link_skills_list = json.loads(obj.link_skills)
            except Exception:
                instance.link_skills_list = []
        if isinstance(obj.awakening_medals, str):
            try:
                instance.awakening_medals_list = json.loads(obj.awakening_medals)
            except Exception:
                instance.awakening_medals_list = []
        return instance


class CardListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    results: List[CardSummary]
