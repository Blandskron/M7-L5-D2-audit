"""Vistas didácticas para comparar ORM, SQL parametrizado y procedimientos."""

from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import AuditLog


def logs_orm_view(request):
    """5.1: filtros dinámicos, ``defer()``, anotaciones y paginación con ORM."""
    user = request.GET.get("user", "")
    severity = request.GET.get("severity", "")
    text = request.GET.get("text", "")
    start = request.GET.get("start", "")
    end = request.GET.get("end", "")
    queryset = AuditLog.objects.all()
    if user:
        queryset = queryset.filter(user__icontains=user)
    if severity:
        queryset = queryset.filter(severity=severity)
    if text:
        queryset = queryset.filter(message__icontains=text)
    if start:
        queryset = queryset.filter(created_at__date__gte=start)
    if end:
        queryset = queryset.filter(created_at__date__lte=end)

    # La columna de texto puede ser grande: se excluye del SELECT inicial.
    queryset = queryset.defer("message")
    metrics = AuditLog.objects.values("severity").annotate(total=Count("id")).order_by("-total")
    page_obj = Paginator(queryset.order_by("-created_at"), 10).get_page(request.GET.get("page"))
    return render(request, "audit/logs.html", {
        "page_obj": page_obj,
        "metrics": metrics,
        "filters": {"user": user, "severity": severity, "text": text, "start": start, "end": end},
        "severities": AuditLog.SEVERITY_CHOICES,
    })


def logs_sql_view(request):
    """5.2: ``raw()`` mapea columnas, incluido ``id``, a instancias de AuditLog."""
    severity = request.GET.get("severity", "ERROR")
    try:
        days = max(1, min(int(request.GET.get("days", "30")), 365))
    except ValueError:
        days = 30
    since = timezone.now() - timedelta(days=days)
    raw_query = """
        SELECT id, "user", action, severity, message, created_at
        FROM audit_log
        WHERE severity = %s AND created_at >= %s
        ORDER BY created_at DESC
        LIMIT 20
    """
    # Los parámetros se pasan aparte: no interpolar valores del request en SQL.
    logs = AuditLog.objects.raw(raw_query, [severity, since])
    return render(request, "audit/logs_sql.html", {
        "logs": logs, "severity": severity, "days": days, "severities": AuditLog.SEVERITY_CHOICES,
    })


def logs_crud_sql_view(request):
    """5.3: INSERT, UPDATE y DELETE SQL acotados al registro recién creado."""
    if request.method != "POST":
        return render(request, "audit/crud_done.html")

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO audit_log ("user", action, severity, message, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id
        """, ["sql-demo", "manual_insert", "INFO", "Registro insertado manualmente"])
        inserted_id = cursor.fetchone()[0]
        cursor.execute("UPDATE audit_log SET severity = %s WHERE id = %s", ["WARNING", inserted_id])
        cursor.execute("DELETE FROM audit_log WHERE id = %s", [inserted_id])

    messages.success(request, "INSERT, UPDATE y DELETE ejecutados dentro de una transacción SQL.")
    return redirect("audit:logs_crud_sql")


def logs_procedure_view(request):
    """Invoca ``CALL`` a un procedimiento y recupera el resumen desde una función SQL."""
    with connection.cursor() as cursor:
        cursor.execute("CALL sp_register_audit(%s, %s, %s, %s)", [
            "procedure-demo", "procedure_call", "INFO", "Registro creado mediante CALL.",
        ])
        cursor.execute("SELECT severity, total FROM sp_audit_summary()")
        result = cursor.fetchall()
    return render(request, "audit/procedure.html", {"result": result})
