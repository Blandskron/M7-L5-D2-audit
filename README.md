## Tutorial paso a paso — Buscador de Auditoría y Bitácora (Django + PostgreSQL)

---

### 1) Crear entorno, instalar dependencias y crear proyecto

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip

pip install django psycopg2-binary faker

django-admin startproject config .
python manage.py startapp audit
```

---

### 2) Configurar PostgreSQL en `settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "audit_db",
        "USER": "postgres",
        "PASSWORD": "tu_password",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "CONN_MAX_AGE": 600,
    }
}

INSTALLED_APPS = [
    # ...
    "audit",
]
```

---

### 3) Definir el modelo con índices: `audit/models.py`

* Tabla: `audit_log`
* Índices: `user`, `severity`, `created_at`, y compuesto `user + severity`

(Usa el `models.py` que ya implementaste.)

---

### 4) Crear y aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5) Habilitar administración: `audit/admin.py` + superusuario

```bash
python manage.py createsuperuser
```

Panel:

* `http://127.0.0.1:8000/admin/`

---

### 6) Implementar endpoints: `audit/views.py`

Implementa estas rutas:

* `logs_orm_view`: filtros ORM, exclusión de campos, paginación, métricas con anotaciones
* `logs_sql_view`: recuperación con `raw()` y parámetros
* `logs_crud_sql_view`: INSERT/UPDATE/DELETE con cursor
* `logs_procedure_view`: invocación a procedimiento almacenado

(Usa el `views.py` que ya definiste.)

---

### 7) Registrar rutas: `audit/urls.py` + `config/urls.py`

**`audit/urls.py`** (ya lo tienes)

En **`config/urls.py`** agrega:

```python
from django.urls import path, include

urlpatterns = [
    path("audit/", include("audit.urls")),
]
```

---

### 8) Crear templates mínimos

Estructura:

```
audit/templates/audit/
  logs.html
  logs_sql.html
  crud_done.html
  procedure.html
```

* `logs.html`: listado paginado + métricas
* `logs_sql.html`: listado desde raw SQL
* `crud_done.html`: confirmación de CRUD SQL
* `procedure.html`: salida del procedimiento

(Usa los HTML mínimos que ya dejaste listos.)

---

### 9) Crear comando para carga masiva

Estructura:

```
audit/management/
  __init__.py
  commands/
    __init__.py
    load_massive_logs.py
```

En `load_massive_logs.py`:

* inserción masiva con `executemany`
* columna `"user"` entre comillas dobles en el SQL (PostgreSQL reserva `user`)

---

### 10) Cargar datos masivos

```bash
python manage.py load_massive_logs 100000
```

---

### 11) Crear función en PostgreSQL (resumen por severidad)

Ejecutar en PostgreSQL:

```sql
CREATE OR REPLACE FUNCTION sp_audit_summary()
RETURNS TABLE(severity VARCHAR, total BIGINT)
AS $$
BEGIN
    RETURN QUERY
    SELECT severity, COUNT(*)
    FROM audit_log
    GROUP BY severity;
END;
$$ LANGUAGE plpgsql;
```

---

### 12) Probar endpoints

#### 12.1 Logs con ORM (filtros + paginación + métricas)

* `http://127.0.0.1:8000/audit/logs/`

Parámetros:

* `?user=ana`
* `?severity=ERROR`
* `?text=failed`
* `?page=2`

#### 12.2 Logs con SQL `raw()` parametrizado

* `http://127.0.0.1:8000/audit/logs/sql/?severity=ERROR`

#### 12.3 CRUD mediante SQL directo (cursor)

* `http://127.0.0.1:8000/audit/logs/crud-sql/`

#### 12.4 Resumen desde función (callproc)

* `http://127.0.0.1:8000/audit/logs/procedure/`

---

### 13) Verificar uso de índices en PostgreSQL

```sql
EXPLAIN ANALYZE
SELECT *
FROM audit_log
WHERE severity = 'ERROR';
```

Si los índices están funcionando, el plan mostrará un `Index Scan` o equivalente.

---

## Checklist de funcionalidades implementadas

* Consultas filtradas con ORM
* Recuperación por SQL con `raw()` + parámetros
* CRUD con SQL directo usando cursor
* Consultas personalizadas con SQL
* Mapeo de resultados al modelo
* Índices y búsquedas optimizadas
* Exclusión de campos (`defer`/`only`)
* Anotaciones y agregaciones (`Count`, agrupaciones)
* Conexión y cursores (`connection.cursor()`)
* Ejecución de función/procedimiento (`callproc`)
* Carga masiva de datos para alto volumen

