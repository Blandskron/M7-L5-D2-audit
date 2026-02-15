from django.core.management.base import BaseCommand
from django.db import connection
from faker import Faker
import random


class Command(BaseCommand):
    """
    Carga masiva optimizada con execute_batch.
    python manage.py load_massive_logs 100000
    """

    help = "Carga masiva de registros en audit_log"

    def add_arguments(self, parser):
        parser.add_argument("total", type=int, help="Cantidad de registros")

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        fake = Faker()

        severities = ["INFO", "WARNING", "ERROR", "CRITICAL"]

        self.stdout.write(f"Insertando {total} registros...")

        data = []
        for _ in range(total):
            data.append((
                fake.user_name(),
                fake.word(),
                random.choice(severities),
                fake.text(max_nb_chars=200),
            ))

        with connection.cursor() as cursor:

            # IMPORTANTE: "user" con comillas dobles porque es palabra reservada
            cursor.executemany("""
                INSERT INTO audit_log ("user", action, severity, message, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, data)

        self.stdout.write(self.style.SUCCESS("Carga masiva completada correctamente."))