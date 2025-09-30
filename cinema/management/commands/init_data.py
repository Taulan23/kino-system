from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cinema.models import (
    User, City, Genre, Movie, Cinema, Hall,
    ShowTime, Promotion, Rule
)
import requests
from io import BytesIO
from django.core.files import File


class Command(BaseCommand):
    help = 'Инициализация базы данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начало инициализации данных...')
        
        # Создание городов
        self.stdout.write('Создание городов...')
        cities_data = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Тюмень', 'Томск']
        cities = {}
        for city_name in cities_data:
            city, created = City.objects.get_or_create(name=city_name, defaults={'is_active': True})
            cities[city_name] = city
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создан город: {city_name}'))

        # Создание жанров
        self.stdout.write('Создание жанров...')
        genres_data = [
            'Боевик', 'Комедия', 'Драма', 'Фантастика', 'Триллер',
            'Ужасы', 'Приключения', 'Мелодрама', 'Детектив', 'Фэнтези'
        ]
        genres = {}
        for genre_name in genres_data:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genres[genre_name] = genre
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создан жанр: {genre_name}'))

        # Создание пользователей
        self.stdout.write('Создание пользователей...')
        
        # Администратор
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@kinomir.ru',
                password='admin123',
                role='admin',
                first_name='Администратор',
                last_name='Системы',
                city=cities['Москва']
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан администратор: admin / admin123'))
        
        # Сотрудник
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user(
                username='staff',
                email='staff@kinomir.ru',
                password='staff123',
                role='staff',
                first_name='Иван',
                last_name='Петров',
                city=cities['Москва']
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан сотрудник: staff / staff123'))
        
        # Обычный пользователь
        if not User.objects.filter(username='user').exists():
            user = User.objects.create_user(
                username='user',
                email='user@example.com',
                password='user123',
                role='user',
                first_name='Алексей',
                last_name='Иванов',
                city=cities['Москва']
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан пользователь: user / user123'))

        # Создание фильмов с постерами из интернета
        self.stdout.write('Создание фильмов и загрузка постеров...')
        
        movies_data = [
            {
                'title': 'Начало',
                'description': 'Профессиональный вор, который крадет коммерческие секреты путем проникновения в подсознание своих целей, получает шанс на искупление.',
                'duration': 148,
                'director': 'Кристофер Нолан',
                'cast': 'Леонардо ДиКаприо, Марион Котийяр, Джозеф Гордон-Левитт',
                'genres': ['Фантастика', 'Триллер', 'Боевик'],
                'rating': 8.8,
                'age_restriction': '12+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg'
            },
            {
                'title': 'Побег из Шоушенка',
                'description': 'Два заключенных подружились на протяжении многих лет, находя утешение и в конечном итоге искупление через акты общего порядочности.',
                'duration': 142,
                'director': 'Фрэнк Дарабонт',
                'cast': 'Тим Роббинс, Морган Фриман',
                'genres': ['Драма'],
                'rating': 9.3,
                'age_restriction': '16+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'
            },
            {
                'title': 'Темный рыцарь',
                'description': 'Когда угроза, известная как Джокер, сеет хаос среди людей Готэма, Бэтмен должен принять один из величайших психологических и физических испытаний.',
                'duration': 152,
                'director': 'Кристофер Нолан',
                'cast': 'Кристиан Бейл, Хит Леджер, Аарон Экхарт',
                'genres': ['Боевик', 'Драма', 'Детектив'],
                'rating': 9.0,
                'age_restriction': '16+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'
            },
            {
                'title': 'Криминальное чтиво',
                'description': 'Переплетающиеся истории преступников Лос-Анджелеса, их босса и его жены, а также боксера.',
                'duration': 154,
                'director': 'Квентин Тарантино',
                'cast': 'Джон Траволта, Сэмюэл Л. Джексон, Ума Турман',
                'genres': ['Драма', 'Детектив'],
                'rating': 8.9,
                'age_restriction': '18+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'
            },
            {
                'title': 'Форрест Гамп',
                'description': 'История жизни простодушного мужчины из Алабамы, который стал свидетелем нескольких определяющих исторических событий XX века.',
                'duration': 142,
                'director': 'Роберт Земекис',
                'cast': 'Том Хэнкс, Робин Райт, Гэри Синиз',
                'genres': ['Драма', 'Мелодрама'],
                'rating': 8.8,
                'age_restriction': '12+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg'
            },
            {
                'title': 'Матрица',
                'description': 'Компьютерный хакер узнает от таинственных повстанцев о истинной природе его реальности и своей роли в войне против ее контролеров.',
                'duration': 136,
                'director': 'Вачовски',
                'cast': 'Киану Ривз, Лоренс Фишберн, Кэрри-Энн Мосс',
                'genres': ['Фантастика', 'Боевик'],
                'rating': 8.7,
                'age_restriction': '16+',
                'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg'
            },
        ]

        movies = []
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'duration': movie_data['duration'],
                    'release_date': timezone.now().date() - timedelta(days=30),
                    'director': movie_data['director'],
                    'cast': movie_data['cast'],
                    'rating': movie_data['rating'],
                    'age_restriction': movie_data['age_restriction'],
                    'is_active': True
                }
            )
            
            if created:
                # Добавление жанров
                for genre_name in movie_data['genres']:
                    movie.genres.add(genres[genre_name])
                
                # Загрузка постера
                try:
                    response = requests.get(movie_data['poster_url'], timeout=10)
                    if response.status_code == 200:
                        img_temp = BytesIO(response.content)
                        movie.poster.save(f"{movie.title.replace(' ', '_')}.jpg", File(img_temp), save=True)
                        self.stdout.write(self.style.SUCCESS(f'✓ Создан фильм: {movie.title} (с постером)'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'✓ Создан фильм: {movie.title} (без постера)'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠ Создан фильм: {movie.title} (ошибка загрузки постера: {str(e)})'))
            
            movies.append(movie)

        # Создание кинотеатров
        self.stdout.write('Создание кинотеатров...')
        cinemas = []
        for city_name, city in cities.items():
            cinema, created = Cinema.objects.get_or_create(
                name=f'КиноМир {city_name}',
                city=city,
                defaults={
                    'address': f'ул. Центральная, 1, {city_name}',
                    'phone': '+7 (800) 555-35-35',
                    'description': f'Современный кинотеатр в центре города {city_name}',
                    'facilities': 'IMAX, Dolby Atmos, VIP-залы, кафе, бесплатная парковка',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создан кинотеатр: {cinema.name}'))
            cinemas.append(cinema)

        # Создание залов
        self.stdout.write('Создание залов...')
        halls = []
        for cinema in cinemas:
            for i in range(1, 4):
                hall, created = Hall.objects.get_or_create(
                    cinema=cinema,
                    name=f'Зал {i}',
                    defaults={
                        'rows': 10,
                        'seats_per_row': 12
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Создан зал: {hall}'))
                halls.append(hall)

        # Создание сеансов
        self.stdout.write('Создание сеансов...')
        today = timezone.now()
        for hall in halls[:6]:  # Только первые 6 залов
            for movie in movies[:3]:  # Только первые 3 фильма
                for day in range(7):  # На неделю вперед
                    for hour in [10, 14, 18, 21]:
                        showtime_date = today + timedelta(days=day, hours=hour-today.hour)
                        showtime, created = ShowTime.objects.get_or_create(
                            movie=movie,
                            hall=hall,
                            start_time=showtime_date,
                            defaults={
                                'price': 300 + (day * 50),
                                'is_active': True
                            }
                        )
                        if created and day == 0 and hour == 10:
                            self.stdout.write(self.style.SUCCESS(f'✓ Создан сеанс: {movie.title} в {hall}'))

        # Создание акций
        self.stdout.write('Создание акций...')
        promotions_data = [
            {
                'title': 'Выходные со скидкой',
                'description': 'Скидка 20% на все сеансы в выходные дни! Приходите всей семьей и наслаждайтесь любимыми фильмами по выгодным ценам.',
                'discount_percent': 20,
                'days': 30
            },
            {
                'title': 'Студенческая среда',
                'description': 'Каждую среду студенты получают скидку 30% на все сеансы. Предъявите студенческий билет на кассе.',
                'discount_percent': 30,
                'days': 60
            },
            {
                'title': 'Утренний сеанс',
                'description': 'Билеты на сеансы до 12:00 со скидкой 25%. Начните день с хорошего кино!',
                'discount_percent': 25,
                'days': 90
            }
        ]
        
        for promo_data in promotions_data:
            promotion, created = Promotion.objects.get_or_create(
                title=promo_data['title'],
                defaults={
                    'description': promo_data['description'],
                    'discount_percent': promo_data['discount_percent'],
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=promo_data['days']),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создана акция: {promotion.title}'))

        # Создание правил
        self.stdout.write('Создание правил...')
        rules_data = [
            {
                'title': 'Правила посещения кинотеатра',
                'content': 'Вход в зал разрешен только с билетом. Опоздавшие зрители допускаются в зал только во время технических пауз или перерывов.',
                'order': 1
            },
            {
                'title': 'Запрещено',
                'content': 'Запрещено проносить в зал свои еду и напитки. В кинотеатре работает кафе с широким ассортиментом.',
                'order': 2
            },
            {
                'title': 'Возрастные ограничения',
                'content': 'Просим соблюдать возрастные ограничения фильмов. При покупке билета на фильмы 16+, 18+ может потребоваться документ, удостоверяющий личность.',
                'order': 3
            },
            {
                'title': 'Правила поведения',
                'content': 'Во время сеанса запрещено пользоваться мобильными телефонами, громко разговаривать и мешать другим зрителям.',
                'order': 4
            },
            {
                'title': 'Возврат билетов',
                'content': 'Возврат билетов возможен не позднее, чем за 1 час до начала сеанса. Возврат осуществляется в кассе кинотеатра.',
                'order': 5
            }
        ]
        
        for rule_data in rules_data:
            rule, created = Rule.objects.get_or_create(
                title=rule_data['title'],
                defaults={
                    'content': rule_data['content'],
                    'order': rule_data['order'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создано правило: {rule.title}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Инициализация завершена успешно!'))
        self.stdout.write('\nДанные для входа:')
        self.stdout.write('Администратор: admin / admin123')
        self.stdout.write('Сотрудник: staff / staff123')
        self.stdout.write('Пользователь: user / user123')
