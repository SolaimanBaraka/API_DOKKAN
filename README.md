#  Dokkan Battle API  v2

API REST no oficial para Dragon Ball Z: Dokkan Battle.
**Python + FastAPI + PostgreSQL + Docker + Sync automtico diario.**

---

##  Inicio rpido

### Opcin A  Local (desarrollo, SQLite)
```bash
pip install -r requirements.txt
cp .env.example .env          # opcional, usa SQLite por defecto
python -m scraper.seed        # cargar datos de ejemplo
uvicorn app.main:app --reload
```
 API en **http://localhost:8000**  Swagger en **http://localhost:8000/docs**

---

### Opcin B  Docker (produccin, PostgreSQL)
```bash
cp .env.example .env
# Edita .env con tu contrasea de PostgreSQL

docker compose up --build -d
```
 API en **http://localhost:8000**
 PostgreSQL en **localhost:5432**

Para importar datos reales nada ms arrancar:
```bash
curl -X POST "http://localhost:8000/sync/cards/rarity/LR?max_cards=100"
curl -X POST "http://localhost:8000/sync/cards/rarity/UR?max_cards=200"
```

---

##  Endpoints

### Cartas
```
GET  /cards                     Lista paginada con filtros
GET  /cards/{id}                Detalle completo
GET  /cards/search?q=goku       Bsqueda por nombre
POST /cards                     Crear carta manualmente
PUT  /cards/{id}                Actualizar carta
DELETE /cards/{id}              Eliminar carta
```

**Filtros en `/cards`:**
| Parmetro | Valores |
|-----------|---------|
| `rarity` | N, R, SR, SSR, UR, LR |
| `type` | AGL, TEQ, INT, STR, PHY |
| `is_lr` | true / false |
| `is_eza` | true / false |
| `is_dokkan_fest` | true / false |
| `page` + `per_page` | paginacin |

### Otros recursos
```
GET  /events                    Eventos (filtro: is_active, type)
GET  /events/active             Solo activos ahora
GET  /banners                   Banners de summon
GET  /banners/active            Solo activos ahora
GET  /items                     Items del juego
```

### Sync & Scheduler
```
GET  /sync/status               Estado BD + ltimo sync
GET  /sync/scheduler            Info scheduler + prxima ejecucin + historial
POST /sync/cards/rarity/{r}     Importar por rareza (LR, UR, SSR...)
POST /sync/cards/character/{n}  Importar todas las cartas de un personaje
POST /sync/cards/latest         Importar cartas ms recientes
POST /sync/run-now              Ejecutar sync completo ahora mismo

GET  /health                    Health check (para Docker / balanceadores)
```

---

##  Sync automtico

La API incluye un **scheduler integrado** que sincroniza con la Fandom Wiki automticamente.

Configuracin en `.env`:
```env
SYNC_ENABLED=true
SYNC_TIME_UTC=03:00        # Hora UTC del sync diario
SYNC_RARITIES=LR,UR        # Rarezas a sincronizar
SYNC_MAX_CARDS=300         # Mximo por rareza
```

Ver estado del scheduler:
```bash
curl http://localhost:8000/sync/scheduler
#  prxima ejecucin, historial, config
```

---

##  Migraciones de BD (Alembic)

```bash
# Crear una nueva migracin tras cambiar un modelo
alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Ver historial de migraciones
alembic history

# Revertir ltima migracin
alembic downgrade -1
```

---

##  Docker  comandos tiles

```bash
docker compose up -d              # Arrancar en background
docker compose logs -f api        # Ver logs de la API
docker compose logs -f db         # Ver logs de PostgreSQL
docker compose down               # Parar todo
docker compose down -v            # Parar + borrar volmenes (borra la BD!)

# Conectar a PostgreSQL directamente
docker compose exec db psql -U dokkan -d dokkan

# Ejecutar sync manual dentro del contenedor
docker compose exec api python -m scraper.scheduler --now
```

---

##  Estructura del proyecto

```
dokkan-api/
 app/
    main.py          # FastAPI + scheduler integrado
    config.py        # Settings desde .env
    database.py      # SQLAlchemy (SQLite/PostgreSQL)
    models/          # Tablas: card, event, banner, item
    routers/         # Endpoints: cards, events, banners, items, sync
    schemas/         # Pydantic (validacin + respuestas JSON)
 scraper/
    fandom_scraper.py  # Scraper real de la Fandom Wiki
    scheduler.py       # Scheduler APScheduler
    seed.py            # Datos de ejemplo para desarrollo
 alembic/               # Migraciones de BD
 Dockerfile
 docker-compose.yml
 .env.example
 .gitignore
 requirements.txt
```

---

## WARNING: Disclaimer

Proyecto fan-made sin nimo de lucro.
Todos los derechos de Dragon Ball Z: Dokkan Battle  **Bandai Namco Entertainment**  **Akatsuki Inc.**
