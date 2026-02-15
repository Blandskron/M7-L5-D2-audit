from django.shortcuts import render
from django.db import connection
from django.db.models import Count
from django.core.paginator import Paginator
from .models import AuditLog


# ============================================================
# 5.1 CONSULTAS ORM FILTRADAS + ANOTACIONES + EXCLUSIÓN CAMPOS
# ============================================================

def logs_orm_view(request):
    """
    Búsqueda optimizada usando ORM:
    - Filtros por usuario
    - Severidad
    - Rango de fechas
    - Texto parcial
    - Exclusión de campos
    - Anotaciones
    - Paginación
    """

    user = request.GET.get("user")
    severity = request.GET.get("severity")
    text = request.GET.get("text")

    queryset = AuditLog.objects.all()

    # Filtros dinámicos
    if user:
        queryset = queryset.filter(user__icontains=user)

    if severity:
        queryset = queryset.filter(severity=severity)

    if text:
        queryset = queryset.filter(message__icontains=text)

    # Exclusión de campo message para optimización
    queryset = queryset.defer("message")

    # Anotación: conteo por severidad
    metrics = (
        AuditLog.objects
        .values("severity")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Paginación
    paginator = Paginator(queryset.order_by("-created_at"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "audit/logs.html", {
        "page_obj": page_obj,
        "metrics": metrics,
    })


# ============================================================
# 5.2 CONSULTAS SQL RAW + PARÁMETROS + MAPEADO A MODELO
# ============================================================

def logs_sql_view(request):
    """
    Recuperación usando raw() con parámetros.
    """

    severity = request.GET.get("severity", "ERROR")

    raw_query = """
        SELECT *
        FROM audit_log
        WHERE severity = %s
        ORDER BY created_at DESC
        LIMIT 20
    """

    logs = AuditLog.objects.raw(raw_query, [severity])

    return render(request, "audit/logs_sql.html", {"logs": logs})


# ============================================================
# 5.3 CRUD CON SQL PERSONALIZADO + CONEXIÓN Y CURSOR
# ============================================================

def logs_crud_sql_view(request):
    """
    CRUD ejecutado con SQL manual usando cursor.
    """

    with connection.cursor() as cursor:

        # INSERT
        cursor.execute("""
            INSERT INTO audit_log (user, action, severity, message, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, ["system", "manual_insert", "INFO", "Registro insertado manualmente"])

        # UPDATE
        cursor.execute("""
            UPDATE audit_log
            SET severity = %s
            WHERE user = %s
        """, ["WARNING", "system"])

        # DELETE
        cursor.execute("""
            DELETE FROM audit_log
            WHERE severity = %s
        """, ["CRITICAL"])

    return render(request, "audit/crud_done.html")


# ============================================================
# PROCEDIMIENTO ALMACENADO (EJEMPLO)
# ============================================================

def logs_procedure_view(request):
    """
    Invoca procedimiento almacenado que devuelve resumen.
    """

    with connection.cursor() as cursor:
        cursor.callproc("sp_audit_summary")  # Debe existir en la BD
        result = cursor.fetchall()

    return render(request, "audit/procedure.html", {"result": result})