from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
import json


#  EVENTS 

class EventBase(BaseModel):
    name: str
    type: Optional[str] = None
    is_active: bool = False
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class EventCreate(EventBase):
    wiki_id: Optional[str] = None
    description: Optional[str] = None
    difficulties: Optional[str] = None
    rewards: Optional[str] = None
    stamina_cost: Optional[int] = None
    image_url: Optional[str] = None
    wiki_url: Optional[str] = None


class EventResponse(EventCreate):
    id: int
    difficulties_list: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        if isinstance(obj.difficulties, str):
            try:
                instance.difficulties_list = json.loads(obj.difficulties)
            except Exception:
                instance.difficulties_list = []
        return instance


class EventListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    results: List[EventResponse]


#  BANNERS 

class BannerBase(BaseModel):
    name: str
    type: Optional[str] = None
    is_active: bool = False
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class BannerCreate(BannerBase):
    wiki_id: Optional[str] = None
    description: Optional[str] = None
    featured_cards: Optional[str] = None
    pool_cards: Optional[str] = None
    single_cost: Optional[int] = None
    multi_cost: Optional[int] = None
    rates: Optional[str] = None
    image_url: Optional[str] = None
    wiki_url: Optional[str] = None


class BannerResponse(BannerCreate):
    id: int
    featured_cards_list: Optional[List[Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        if isinstance(obj.featured_cards, str):
            try:
                instance.featured_cards_list = json.loads(obj.featured_cards)
            except Exception:
                instance.featured_cards_list = []
        return instance


class BannerListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    results: List[BannerResponse]


#  ITEMS 

class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    usable_in_battle: bool = False


class ItemCreate(ItemBase):
    wiki_id: Optional[str] = None
    description: Optional[str] = None
    effect: Optional[str] = None
    max_stack: Optional[int] = None
    how_to_obtain: Optional[str] = None
    image_url: Optional[str] = None
    wiki_url: Optional[str] = None


class ItemResponse(ItemCreate):
    id: int
    how_to_obtain_list: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        if isinstance(obj.how_to_obtain, str):
            try:
                instance.how_to_obtain_list = json.loads(obj.how_to_obtain)
            except Exception:
                instance.how_to_obtain_list = []
        return instance


class ItemListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    results: List[ItemResponse]
