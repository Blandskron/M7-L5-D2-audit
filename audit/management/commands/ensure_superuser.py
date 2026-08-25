import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea el superusuario configurado por variables de entorno si no existe."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        if not username or not password:
            raise CommandError("Defina DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD.")

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write("El superusuario ya existe.")
            return
        user_model.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS("Superusuario creado."))
