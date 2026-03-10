"""
scraper/scheduler.py

Scheduler de sincronizacin automtica con la Fandom Wiki.
Usa APScheduler para ejecutar el sync diariamente a la hora configurada.

Puede correr de dos formas:
  1. Integrado en FastAPI (lifespan)  el mismo proceso
  2. Proceso separado  python -m scraper.scheduler
"""
import logging
import sys
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking  import BlockingScheduler
from apscheduler.triggers.cron        import CronTrigger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config   import settings
from app.database import SessionLocal, init_db
from app.models.card import Card

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

#  Estado del scheduler 

sync_log: list[dict] = []   # historial de ltimas ejecuciones


def _upsert_cards(cards_data: list, db) -> dict:
    inserted = updated = errors = 0
    valid_fields = {c.name for c in Card.__table__.columns}
    for data in cards_data:
        try:
            clean   = {k: v for k, v in data.items() if k in valid_fields}
            wiki_id = clean.get("wiki_id")
            if not wiki_id:
                continue
            existing = db.query(Card).filter(Card.wiki_id == wiki_id).first()
            if existing:
                for k, v in clean.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                db.add(Card(**clean))
                inserted += 1
        except Exception as e:
            logger.error(f"Error insertando carta: {e}")
            errors += 1
    db.commit()
    return {"inserted": inserted, "updated": updated, "errors": errors}


def run_daily_sync():
    """
    Job que se ejecuta automticamente cada da.
    Sincroniza las rarezas configuradas en SYNC_RARITIES.
    """
    if not settings.SYNC_ENABLED:
        logger.info("Sync automtico desactivado (SYNC_ENABLED=false)")
        return

    start = datetime.utcnow()
    logger.info(f"=== Iniciando sync automtico ===")
    logger.info(f"Rarezas: {settings.SYNC_RARITIES} | Max por rareza: {settings.SYNC_MAX_CARDS}")

    from scraper.fandom_scraper import scrape_cards

    total_result = {"inserted": 0, "updated": 0, "errors": 0, "rarezas": []}
    db = SessionLocal()

    try:
        for rarity in settings.SYNC_RARITIES:
            rarity = rarity.strip().upper()
            logger.info(f"--- Sincronizando {rarity} ---")
            try:
                cards = scrape_cards(
                    rarity_filter=[rarity],
                    max_cards=settings.SYNC_MAX_CARDS,
                )
                result = _upsert_cards(cards, db)
                total_result["rarezas"].append({rarity: result})
                total_result["inserted"] += result["inserted"]
                total_result["updated"]  += result["updated"]
                total_result["errors"]   += result["errors"]
                logger.info(f"{rarity}: {result}")
            except Exception as e:
                logger.error(f"Error en rareza {rarity}: {e}", exc_info=True)
                total_result["rarezas"].append({rarity: {"error": str(e)}})

        # Tambin sync de las cartas ms recientes (novedades)
        logger.info("--- Sincronizando novedades (latest) ---")
        from scraper.fandom_scraper import scrape_latest_cards
        latest = scrape_latest_cards(pages_back=1)
        latest_result = _upsert_cards(latest, db)
        logger.info(f"Latest: {latest_result}")
        total_result["latest"] = latest_result

    except Exception as e:
        logger.error(f"Error global en sync: {e}", exc_info=True)
        total_result["error"] = str(e)
    finally:
        db.close()

    duration = (datetime.utcnow() - start).total_seconds()
    total_result["duration_seconds"] = round(duration, 1)
    total_result["timestamp"] = start.isoformat()

    sync_log.append(total_result)
    if len(sync_log) > 30:   # Guardar solo ltimos 30
        sync_log.pop(0)

    logger.info(f"=== Sync completado en {duration:.1f}s: {total_result} ===")
    return total_result


def create_background_scheduler() -> BackgroundScheduler:
    """
    Crea un scheduler en background para integrarse con FastAPI.
    """
    hour, minute = settings.SYNC_TIME_UTC.split(":")
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_daily_sync,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_sync",
        name=f"Dokkan Wiki daily sync @ {settings.SYNC_TIME_UTC} UTC",
        replace_existing=True,
        misfire_grace_time=3600,   # si el job se pierde, reintenta 1h despus
    )
    logger.info(f"Scheduler configurado: sync diario a las {settings.SYNC_TIME_UTC} UTC")
    return scheduler


#  Ejecucin independiente 

if __name__ == "__main__":
    """
    Ejecutar como proceso separado:
        python -m scraper.scheduler

    Opciones:
        --now    ejecutar sync inmediatamente y salir
        --run    lanzar scheduler bloqueante (para Docker)
    """
    import argparse
    parser = argparse.ArgumentParser(description="Dokkan Battle Scheduler")
    parser.add_argument("--now",  action="store_true", help="Ejecutar sync ahora mismo")
    parser.add_argument("--run",  action="store_true", help="Lanzar scheduler continuo")
    args = parser.parse_args()

    init_db()

    if args.now:
        logger.info("Ejecutando sync manual...")
        result = run_daily_sync()
        logger.info(f"Resultado: {result}")
        sys.exit(0)

    elif args.run:
        hour, minute = settings.SYNC_TIME_UTC.split(":")
        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_job(
            run_daily_sync,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id="daily_sync",
            name=f"Daily sync @ {settings.SYNC_TIME_UTC} UTC",
            misfire_grace_time=3600,
        )
        logger.info(f"Scheduler activo. Prximo sync: {settings.SYNC_TIME_UTC} UTC diario.")
        logger.info("Ctrl+C para detener.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler detenido.")

    else:
        parser.print_help()
