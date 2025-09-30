# 🚀 Инструкция по деплою на Railway

## Шаг 1: Загрузка на GitHub (5 минут)

### 1.1. Инициализируйте Git репозиторий
```bash
cd /Users/shadownight/Desktop/kino
git init
git add .
git commit -m "Initial commit: Django Cinema System"
```

### 1.2. Создайте репозиторий на GitHub
1. Откройте https://github.com/new
2. Название: `kino-system` (или любое другое)
3. Приватность: Public или Private (не важно)
4. НЕ создавайте README, .gitignore или LICENSE
5. Нажмите "Create repository"

### 1.3. Загрузите код на GitHub
После создания репозитория GitHub покажет команды, выполните их:
```bash
git remote add origin https://github.com/ВАШ_ЮЗЕРНЕЙМ/kino-system.git
git branch -M main
git push -u origin main
```

**Если нужна авторизация:**
- Username: ваш GitHub username
- Password: используйте Personal Access Token (не пароль!)
  - Получить токен: https://github.com/settings/tokens
  - Создайте Classic Token с правами `repo`

---

## Шаг 2: Деплой на Railway (3 минуты)

### 2.1. Регистрация на Railway
1. Откройте https://railway.app/
2. Нажмите **"Start a New Project"**
3. Войдите через GitHub (Login with GitHub)
4. Разрешите доступ Railway к вашему GitHub

### 2.2. Создание проекта
1. Нажмите **"New Project"**
2. Выберите **"Deploy from GitHub repo"**
3. Выберите репозиторий `kino-system`
4. Railway автоматически определит Django проект ✅

### 2.3. Добавление PostgreSQL
1. В вашем проекте нажмите **"+ New"**
2. Выберите **"Database"** → **"Add PostgreSQL"**
3. Railway автоматически создаст базу данных и подключит её
4. Переменная `DATABASE_URL` будет автоматически добавлена ✅

### 2.4. Настройка переменных окружения
В разделе **"Variables"** вашего Django сервиса добавьте:

```
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
DISABLE_COLLECTSTATIC=0
```

**Сгенерировать SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.5. Инициализация данных
После успешного деплоя выполните команду для заполнения базы данных:

1. В Railway перейдите в раздел вашего Django сервиса
2. Откройте вкладку **"Settings"** → **"Deploy"**
3. Или используйте Railway CLI (опционально):

```bash
# Установка Railway CLI
npm i -g @railway/cli

# Логин
railway login

# Подключение к проекту
railway link

# Выполнение команды инициализации
railway run python manage.py init_data
```

**Альтернатива (через веб-интерфейс):**
1. В Railway нажмите на ваш Django сервис
2. Перейдите в **"Logs"**
3. Дождитесь успешного деплоя
4. Используйте **"Settings"** → **"Custom Start Command"** и временно измените на:
   ```
   python manage.py migrate && python manage.py init_data && gunicorn kino_project.wsgi
   ```
5. После запуска верните команду обратно:
   ```
   python manage.py migrate && python manage.py collectstatic --noinput && gunicorn kino_project.wsgi
   ```

---

## Шаг 3: Проверка работы

### 3.1. Получение URL
Railway автоматически создаст публичный URL вида:
```
https://kino-system-production-xxxx.up.railway.app
```

Найдите его в разделе **"Settings"** → **"Domains"**

### 3.2. Проверьте работу сайта
1. Откройте URL в браузере
2. Должна появиться главная страница с фильмами
3. Попробуйте войти с тестовыми данными:
   - **Администратор:** admin / admin123
   - **Сотрудник:** staff / staff123
   - **Пользователь:** user / user123

---

## 🎉 Готово!

Ваш сайт доступен публично и работает с PostgreSQL!

### Что еще можно сделать:

1. **Добавить свой домен** (опционально)
   - В Railway: Settings → Domains → Custom Domain
   
2. **Мониторинг**
   - Railway показывает логи, использование ресурсов и метрики
   
3. **Автоматическое обновление**
   - При каждом `git push` в main, Railway автоматически задеплоит изменения

---

## Альтернатива: Render.com (если Railway не подошел)

### Быстрый старт на Render:
1. https://render.com/ → Sign Up (через GitHub)
2. New → Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python manage.py migrate && gunicorn kino_project.wsgi`
5. Add PostgreSQL: New → PostgreSQL
6. Подключите БД через переменную `DATABASE_URL`

---

## 💡 Полезные команды

```bash
# Просмотр логов Railway
railway logs

# Выполнение команд на сервере
railway run python manage.py createsuperuser
railway run python manage.py migrate

# Обновление кода
git add .
git commit -m "Update"
git push
```

---

## 🆘 Если что-то не работает:

1. **Проверьте логи** в Railway (вкладка "Logs")
2. **Убедитесь**, что `DATABASE_URL` установлена
3. **Проверьте**, что миграции выполнены
4. **DEBUG=False** должен быть установлен
5. Если сайт не открывается - подождите 2-3 минуты после первого деплоя

---

**Время деплоя: ~8 минут**  
**Стоимость: БЕСПЛАТНО** (Railway дает 500 часов/месяц, этого хватит на круглосуточную работу сайта)
