#!/bin/bash
# Быстрый деплой через SSH

SERVER="root@212.67.9.187"
PASS="4jx)HAwN3mP%"

echo "Копирование файлов на сервер..."
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no deploy_files.tar.gz $SERVER:/root/kino/

echo "Выполнение команд на сервере..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd /root/kino
tar -xzf deploy_files.tar.gz
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart gunicorn || systemctl restart django || (pkill -f gunicorn && nohup gunicorn kino_project.wsgi:application --bind 0.0.0.0:8000 &)
echo "Деплой завершен!"
ENDSSH
