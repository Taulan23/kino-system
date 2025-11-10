from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """Расширенная модель пользователя с ролями"""
    ROLE_CHOICES = [
        ('user', 'Зритель'),
        ('staff', 'Сотрудник'),
        ('admin', 'Администратор'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Город'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class City(models.Model):
    """Города"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры фильмов"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """Фильмы"""
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Длительность (минуты)'
    )
    release_date = models.DateField(
        verbose_name='Дата выхода'
    )
    director = models.CharField(
        max_length=255,
        verbose_name='Режиссер'
    )
    cast = models.TextField(
        verbose_name='Актерский состав'
    )
    genres = models.ManyToManyField(
        Genre,
        verbose_name='Жанры'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0,
        verbose_name='Рейтинг'
    )
    age_restriction = models.CharField(
        max_length=5,
        default='0+',
        verbose_name='Возрастное ограничение'
    )
    poster = models.ImageField(
        upload_to='movies/posters/',
        blank=True,
        null=True,
        verbose_name='Постер'
    )
    poster_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на постер'
    )
    trailer_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на трейлер'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0


class Cinema(models.Model):
    """Кинотеатры"""
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='cinemas',
        verbose_name='Город'
    )
    address = models.CharField(
        max_length=500,
        verbose_name='Адрес'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    facilities = models.TextField(
        blank=True,
        verbose_name='Удобства и особенности'
    )
    image = models.ImageField(
        upload_to='cinemas/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на изображение'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатры'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.city.name})"


class Hall(models.Model):
    """Залы кинотеатра"""
    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name='halls',
        verbose_name='Кинотеатр'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название зала'
    )
    rows = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество рядов'
    )
    seats_per_row = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество мест в ряду'
    )
    
    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'
        ordering = ['cinema', 'name']
    
    def __str__(self):
        return f"{self.cinema.name} - {self.name}"
    
    @property
    def total_seats(self):
        return self.rows * self.seats_per_row


class ShowTime(models.Model):
    """Сеансы"""
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='showtimes',
        verbose_name='Фильм'
    )
    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name='showtimes',
        verbose_name='Зал'
    )
    start_time = models.DateTimeField(
        verbose_name='Время начала'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена билета'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"
    
    def get_available_seats(self):
        """Получить количество свободных мест"""
        booked = self.tickets.filter(
            status__in=['booked', 'paid']
        ).count()
        return self.hall.total_seats - booked
    
    def is_seat_available(self, row, seat):
        """Проверить доступность места"""
        return not self.tickets.filter(
            row=row,
            seat=seat,
            status__in=['booked', 'paid']
        ).exists()


class Ticket(models.Model):
    """Билеты"""
    STATUS_CHOICES = [
        ('booked', 'Забронирован'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
    ]
    
    showtime = models.ForeignKey(
        ShowTime,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Сеанс'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Пользователь'
    )
    row = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Ряд'
    )
    seat = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Место'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='booked',
        verbose_name='Статус'
    )
    booking_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата бронирования'
    )
    
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        ordering = ['-booking_date']
        unique_together = ['showtime', 'row', 'seat']
    
    def __str__(self):
        return f"Билет #{self.id} - {self.showtime.movie.title}"


class Review(models.Model):
    """Отзывы к фильмам"""
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Фильм'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Одобрен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['movie', 'user']
    
    def __str__(self):
        return f"Отзыв {self.user.username} на {self.movie.title}"


class Promotion(models.Model):
    """Акции и специальные предложения"""
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    discount_percent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name='Скидка (%)'
    )
    start_date = models.DateField(
        verbose_name='Дата начала'
    )
    end_date = models.DateField(
        verbose_name='Дата окончания'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    image = models.ImageField(
        upload_to='promotions/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def is_valid(self):
        """Проверить действительность акции"""
        today = timezone.now().date()
        return (self.is_active and 
                self.start_date <= today <= self.end_date)


class Rule(models.Model):
    """Правила кинотеатра"""
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержание'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    
    class Meta:
        verbose_name = 'Правило'
        verbose_name_plural = 'Правила'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class PasswordResetToken(models.Model):
    """Токен для восстановления пароля"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name='Пользователь'
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Токен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    expires_at = models.DateTimeField(
        verbose_name='Истекает'
    )
    used = models.BooleanField(
        default=False,
        verbose_name='Использован'
    )
    
    class Meta:
        verbose_name = 'Токен восстановления пароля'
        verbose_name_plural = 'Токены восстановления пароля'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Токен для {self.user.username} - {self.token[:8]}..."
    
    def is_valid(self):
        """Проверить валидность токена"""
        return not self.used and self.expires_at > timezone.now()
