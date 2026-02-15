from django.db import models
from django.db.models import Index


class AuditLog(models.Model):
    """
    Modelo principal de bitácora/auditoría.
    Incluye índices para búsquedas optimizadas.
    """

    SEVERITY_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    user = models.CharField(max_length=100, db_index=True)
    action = models.CharField(max_length=255)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, db_index=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_log"
        indexes = [
            Index(fields=["user", "severity"]),   # Índice compuesto
            Index(fields=["created_at"]),         # Índice temporal
        ]

    def __str__(self):
        return f"{self.user} - {self.severity} - {self.created_at}"