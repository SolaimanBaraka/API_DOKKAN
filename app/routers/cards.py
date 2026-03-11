from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.database import get_db
from app.models.card import Card
from app.schemas.card import CardDetail, CardSummary, CardCreate, CardListResponse
import json

router = APIRouter(prefix="/cards", tags=["Cards"])

VALID_RARITIES = ["N", "R", "SR", "SSR", "UR", "LR"]
VALID_TYPES    = ["AGL", "TEQ", "INT", "STR", "PHY"]


@router.get("/categories", response_model=List[str], summary="Listar todas las categorías")
def list_categories(db: Session = Depends(get_db)):
    """
    Devuelve la lista de todas las categorías únicas presentes en la base de datos.
    Útil para saber qué valores usar en el filtro ?category=...
    """
    rows = db.query(Card.categories).filter(Card.categories.isnot(None)).all()
    seen = set()
    for (cats_json,) in rows:
        try:
            for cat in json.loads(cats_json):
                seen.add(cat)
        except Exception:
            pass
    return sorted(seen)


@router.get("/link-skills", response_model=List[str], summary="Listar todos los link skills")
def list_link_skills(db: Session = Depends(get_db)):
    """
    Devuelve la lista de todos los link skills únicos presentes en la base de datos.
    Útil para saber qué valores usar en el filtro ?link_skill=...
    """
    rows = db.query(Card.link_skills).filter(Card.link_skills.isnot(None)).all()
    seen = set()
    for (ls_json,) in rows:
        try:
            for ls in json.loads(ls_json):
                seen.add(ls)
        except Exception:
            pass
    return sorted(seen)


@router.get("/", response_model=CardListResponse, summary="Listar cartas")
def list_cards(
    page:       int            = Query(1,    ge=1,   description="Número de página"),
    per_page:   int            = Query(20,   ge=1, le=100, description="Resultados por página"),
    rarity:     Optional[str]  = Query(None, description=f"Filtrar por rareza: {VALID_RARITIES}"),
    type:       Optional[str]  = Query(None, description=f"Filtrar por tipo: {VALID_TYPES}"),
    is_lr:      Optional[bool] = Query(None, description="Solo cartas LR"),
    is_eza:     Optional[bool] = Query(None, description="Solo cartas con EZA"),
    is_dokkan_fest: Optional[bool] = Query(None, description="Solo Dokkan Festival"),
    is_transformable: Optional[bool] = Query(None, description="Solo cartas con transformación"),
    category:   Optional[str]  = Query(None, description="Filtrar por categoría (ej: 'Goku\\'s Family')"),
    link_skill: Optional[str]  = Query(None, description="Filtrar por link skill (ej: 'Super Saiyan')"),
    db: Session = Depends(get_db)
):
    """
    Devuelve una lista paginada de cartas con filtros opcionales.
    """
    query = db.query(Card)

    if rarity:
        if rarity.upper() not in VALID_RARITIES:
            raise HTTPException(400, f"Rareza inválida. Opciones: {VALID_RARITIES}")
        query = query.filter(Card.rarity == rarity.upper())

    if type:
        if type.upper() not in VALID_TYPES:
            raise HTTPException(400, f"Tipo inválido. Opciones: {VALID_TYPES}")
        query = query.filter(Card.type == type.upper())

    if is_lr is not None:
        query = query.filter(Card.is_lr == is_lr)

    if is_eza is not None:
        query = query.filter(Card.is_eza == is_eza)

    if is_dokkan_fest is not None:
        query = query.filter(Card.is_dokkan_fest == is_dokkan_fest)

    if is_transformable is not None:
        query = query.filter(Card.is_transformable == is_transformable)

    if category:
        # Búsqueda JSON: el valor aparece como cadena dentro del array JSON
        query = query.filter(Card.categories.contains(category))

    if link_skill:
        query = query.filter(Card.link_skills.contains(link_skill))

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
    Búsqueda de cartas por nombre, título o nombre completo.
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
    Crea una carta manualmente (también usado por el scraper).
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
