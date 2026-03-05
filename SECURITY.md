# Política de Seguridad — QuantLab

## Clasificación

**Tier 3** — Sin autenticación, sin datos personales, herramienta local de demo.
Controles aplicados: CI gates (Gitleaks + pip-audit + npm audit + build + tests), security headers HTTP.

## Versiones soportadas

Solo la versión en rama `main` recibe parches de seguridad.

## Reportar una vulnerabilidad

Enviar email a: security@agenciafactoriai.com  
Tiempo de respuesta esperado: 48 horas.  
No publicar vulnerabilidades públicamente antes de dar tiempo a corregirlas (responsible disclosure).

## SLAs internos (Capa 0)

| Severidad | SLA de fix | Efecto en deploy |
|-----------|------------|-----------------|
| CRITICAL  | < 48h      | ❌ Bloqueado     |
| HIGH      | < 72h      | ❌ Bloqueado     |
| MEDIUM    | < 14 días  | ⚠️ Con ticket   |
| LOW       | Backlog    | ✅ Permitido     |
