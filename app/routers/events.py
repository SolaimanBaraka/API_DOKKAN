from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.event import Event
from app.schemas.other import EventResponse, EventCreate, EventListResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=EventListResponse, summary="Listar eventos")
def list_events(
    page:       int            = Query(1, ge=1),
    per_page:   int            = Query(20, ge=1, le=100),
    is_active:  Optional[bool] = Query(None, description="Solo eventos activos"),
    type:       Optional[str]  = Query(None, description="Filtrar por tipo de evento"),
    db: Session = Depends(get_db)
):
    """Lista eventos con filtros. Usa `is_active=true` para ver los eventos en curso."""
    query = db.query(Event)

    if is_active is not None:
        query = query.filter(Event.is_active == is_active)
    if type:
        query = query.filter(Event.type.ilike(f"%{type}%"))

    total   = query.count()
    offset  = (page - 1) * per_page
    results = query.order_by(Event.id.desc()).offset(offset).limit(per_page).all()

    return EventListResponse(
        total=total, page=page, per_page=per_page,
        results=[EventResponse.model_validate(e) for e in results]
    )


@router.get("/active", response_model=EventListResponse, summary="Eventos activos ahora")
def active_events(db: Session = Depends(get_db)):
    """Atajo rpido para ver todos los eventos activos en este momento."""
    results = db.query(Event).filter(Event.is_active == True).all()
    return EventListResponse(
        total=len(results), page=1, per_page=len(results) or 1,
        results=[EventResponse.model_validate(e) for e in results]
    )


@router.get("/{event_id}", response_model=EventResponse, summary="Detalle de evento")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, f"Evento con id={event_id} no encontrado.")
    return EventResponse.model_validate(event)


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, payload: EventCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, f"Evento con id={event_id} no encontrado.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404)
    db.delete(event)
    db.commit()
