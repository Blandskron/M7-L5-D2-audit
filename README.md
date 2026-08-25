# Aula Django: consultas ORM y SQL de auditoría

Aplicación educativa que resuelve el problema de buscar, resumir y mantener una bitácora de eventos. Usa Django con PostgreSQL y expone ejemplos navegables de ORM, SQL parametrizado, CRUD mediante cursor e invocación de procedimientos almacenados.

## Resultados de aprendizaje cubiertos

| Requisito | Implementación verificable |
| --- | --- |
| 5.1 Consultas ORM filtradas | `/audit/logs/`: `filter()`, `icontains`, rangos de fecha, `defer()`, paginación y `Count()` |
| 5.2 Recuperación SQL con filtros | `/audit/logs/sql/`: `AuditLog.objects.raw()` con `%s` y parámetros separados |
| Mapeo al modelo y parámetros `raw()` | El `SELECT` incluye `id` y las columnas de `AuditLog`; los parámetros son `[severity, since]` |
| Índices | `db_index` y los índices compuesto `user + severity` y temporal `created_at` en el modelo |
| 5.3 CRUD SQL | `/audit/logs/crud-sql/` ejecuta INSERT, UPDATE y DELETE con `connection.cursor()` y transacción |
| SQL personalizado, conexión y cursor | Consultas directas protegidas por parámetros y `transaction.atomic()` |
| Procedimientos almacenados | `/audit/logs/procedure/` usa `CALL sp_register_audit(...)` y consulta la función de resumen |

## Inicio rápido con Docker

```bash
copy .env.example .env
docker compose up --build
```

Abre `http://localhost:8000/audit/logs/` y el administrador en `http://localhost:8000/admin/`. En el primer arranque el `entrypoint.sh` aplica migraciones, instala `audit/sql/audit_procedures.sql`, recopila estáticos y crea el superusuario con las variables `DJANGO_SUPERUSER_*`. Cambia las credenciales de `.env` antes de usarlo fuera de desarrollo.

Para detenerlo conservando datos: `docker compose down`. Para eliminar también el volumen de PostgreSQL: `docker compose down -v`.

## Rutas del aula

| Ruta | Demostración |
| --- | --- |
| `/audit/logs/?user=ana&severity=ERROR&text=failed&start=2026-01-01&end=2026-12-31` | Filtros ORM y recuperación paginada |
| `/audit/logs/sql/?severity=ERROR&days=30` | SQL `raw()` parametrizado y mapeado al modelo |
| `/audit/logs/crud-sql/` | Formulario POST para ejecutar el CRUD SQL aislado |
| `/audit/logs/procedure/` | `CALL` a procedimiento y resultado de función SQL |

El CRUD solo actúa sobre el registro de demostración que acaba de insertar; así no destruye datos existentes. Los valores de URL nunca se concatenan en una sentencia SQL.

## Ejecución sin Docker

Necesitas PostgreSQL 16+ y Python 3.12+.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set POSTGRES_PASSWORD=tu_clave
python manage.py migrate
python manage.py install_audit_procedures
python manage.py createsuperuser
python manage.py load_massive_logs 1000
python manage.py runserver
```

## Índices y rendimiento

El índice compuesto favorece búsquedas por usuario y severidad; el temporal ordena/filtra auditorías recientes. En PostgreSQL se puede comprobar el plan con:

```sql
EXPLAIN ANALYZE
SELECT * FROM audit_log
WHERE "user" = 'ana' AND severity = 'ERROR'
ORDER BY created_at DESC;
```

La elección entre `Index Scan` y `Seq Scan` depende del volumen y de la selectividad; el planificador decide la alternativa adecuada.

## Pruebas

Con la base PostgreSQL iniciada:

```bash
docker compose run --rm web python manage.py test
```

El archivo SQL de procedimientos se puede revisar en `audit/sql/audit_procedures.sql`. `procedimientoAlmacenado.sql` se conserva como acceso rápido al mismo material.
