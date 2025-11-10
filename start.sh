#!/bin/bash
cd /opt/kino
source venv/bin/activate
export DB_NAME=kino_db
export DB_USER=kino_user
export DB_PASSWORD=kino_password_2024
export DB_HOST=localhost
export DB_PORT=5432
python manage.py runserver 0.0.0.0:8000
