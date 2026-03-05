# QuantLab — Project Memory

## Clasificación de seguridad

**Tier 3** — Sin auth, sin datos personales, herramienta local de demo.  
Controles: CI gates (Gitleaks + pip-audit + npm audit + build + tests), security headers HTTP.

## Protocolo de inicio de sesión IA

1. Leer este archivo.
2. Leer `README.md` y `SECURITY.md`.
3. Revisar estándares en `docs/` si aplica.
4. No empezar a trabajar sin haber leído todos.

## Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2 async, Alembic, PostgreSQL, asyncpg, pydantic-settings, yfinance
- **Frontend:** React 18, Vite, TypeScript 5, MUI 6, Recharts 2, React Router 7, Axios

## Arquitectura

Hexagonal (Ports & Adapters):
- `domain/` — puro, sin I/O: entidades, interfaces (ports), estrategias, broker, métricas
- `infrastructure/` — adaptadores concretos: yfinance provider, repos SQLAlchemy, sesión DB
- `services/` — orquestación del caso de uso
- `api/` — controladores thin: rutas + schemas Pydantic

## Reglas críticas de desarrollo

- **Frontend:** todos los imports usan alias `@/`. Prohibido `../../`.
- **Secrets:** `DATABASE_URL` requerido en `.env`. App no arranca sin él. Nunca en código.
- **TypeScript:** `strict: true`, `noUnusedLocals: true`, `noUnusedParameters: true`.
- **ORM:** SQLAlchemy models sólo en `infrastructure/db/`. Dominio nunca los importa.
- **Seguridad HTTP:** middleware aplica `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- **CORS:** restringido a `ALLOWED_ORIGINS` del entorno.

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/simulations/run` | Crea y ejecuta simulación |
| GET  | `/simulations` | Lista con métricas resumidas |
| GET  | `/simulations/{id}` | Detalle completo |
| GET  | `/simulations/compare/pair?a=ID&b=ID` | Comparador |
| GET  | `/health` | Health check |

## DB schema (tablas)

- `simulations` (id, ticker, strategy_name, config_json JSONB, status, error_message, created_at)
- `trades` (id, simulation_id FK, timestamp, side, qty, price, fees, slippage, pnl)
- `equity_points` (id, simulation_id FK, timestamp, equity)
- `metrics` (simulation_id PK/FK, profit_pct, win_rate, max_drawdown, sharpe, num_trades)

## Variables de entorno requeridas

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| DATABASE_URL | Sí | Postgres connection string |
| ENVIRONMENT | No (local) | local / production |
| LOG_LEVEL | No (INFO) | Log level |
| ALLOWED_ORIGINS | No | CORS origins |

## Archivos críticos del frontend (deben existir)

```
src/main.tsx
src/routes.tsx
src/api/client.ts
src/components/common/AppLayout.tsx
src/components/common/MetricCard.tsx
src/components/common/EquityChart.tsx
src/components/common/TradesTable.tsx
src/pages/SimulatePage.tsx
src/pages/ResultsPage.tsx
src/pages/ComparePage.tsx
```
