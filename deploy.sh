#!/bin/bash

# Скрипт для деплоя изменений на сервер

SERVER="root@212.67.9.187"
PASSWORD="R41VjU7HlyE*"
REMOTE_DIR="/root/kino"

echo "Подключение к серверу и обновление кода..."

# Копируем измененные файлы на сервер
scp -o StrictHostKeyChecking=no cinema/models.py cinema/forms.py cinema/views.py cinema/urls.py cinema/admin.py kino_project/settings.py $SERVER:$REMOTE_DIR/cinema/ 2>/dev/null || echo "Ошибка копирования models.py"
scp -o StrictHostKeyChecking=no cinema/forms.py $SERVER:$REMOTE_DIR/cinema/ 2>/dev/null || echo "Ошибка копирования forms.py"
scp -o StrictHostKeyChecking=no cinema/views.py $SERVER:$REMOTE_DIR/cinema/ 2>/dev/null || echo "Ошибка копирования views.py"
scp -o StrictHostKeyChecking=no cinema/urls.py $SERVER:$REMOTE_DIR/cinema/ 2>/dev/null || echo "Ошибка копирования urls.py"
scp -o StrictHostKeyChecking=no cinema/admin.py $SERVER:$REMOTE_DIR/cinema/ 2>/dev/null || echo "Ошибка копирования admin.py"
scp -o StrictHostKeyChecking=no kino_project/settings.py $SERVER:$REMOTE_DIR/kino_project/ 2>/dev/null || echo "Ошибка копирования settings.py"

# Копируем шаблоны
scp -o StrictHostKeyChecking=no templates/cinema/password_reset_request.html templates/cinema/password_reset_confirm.html $SERVER:$REMOTE_DIR/templates/cinema/ 2>/dev/null || echo "Ошибка копирования шаблонов"
scp -o StrictHostKeyChecking=no templates/cinema/login.html $SERVER:$REMOTE_DIR/templates/cinema/ 2>/dev/null || echo "Ошибка копирования login.html"

echo "Выполнение команд на сервере..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd /root/kino
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart gunicorn 2>/dev/null || systemctl restart django 2>/dev/null || echo "Перезапустите сервер вручную"
echo "Деплой завершен!"
ENDSSH

echo "Готово!"

