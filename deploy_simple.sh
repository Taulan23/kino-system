#!/bin/bash

# Простой скрипт деплоя через rsync/ssh

echo "Подготовка файлов для деплоя..."

# Создаем архив с измененными файлами
tar -czf deploy_files.tar.gz \
    cinema/models.py \
    cinema/forms.py \
    cinema/views.py \
    cinema/urls.py \
    cinema/admin.py \
    kino_project/settings.py \
    templates/cinema/password_reset_request.html \
    templates/cinema/password_reset_confirm.html \
    templates/cinema/login.html

echo "Архив создан. Теперь скопируйте файлы вручную на сервер:"
echo "scp deploy_files.tar.gz root@212.67.9.187:/root/kino/"
echo ""
echo "Затем выполните на сервере:"
echo "cd /root/kino"
echo "tar -xzf deploy_files.tar.gz"
echo "source venv/bin/activate"
echo "python manage.py makemigrations"
echo "python manage.py migrate"
echo "python manage.py collectstatic --noinput"
echo "systemctl restart gunicorn || systemctl restart django"

