from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.banner import Banner
from app.schemas.other import BannerResponse, BannerCreate, BannerListResponse

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.get("/", response_model=BannerListResponse, summary="Listar banners de summon")
def list_banners(
    page:       int            = Query(1, ge=1),
    per_page:   int            = Query(20, ge=1, le=100),
    is_active:  Optional[bool] = Query(None, description="Solo banners activos"),
    type:       Optional[str]  = Query(None, description="Filtrar por tipo: dokkan_fest, legendary, etc."),
    db: Session = Depends(get_db)
):
    """Lista todos los banners de invocacin. Filtrable por estado y tipo."""
    query = db.query(Banner)

    if is_active is not None:
        query = query.filter(Banner.is_active == is_active)
    if type:
        query = query.filter(Banner.type.ilike(f"%{type}%"))

    total   = query.count()
    offset  = (page - 1) * per_page
    results = query.order_by(Banner.id.desc()).offset(offset).limit(per_page).all()

    return BannerListResponse(
        total=total, page=page, per_page=per_page,
        results=[BannerResponse.model_validate(b) for b in results]
    )


@router.get("/active", response_model=BannerListResponse, summary="Banners activos ahora")
def active_banners(db: Session = Depends(get_db)):
    """Atajo rpido: banners de summon disponibles en este momento."""
    results = db.query(Banner).filter(Banner.is_active == True).all()
    return BannerListResponse(
        total=len(results), page=1, per_page=len(results) or 1,
        results=[BannerResponse.model_validate(b) for b in results]
    )


@router.get("/{banner_id}", response_model=BannerResponse, summary="Detalle de banner")
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(404, f"Banner con id={banner_id} no encontrado.")
    return BannerResponse.model_validate(banner)


@router.post("/", response_model=BannerResponse, status_code=201)
def create_banner(payload: BannerCreate, db: Session = Depends(get_db)):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return BannerResponse.model_validate(banner)


@router.put("/{banner_id}", response_model=BannerResponse)
def update_banner(banner_id: int, payload: BannerCreate, db: Session = Depends(get_db)):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(404, f"Banner con id={banner_id} no encontrado.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    db.commit()
    db.refresh(banner)
    return BannerResponse.model_validate(banner)


@router.delete("/{banner_id}", status_code=204)
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(404)
    db.delete(banner)
    db.commit()
