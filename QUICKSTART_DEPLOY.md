# ⚡ Быстрый старт - Деплой за 5 минут

## 🔥 Вариант 1: Railway (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Загрузите код на GitHub
```bash
cd /Users/shadownight/Desktop/kino
git init
git add .
git commit -m "Initial commit"
```

Создайте репозиторий на https://github.com/new и выполните:
```bash
git remote add origin https://github.com/ВАШ_USERNAME/kino-system.git
git branch -M main
git push -u origin main
```

### Шаг 2: Деплой на Railway
1. Откройте https://railway.app/
2. Login with GitHub
3. **New Project** → **Deploy from GitHub repo** → выберите ваш репозиторий
4. **+ New** → **Database** → **Add PostgreSQL**
5. В настройках Django сервиса добавьте переменные:
   ```
   SECRET_KEY=сгенерируйте-случайный-ключ
   DEBUG=False
   ```

### Шаг 3: Инициализация данных
Установите Railway CLI:
```bash
npm i -g @railway/cli
railway login
railway link
railway run python manage.py init_data
```

**Готово!** Ваш сайт доступен по ссылке из Railway Dashboard.

---

## 🌐 Вариант 2: Render

1. https://render.com/ → Sign Up через GitHub
2. **New** → **Web Service** → подключите GitHub repo
3. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python manage.py migrate && gunicorn kino_project.wsgi`
4. **New** → **PostgreSQL** → подключите к Web Service
5. Добавьте переменную `SECRET_KEY` в Environment

---

## 🎯 Логины для тестирования

После выполнения `init_data`:
- **Админ:** `admin` / `admin123`
- **Сотрудник:** `staff` / `staff123`
- **Пользователь:** `user` / `user123`

---

## 📋 Что уже настроено:

✅ PostgreSQL подключение  
✅ Статические файлы (WhiteNoise)  
✅ Gunicorn сервер  
✅ Production settings  
✅ Автоматическая миграция БД  
✅ Тестовые данные (7 городов, 6 фильмов, сеансы)

---

## 🔧 После деплоя:

```bash
# Создать суперпользователя
railway run python manage.py createsuperuser

# Посмотреть логи
railway logs

# Обновить код на сервере
git add .
git commit -m "Update"
git push
```

Всё! 🎉
