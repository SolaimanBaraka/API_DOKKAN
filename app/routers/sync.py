from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.card import Card
import logging

router = APIRouter(prefix="/sync", tags=["Sync"])
logger = logging.getLogger(__name__)

_sync_state = {"running": False, "last_run": None, "last_result": None}


def _upsert(cards_data: list, db: Session) -> dict:
    ins = upd = skip = 0
    valid = {c.name for c in Card.__table__.columns}
    for data in cards_data:
        clean = {k: v for k, v in data.items() if k in valid}
        wid = clean.get("wiki_id")
        if not wid:
            skip += 1; continue
        ex = db.query(Card).filter(Card.wiki_id == wid).first()
        if ex:
            for k, v in clean.items(): setattr(ex, k, v)
            upd += 1
        else:
            db.add(Card(**clean)); ins += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback(); logger.error(f"Commit error: {e}")
    return {"inserted": ins, "updated": upd, "skipped": skip}


def _job_rarity(rarity, max_cards, db):
    _sync_state["running"] = True
    try:
        from scraper.fandom_scraper import scrape_cards
        from datetime import datetime
        cards  = scrape_cards(rarity_filter=[rarity], max_cards=max_cards)
        result = _upsert(cards, db)
        _sync_state.update({"last_run": datetime.utcnow().isoformat(), "last_result": {**result, "rarity": rarity}})
    except Exception as e:
        logger.error(f"[SYNC] {e}", exc_info=True)
        _sync_state["last_result"] = {"error": str(e)}
    finally:
        _sync_state["running"] = False


def _job_character(name, db):
    _sync_state["running"] = True
    try:
        from scraper.fandom_scraper import scrape_character
        from datetime import datetime
        cards  = scrape_character(name)
        result = _upsert(cards, db)
        _sync_state.update({"last_run": datetime.utcnow().isoformat(), "last_result": {**result, "character": name}})
    except Exception as e:
        _sync_state["last_result"] = {"error": str(e)}
    finally:
        _sync_state["running"] = False


def _job_latest(pages_back, db):
    _sync_state["running"] = True
    try:
        from scraper.fandom_scraper import scrape_latest_cards
        from datetime import datetime
        cards  = scrape_latest_cards(pages_back=pages_back)
        result = _upsert(cards, db)
        _sync_state.update({"last_run": datetime.utcnow().isoformat(), "last_result": {**result, "mode": "latest"}})
    except Exception as e:
        _sync_state["last_result"] = {"error": str(e)}
    finally:
        _sync_state["running"] = False


#  Endpoints 

@router.get("/status", summary="Estado de la BD y ltimo sync")
def status(db: Session = Depends(get_db)):
    from app.models.event  import Event
    from app.models.banner import Banner
    from app.models.item   import Item
    return {
        "sync_running": _sync_state["running"],
        "last_sync":    _sync_state["last_run"],
        "last_result":  _sync_state["last_result"],
        "database": {
            "cards":   db.query(Card).count(),
            "events":  db.query(Event).count(),
            "banners": db.query(Banner).count(),
            "items":   db.query(Item).count(),
        },
        "cards_by_rarity": {r: db.query(Card).filter(Card.rarity == r).count() for r in ["N","R","SR","SSR","UR","LR"]},
        "cards_by_type":   {t: db.query(Card).filter(Card.type   == t).count() for t in ["AGL","TEQ","INT","STR","PHY"]},
    }


@router.get("/scheduler", summary="Estado del scheduler automtico")
def scheduler_info():
    """Informacin sobre el scheduler y el prximo sync programado."""
    from app.config import settings
    from app.main   import _scheduler
    from scraper.scheduler import sync_log

    next_run = None
    if _scheduler and _scheduler.running:
        job = _scheduler.get_job("daily_sync")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return {
        "enabled":       settings.SYNC_ENABLED,
        "schedule":      f"Diario a las {settings.SYNC_TIME_UTC} UTC",
        "rarities":      settings.SYNC_RARITIES,
        "max_cards":     settings.SYNC_MAX_CARDS,
        "scheduler_running": bool(_scheduler and _scheduler.running),
        "next_run":      next_run,
        "history":       sync_log[-10:],  # ltimas 10 ejecuciones
    }


@router.post("/cards/rarity/{rarity}", summary="Importar cartas por rareza")
def sync_rarity(
    rarity: str,
    max_cards: int = Query(50, ge=1, le=500, description="Mximo de cartas"),
    bt: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Scrapea la Fandom Wiki e importa cartas de la rareza indicada (LR, UR, SSR...)."""
    if rarity.upper() not in ["N","R","SR","SSR","UR","LR"]:
        raise HTTPException(400, f"Rareza invlida. Opciones: N, R, SR, SSR, UR, LR")
    if _sync_state["running"]:
        raise HTTPException(409, "Hay un sync en curso. Espera a que termine.")
    bt.add_task(_job_rarity, rarity.upper(), max_cards, db)
    return {"status": "iniciado", "rarity": rarity.upper(), "max_cards": max_cards, "tip": "GET /sync/status"}


@router.post("/cards/character/{name}", summary="Importar cartas de un personaje")
def sync_character(
    name: str,
    bt: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Scrapea todas las cartas de un personaje. Ej: Goku, Vegeta, Frieza, Gohan..."""
    if _sync_state["running"]:
        raise HTTPException(409, "Hay un sync en curso.")
    bt.add_task(_job_character, name, db)
    return {"status": "iniciado", "character": name}


@router.post("/cards/latest", summary="Importar cartas ms recientes")
def sync_latest(
    pages_back: int = Query(2, ge=1, le=5, description="Pginas a importar (~100 cartas/pgina)"),
    bt: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Importa las cartas ms recientes del ndice (novedades del juego)."""
    if _sync_state["running"]:
        raise HTTPException(409, "Hay un sync en curso.")
    bt.add_task(_job_latest, pages_back, db)
    return {"status": "iniciado", "approx_cards": pages_back * 100}


@router.post("/run-now", summary="Ejecutar sync automtico ahora mismo")
def run_now(bt: BackgroundTasks = BackgroundTasks(), db: Session = Depends(get_db)):
    """Dispara el mismo job que ejecuta el scheduler automtico, de forma inmediata."""
    if _sync_state["running"]:
        raise HTTPException(409, "Hay un sync en curso.")
    from scraper.scheduler import run_daily_sync
    bt.add_task(run_daily_sync)
    return {"status": "iniciado", "message": "Ejecutando sync completo (mismas rarezas que el scheduler)"}
