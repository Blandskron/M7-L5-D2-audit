from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Instala o actualiza el procedimiento y la función SQL de auditoría."

    def handle(self, *args, **options):
        sql_file = Path(__file__).resolve().parents[2] / "sql" / "audit_procedures.sql"
        with connection.cursor() as cursor:
            cursor.execute(sql_file.read_text(encoding="utf-8"))
        self.stdout.write(self.style.SUCCESS("Procedimientos de auditoría instalados."))
