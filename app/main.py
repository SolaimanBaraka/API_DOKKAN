import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config   import settings
from app.database import init_db
from app.routers  import cards, events, banners, items, sync as sync_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

_scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    init_db()
    if settings.SYNC_ENABLED:
        from scraper.scheduler import create_background_scheduler
        _scheduler = create_background_scheduler()
        _scheduler.start()
        logger.info(f"[OK] Scheduler activo  sync diario a las {settings.SYNC_TIME_UTC} UTC")
    else:
        logger.info("  Scheduler desactivado")
    yield
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)

app = FastAPI(
    title=" Dokkan Battle API",
    description="""
API no oficial de Dragon Ball Z: Dokkan Battle. Datos sincronizados automticamente desde la Fandom Wiki.

**Recursos:** Cards  Events  Banners  Items  Sync

**Filtros en /cards:** `rarity`  `type`  `is_lr`  `is_eza`  `is_dokkan_fest`

> WARNING: Proyecto fan-made.  Bandai Namco / Akatsuki.
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(events.router)
app.include_router(banners.router)
app.include_router(items.router)
app.include_router(sync_router.router)

@app.get("/", tags=["Root"])
def root():
    from app.database import SessionLocal
    from app.models.card import Card
    db = SessionLocal()
    n = db.query(Card).count()
    db.close()
    return {
        "name": "Dokkan Battle API", "version": "2.0.0",
        "environment": settings.APP_ENV, "docs": "/docs",
        "total_cards": n,
        "sync_schedule": f"Diario a las {settings.SYNC_TIME_UTC} UTC",
        "endpoints": {"cards":"/cards","events":"/events","banners":"/banners","items":"/items","sync":"/sync/status"},
    }

@app.get("/health", tags=["Root"])
def health():
    """Health check para Docker / load balancer."""
    try:
        from app.database import engine
        import sqlalchemy
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "scheduler": "running" if (_scheduler and _scheduler.running) else "stopped",
        "environment": settings.APP_ENV,
    }
