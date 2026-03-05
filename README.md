# QuantLab

Plataforma local de simulación de trading automático (paper trading) con datos reales (yfinance).  
Estrategias: SMA Crossover, RSI Mean Reversion. Comparador A vs B. Sin autenticación.

**Clasificación: Tier 3** (sin auth, sin datos personales) — Capa 0 Agencia FactorIA.

---

## Quick Start

### 1. Base de datos

```bash
cp .env.example .env
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Copiar .env del backend
cp .env.example .env

# Migraciones (crea tablas automáticamente al arrancar, alembic es opcional)
# alembic upgrade head

uvicorn quantlab.main:app --reload --port 8000
# → Docs en http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Build de producción (verifica TypeScript)

```bash
cd frontend
npm run build
```

---

## Estructura

```
quantlab/
├── backend/          FastAPI + SQLAlchemy + Alembic
│   └── src/quantlab/
│       ├── api/      rutas + schemas Pydantic
│       ├── domain/   estrategias, broker, métricas, entidades
│       ├── infrastructure/  DB, repos, yfinance
│       └── services/ orquestación
├── frontend/         React + Vite + MUI + Recharts
│   └── src/
│       ├── api/      client.ts (axios)
│       ├── components/common/
│       └── pages/
├── docker-compose.yml
└── .env.example
```

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/simulations/run` | Ejecuta simulación |
| GET  | `/simulations` | Lista simulaciones |
| GET  | `/simulations/{id}` | Detalle: métricas + equity + trades |
| GET  | `/simulations/compare/pair?a=1&b=2` | Comparador |
| GET  | `/health` | Health check |

## Tests

```bash
cd backend
pytest
```

## Variables de entorno

Ver `.env.example`. `DATABASE_URL` es obligatoria — la app no arranca sin ella.
