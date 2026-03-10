from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.card import Card
from app.schemas.card import CardDetail, CardSummary, CardCreate, CardListResponse

router = APIRouter(prefix="/cards", tags=["Cards"])

VALID_RARITIES = ["N", "R", "SR", "SSR", "UR", "LR"]
VALID_TYPES    = ["AGL", "TEQ", "INT", "STR", "PHY"]


@router.get("/", response_model=CardListResponse, summary="Listar cartas")
def list_cards(
    page:       int            = Query(1,    ge=1,   description="Nmero de pgina"),
    per_page:   int            = Query(20,   ge=1, le=100, description="Resultados por pgina"),
    rarity:     Optional[str]  = Query(None, description=f"Filtrar por rareza: {VALID_RARITIES}"),
    type:       Optional[str]  = Query(None, description=f"Filtrar por tipo: {VALID_TYPES}"),
    is_lr:      Optional[bool] = Query(None, description="Solo cartas LR"),
    is_eza:     Optional[bool] = Query(None, description="Solo cartas con EZA"),
    is_dokkan_fest: Optional[bool] = Query(None, description="Solo Dokkan Festival"),
    db: Session = Depends(get_db)
):
    """
    Devuelve una lista paginada de cartas con filtros opcionales.
    """
    query = db.query(Card)

    if rarity:
        if rarity.upper() not in VALID_RARITIES:
            raise HTTPException(400, f"Rareza invlida. Opciones: {VALID_RARITIES}")
        query = query.filter(Card.rarity == rarity.upper())

    if type:
        if type.upper() not in VALID_TYPES:
            raise HTTPException(400, f"Tipo invlido. Opciones: {VALID_TYPES}")
        query = query.filter(Card.type == type.upper())

    if is_lr is not None:
        query = query.filter(Card.is_lr == is_lr)

    if is_eza is not None:
        query = query.filter(Card.is_eza == is_eza)

    if is_dokkan_fest is not None:
        query = query.filter(Card.is_dokkan_fest == is_dokkan_fest)

    total   = query.count()
    offset  = (page - 1) * per_page
    results = query.order_by(Card.id).offset(offset).limit(per_page).all()

    return CardListResponse(
        total=total,
        page=page,
        per_page=per_page,
        results=[CardSummary.model_validate(c) for c in results]
    )


@router.get("/search", response_model=CardListResponse, summary="Buscar cartas por nombre")
def search_cards(
    q:          str           = Query(..., min_length=2, description="Texto a buscar"),
    page:       int           = Query(1, ge=1),
    per_page:   int           = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Bsqueda de cartas por nombre, ttulo o nombre completo.
    """
    term = f"%{q}%"
    query = db.query(Card).filter(
        or_(
            Card.name.ilike(term),
            Card.title.ilike(term),
            Card.full_name.ilike(term),
        )
    )

    total   = query.count()
    offset  = (page - 1) * per_page
    results = query.order_by(Card.id).offset(offset).limit(per_page).all()

    return CardListResponse(
        total=total,
        page=page,
        per_page=per_page,
        results=[CardSummary.model_validate(c) for c in results]
    )


@router.get("/{card_id}", response_model=CardDetail, summary="Detalle de una carta")
def get_card(card_id: int, db: Session = Depends(get_db)):
    """
    Devuelve todos los datos de una carta por su ID.
    """
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(404, f"Carta con id={card_id} no encontrada.")
    return CardDetail.model_validate(card)


@router.post("/", response_model=CardDetail, status_code=201, summary="Crear carta")
def create_card(payload: CardCreate, db: Session = Depends(get_db)):
    """
    Crea una carta manualmente (tambin usado por el scraper).
    """
    card = Card(**payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return CardDetail.model_validate(card)


@router.put("/{card_id}", response_model=CardDetail, summary="Actualizar carta")
def update_card(card_id: int, payload: CardCreate, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(404, f"Carta con id={card_id} no encontrada.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(card, key, value)
    db.commit()
    db.refresh(card)
    return CardDetail.model_validate(card)


@router.delete("/{card_id}", status_code=204, summary="Eliminar carta")
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(404, f"Carta con id={card_id} no encontrada.")
    db.delete(card)
    db.commit()
