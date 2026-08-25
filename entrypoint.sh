#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py install_audit_procedures
python manage.py collectstatic --noinput

# Idempotente: crea el usuario solamente si aún no existe.
python manage.py ensure_superuser

exec "$@"
