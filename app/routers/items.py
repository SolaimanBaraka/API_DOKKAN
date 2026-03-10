from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.item import Item
from app.schemas.other import ItemResponse, ItemCreate, ItemListResponse

router = APIRouter(prefix="/items", tags=["Items"])

ITEM_CATEGORIES = [
    "recovery", "training", "awakening", "summon",
    "dragon_stone", "orb", "z_sword", "other"
]


@router.get("/", response_model=ItemListResponse, summary="Listar items")
def list_items(
    page:       int            = Query(1, ge=1),
    per_page:   int            = Query(20, ge=1, le=100),
    category:   Optional[str]  = Query(None, description=f"Categora: {ITEM_CATEGORIES}"),
    usable_in_battle: Optional[bool] = Query(None, description="Solo items usables en batalla"),
    db: Session = Depends(get_db)
):
    query = db.query(Item)

    if category:
        query = query.filter(Item.category == category)
    if usable_in_battle is not None:
        query = query.filter(Item.usable_in_battle == usable_in_battle)

    total   = query.count()
    offset  = (page - 1) * per_page
    results = query.order_by(Item.name).offset(offset).limit(per_page).all()

    return ItemListResponse(
        total=total, page=page, per_page=per_page,
        results=[ItemResponse.model_validate(i) for i in results]
    )


@router.get("/{item_id}", response_model=ItemResponse, summary="Detalle de item")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, f"Item con id={item_id} no encontrado.")
    return ItemResponse.model_validate(item)


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, payload: ItemCreate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, f"Item con id={item_id} no encontrado.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404)
    db.delete(item)
    db.commit()
