from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "severity", "created_at")
    list_filter = ("severity", "created_at")
    search_fields = ("user", "message")