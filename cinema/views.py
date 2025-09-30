from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    City, Movie, Cinema, Hall, ShowTime, Ticket, 
    Review, Promotion, Rule, User, Genre
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    ReviewForm, MovieForm, ShowTimeForm, CinemaForm,
    HallForm, PromotionForm, RuleForm
)


def index(request):
    """Главная страница"""
    movies = Movie.objects.filter(is_active=True)[:6]
    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )[:3]
    
    context = {
        'movies': movies,
        'promotions': promotions,
    }
    return render(request, 'cinema/index.html', context)


def select_city(request, city_id):
    """Выбор города"""
    city = get_object_or_404(City, id=city_id, is_active=True)
    request.session['selected_city_id'] = city.id
    messages.success(request, f'Выбран город: {city.name}')
    return redirect('cinema:index')


def movie_list(request):
    """Список фильмов с фильтрацией"""
    movies = Movie.objects.filter(is_active=True)
    
    # Фильтрация по жанру
    genre_id = request.GET.get('genre')
    if genre_id:
        movies = movies.filter(genres__id=genre_id)
    
    # Поиск по названию
    search = request.GET.get('search')
    if search:
        movies = movies.filter(
            Q(title__icontains=search) |
            Q(director__icontains=search) |
            Q(cast__icontains=search)
        )
    
    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    movies = movies.order_by(sort)
    
    genres = Genre.objects.all()
    
    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre': genre_id,
        'search_query': search,
    }
    return render(request, 'cinema/movie_list.html', context)


def movie_detail(request, pk):
    """Детальная информация о фильме"""
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Проверяем, оставлял ли пользователь отзыв
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(movie=movie, user=request.user)
        except Review.DoesNotExist:
            pass
    
    # Получаем сеансы фильма
    selected_city = request.session.get('selected_city_id')
    showtimes = ShowTime.objects.filter(
        movie=movie,
        is_active=True,
        start_time__gte=timezone.now()
    ).order_by('start_time')
    
    if selected_city:
        showtimes = showtimes.filter(hall__cinema__city_id=selected_city)
    
    context = {
        'movie': movie,
        'reviews': reviews,
        'user_review': user_review,
        'showtimes': showtimes[:10],
        'average_rating': movie.get_average_rating(),
    }
    return render(request, 'cinema/movie_detail.html', context)


@login_required
def add_review(request, pk):
    """Добавление отзыва к фильму"""
    movie = get_object_or_404(Movie, pk=pk)
    
    # Проверяем, не оставлял ли пользователь уже отзыв
    if Review.objects.filter(movie=movie, user=request.user).exists():
        messages.warning(request, 'Вы уже оставили отзыв на этот фильм.')
        return redirect('cinema:movie_detail', pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('cinema:movie_detail', pk=pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'movie': movie,
    }
    return render(request, 'cinema/add_review.html', context)


def schedule(request):
    """Расписание сеансов"""
    selected_city = request.session.get('selected_city_id')
    
    # Фильтрация по дате
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Получаем сеансы
    showtimes = ShowTime.objects.filter(
        is_active=True,
        start_time__date=selected_date
    ).select_related('movie', 'hall', 'hall__cinema')
    
    if selected_city:
        showtimes = showtimes.filter(hall__cinema__city_id=selected_city)
    
    # Фильтрация по фильму
    movie_id = request.GET.get('movie')
    if movie_id:
        showtimes = showtimes.filter(movie_id=movie_id)
    
    # Фильтрация по кинотеатру
    cinema_id = request.GET.get('cinema')
    if cinema_id:
        showtimes = showtimes.filter(hall__cinema_id=cinema_id)
    
    # Получаем список фильмов для фильтра
    movies = Movie.objects.filter(is_active=True).order_by('title')
    
    # Получаем список кинотеатров для фильтра
    cinemas = Cinema.objects.filter(is_active=True)
    if selected_city:
        cinemas = cinemas.filter(city_id=selected_city)
    
    # Генерируем даты на неделю вперед
    dates = [selected_date + timedelta(days=i) for i in range(7)]
    
    context = {
        'showtimes': showtimes.order_by('start_time'),
        'movies': movies,
        'cinemas': cinemas,
        'selected_date': selected_date,
        'dates': dates,
        'selected_movie': movie_id,
        'selected_cinema': cinema_id,
    }
    return render(request, 'cinema/schedule.html', context)


def cinema_list(request):
    """Список кинотеатров"""
    selected_city = request.session.get('selected_city_id')
    
    cinemas = Cinema.objects.filter(is_active=True)
    if selected_city:
        cinemas = cinemas.filter(city_id=selected_city)
    
    context = {
        'cinemas': cinemas,
    }
    return render(request, 'cinema/cinema_list.html', context)


def cinema_detail(request, pk):
    """Детальная информация о кинотеатре"""
    cinema = get_object_or_404(Cinema, pk=pk)
    halls = cinema.halls.all()
    
    # Получаем ближайшие сеансы в этом кинотеатре
    showtimes = ShowTime.objects.filter(
        hall__cinema=cinema,
        is_active=True,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:10]
    
    context = {
        'cinema': cinema,
        'halls': halls,
        'showtimes': showtimes,
    }
    return render(request, 'cinema/cinema_detail.html', context)


def promotion_list(request):
    """Список акций"""
    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    context = {
        'promotions': promotions,
    }
    return render(request, 'cinema/promotion_list.html', context)


def promotion_detail(request, pk):
    """Детальная информация об акции"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    context = {
        'promotion': promotion,
    }
    return render(request, 'cinema/promotion_detail.html', context)


def rules(request):
    """Правила кинотеатра"""
    rules = Rule.objects.filter(is_active=True)
    
    context = {
        'rules': rules,
    }
    return render(request, 'cinema/rules.html', context)


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('cinema:index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('cinema:index')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'cinema/register.html', context)


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('cinema:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            
            # Перенаправление в зависимости от роли
            if user.role == 'admin':
                return redirect('cinema:admin_dashboard')
            elif user.role == 'staff':
                return redirect('cinema:staff_dashboard')
            else:
                return redirect('cinema:index')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
    }
    return render(request, 'cinema/login.html', context)


@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('cinema:index')


@login_required
def profile(request):
    """Профиль пользователя"""
    context = {
        'user': request.user,
    }
    return render(request, 'cinema/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('cinema:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'cinema/edit_profile.html', context)


@login_required
def change_password(request):
    """Смена пароля"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('cinema:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'cinema/change_password.html', context)


@login_required
def my_tickets(request):
    """Мои билеты"""
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'showtime__movie', 'showtime__hall__cinema'
    ).order_by('-booking_date')
    
    context = {
        'tickets': tickets,
        'now': timezone.now(),
    }
    return render(request, 'cinema/my_tickets.html', context)


@login_required
def my_reviews(request):
    """Мои отзывы"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'cinema/my_reviews.html', context)


@login_required
def delete_review(request, pk):
    """Удаление отзыва"""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    movie_pk = review.movie.pk
    review.delete()
    messages.success(request, 'Отзыв успешно удален.')
    return redirect('cinema:movie_detail', pk=movie_pk)


@login_required
def book_ticket(request, pk):
    """Бронирование билета"""
    showtime = get_object_or_404(ShowTime, pk=pk)
    
    # Проверяем, что сеанс не начался
    if showtime.start_time <= timezone.now():
        messages.error(request, 'Невозможно забронировать билет на прошедший сеанс.')
        return redirect('cinema:schedule')
    
    if request.method == 'POST':
        row = int(request.POST.get('row'))
        seat = int(request.POST.get('seat'))
        
        # Проверяем доступность места
        if not showtime.is_seat_available(row, seat):
            messages.error(request, 'Это место уже занято.')
            return redirect('cinema:book_ticket', pk=pk)
        
        # Создаем билет
        ticket = Ticket.objects.create(
            showtime=showtime,
            user=request.user,
            row=row,
            seat=seat,
            price=showtime.price,
            status='paid'
        )
        
        messages.success(request, f'Билет успешно куплен! Ряд {row}, место {seat}')
        return redirect('cinema:my_tickets')
    
    # Получаем занятые места
    booked_seats = Ticket.objects.filter(
        showtime=showtime,
        status__in=['booked', 'paid']
    ).values_list('row', 'seat')
    
    # Создаем схему зала
    seats = []
    for row in range(1, showtime.hall.rows + 1):
        row_seats = []
        for seat in range(1, showtime.hall.seats_per_row + 1):
            is_booked = (row, seat) in booked_seats
            row_seats.append({
                'row': row,
                'seat': seat,
                'is_booked': is_booked
            })
        seats.append(row_seats)
    
    context = {
        'showtime': showtime,
        'seats': seats,
    }
    return render(request, 'cinema/book_ticket.html', context)


@login_required
def cancel_ticket(request, pk):
    """Отмена билета"""
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    
    # Проверяем, что до сеанса осталось хотя бы 1 час
    if ticket.showtime.start_time - timezone.now() < timedelta(hours=1):
        messages.error(request, 'Невозможно отменить билет менее чем за 1 час до сеанса.')
        return redirect('cinema:my_tickets')
    
    ticket.status = 'cancelled'
    ticket.save()
    messages.success(request, 'Билет успешно отменен.')
    return redirect('cinema:my_tickets')


# Панель сотрудника

def staff_required(view_func):
    """Декоратор для проверки прав сотрудника или администратора"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Требуется авторизация.')
            return redirect('cinema:login')
        if request.user.role not in ['staff', 'admin']:
            messages.error(request, 'У вас нет доступа к этой странице.')
            return redirect('cinema:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def staff_dashboard(request):
    """Панель сотрудника"""
    today = timezone.now().date()
    
    # Сеансы на сегодня
    showtimes = ShowTime.objects.filter(
        start_time__date=today,
        is_active=True
    ).order_by('start_time')
    
    # Статистика
    today_tickets = Ticket.objects.filter(
        booking_date__date=today,
        status__in=['booked', 'paid']
    ).count()
    
    context = {
        'showtimes': showtimes,
        'today_tickets': today_tickets,
    }
    return render(request, 'cinema/staff/dashboard.html', context)


@staff_required
def staff_seats(request, showtime_id):
    """Просмотр занятости мест"""
    showtime = get_object_or_404(ShowTime, pk=showtime_id)
    
    # Получаем занятые места
    booked_tickets = Ticket.objects.filter(
        showtime=showtime,
        status__in=['booked', 'paid']
    ).select_related('user')
    
    # Создаем схему зала с информацией о билетах
    seats = []
    for row in range(1, showtime.hall.rows + 1):
        row_seats = []
        for seat in range(1, showtime.hall.seats_per_row + 1):
            ticket = booked_tickets.filter(row=row, seat=seat).first()
            row_seats.append({
                'row': row,
                'seat': seat,
                'ticket': ticket,
                'is_booked': ticket is not None
            })
        seats.append(row_seats)
    
    context = {
        'showtime': showtime,
        'seats': seats,
        'available_seats': showtime.get_available_seats(),
        'total_seats': showtime.hall.total_seats,
    }
    return render(request, 'cinema/staff/seats.html', context)


@staff_required
def staff_reviews(request):
    """Панель модерации отзывов для сотрудников"""
    status_filter = request.GET.get('status', 'all')
    
    reviews = Review.objects.all().select_related('user', 'movie').order_by('-created_at')
    
    if status_filter == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif status_filter == 'approved':
        reviews = reviews.filter(is_approved=True)
    
    context = {
        'reviews': reviews,
        'status_filter': status_filter,
        'pending_count': Review.objects.filter(is_approved=False).count(),
    }
    return render(request, 'cinema/staff/reviews.html', context)


@staff_required
def toggle_review_approval(request, pk):
    """Одобрение/отклонение отзыва"""
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = not review.is_approved
    review.save()
    
    status = 'одобрен' if review.is_approved else 'отклонен'
    messages.success(request, f'Отзыв {status}.')
    
    return redirect(request.META.get('HTTP_REFERER', 'cinema:staff_dashboard'))


@staff_required
def staff_delete_review(request, pk):
    """Удаление некорректного отзыва сотрудником"""
    review = get_object_or_404(Review, pk=pk)
    movie_title = review.movie.title
    review.delete()
    messages.success(request, f'Отзыв к фильму "{movie_title}" удален.')
    return redirect(request.META.get('HTTP_REFERER', 'cinema:staff_reviews'))


# Панель администратора

def admin_required(view_func):
    """Декоратор для проверки прав администратора"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Требуется авторизация.')
            return redirect('cinema:login')
        if request.user.role != 'admin':
            messages.error(request, 'У вас нет доступа к этой странице.')
            return redirect('cinema:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Панель администратора"""
    today = timezone.now().date()
    
    # Статистика
    total_users = User.objects.filter(role='user').count()
    total_movies = Movie.objects.filter(is_active=True).count()
    total_cinemas = Cinema.objects.filter(is_active=True).count()
    today_tickets = Ticket.objects.filter(
        booking_date__date=today,
        status__in=['booked', 'paid']
    ).count()
    
    # Последние билеты
    recent_tickets = Ticket.objects.filter(
        status__in=['booked', 'paid']
    ).order_by('-booking_date')[:10]
    
    # Непроверенные отзывы
    pending_reviews = Review.objects.filter(is_approved=False).count()
    
    context = {
        'total_users': total_users,
        'total_movies': total_movies,
        'total_cinemas': total_cinemas,
        'today_tickets': today_tickets,
        'recent_tickets': recent_tickets,
        'pending_reviews': pending_reviews,
    }
    return render(request, 'cinema/admin/dashboard.html', context)


@admin_required
def admin_movies(request):
    """Управление фильмами"""
    movies = Movie.objects.all().order_by('-created_at')
    
    context = {
        'movies': movies,
    }
    return render(request, 'cinema/admin/movies.html', context)


@admin_required
def admin_movie_create(request):
    """Создание фильма"""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Фильм успешно создан!')
            return redirect('cinema:admin_movies')
    else:
        form = MovieForm()
    
    context = {
        'form': form,
        'title': 'Создать фильм',
    }
    return render(request, 'cinema/admin/movie_form.html', context)


@admin_required
def admin_movie_edit(request, pk):
    """Редактирование фильма"""
    movie = get_object_or_404(Movie, pk=pk)
    
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Фильм успешно обновлен!')
            return redirect('cinema:admin_movies')
    else:
        form = MovieForm(instance=movie)
    
    context = {
        'form': form,
        'movie': movie,
        'title': 'Редактировать фильм',
    }
    return render(request, 'cinema/admin/movie_form.html', context)


@admin_required
def admin_movie_delete(request, pk):
    """Удаление фильма"""
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, 'Фильм успешно удален!')
    return redirect('cinema:admin_movies')


@admin_required
def admin_showtimes(request):
    """Управление сеансами"""
    from django.core.paginator import Paginator
    
    # Фильтры
    showtimes = ShowTime.objects.select_related('movie', 'hall', 'hall__cinema').all()
    
    # Фильтр по фильму
    movie_id = request.GET.get('movie')
    if movie_id:
        showtimes = showtimes.filter(movie_id=movie_id)
    
    # Фильтр по кинотеатру
    cinema_id = request.GET.get('cinema')
    if cinema_id:
        showtimes = showtimes.filter(hall__cinema_id=cinema_id)
    
    # Фильтр по дате
    date_str = request.GET.get('date')
    if date_str:
        from datetime import datetime
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            showtimes = showtimes.filter(start_time__date=selected_date)
        except ValueError:
            pass
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status == 'active':
        showtimes = showtimes.filter(is_active=True)
    elif status == 'inactive':
        showtimes = showtimes.filter(is_active=False)
    
    # Сортировка
    showtimes = showtimes.order_by('-start_time')
    
    # Пагинация (50 сеансов на страницу)
    paginator = Paginator(showtimes, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Список фильмов и кинотеатров для фильтров
    movies = Movie.objects.filter(is_active=True).order_by('title')
    cinemas = Cinema.objects.filter(is_active=True).order_by('name')
    
    context = {
        'showtimes': page_obj,
        'page_obj': page_obj,
        'movies': movies,
        'cinemas': cinemas,
        'total_count': paginator.count,
    }
    return render(request, 'cinema/admin/showtimes.html', context)


@admin_required
def admin_showtime_create(request):
    """Создание сеанса"""
    if request.method == 'POST':
        form = ShowTimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сеанс успешно создан!')
            return redirect('cinema:admin_showtimes')
    else:
        form = ShowTimeForm()
    
    context = {
        'form': form,
        'title': 'Создать сеанс',
    }
    return render(request, 'cinema/admin/showtime_form.html', context)


@admin_required
def admin_showtime_edit(request, pk):
    """Редактирование сеанса"""
    showtime = get_object_or_404(ShowTime, pk=pk)
    
    if request.method == 'POST':
        form = ShowTimeForm(request.POST, instance=showtime)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сеанс успешно обновлен!')
            return redirect('cinema:admin_showtimes')
    else:
        form = ShowTimeForm(instance=showtime)
    
    context = {
        'form': form,
        'showtime': showtime,
        'title': 'Редактировать сеанс',
    }
    return render(request, 'cinema/admin/showtime_form.html', context)


@admin_required
def admin_showtime_delete(request, pk):
    """Удаление сеанса"""
    showtime = get_object_or_404(ShowTime, pk=pk)
    showtime.delete()
    messages.success(request, 'Сеанс успешно удален!')
    return redirect('cinema:admin_showtimes')


@admin_required
def admin_cinemas(request):
    """Управление кинотеатрами"""
    cinemas = Cinema.objects.all()
    
    context = {
        'cinemas': cinemas,
    }
    return render(request, 'cinema/admin/cinemas.html', context)


@admin_required
def admin_cinema_create(request):
    """Создание кинотеатра"""
    if request.method == 'POST':
        form = CinemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кинотеатр успешно создан!')
            return redirect('cinema:admin_cinemas')
    else:
        form = CinemaForm()
    
    context = {
        'form': form,
        'title': 'Создать кинотеатр',
    }
    return render(request, 'cinema/admin/cinema_form.html', context)


@admin_required
def admin_cinema_edit(request, pk):
    """Редактирование кинотеатра"""
    cinema = get_object_or_404(Cinema, pk=pk)
    
    if request.method == 'POST':
        form = CinemaForm(request.POST, instance=cinema)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кинотеатр успешно обновлен!')
            return redirect('cinema:admin_cinemas')
    else:
        form = CinemaForm(instance=cinema)
    
    context = {
        'form': form,
        'cinema': cinema,
        'title': 'Редактировать кинотеатр',
    }
    return render(request, 'cinema/admin/cinema_form.html', context)


@admin_required
def admin_cinema_delete(request, pk):
    """Удаление кинотеатра"""
    cinema = get_object_or_404(Cinema, pk=pk)
    cinema.delete()
    messages.success(request, 'Кинотеатр успешно удален!')
    return redirect('cinema:admin_cinemas')


@admin_required
def admin_halls(request):
    """Управление залами"""
    halls = Hall.objects.all()
    
    context = {
        'halls': halls,
    }
    return render(request, 'cinema/admin/halls.html', context)


@admin_required
def admin_hall_create(request):
    """Создание зала"""
    if request.method == 'POST':
        form = HallForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Зал успешно создан!')
            return redirect('cinema:admin_halls')
    else:
        form = HallForm()
    
    context = {
        'form': form,
        'title': 'Создать зал',
    }
    return render(request, 'cinema/admin/hall_form.html', context)


@admin_required
def admin_hall_edit(request, pk):
    """Редактирование зала"""
    hall = get_object_or_404(Hall, pk=pk)
    
    if request.method == 'POST':
        form = HallForm(request.POST, instance=hall)
        if form.is_valid():
            form.save()
            messages.success(request, 'Зал успешно обновлен!')
            return redirect('cinema:admin_halls')
    else:
        form = HallForm(instance=hall)
    
    context = {
        'form': form,
        'hall': hall,
        'title': 'Редактировать зал',
    }
    return render(request, 'cinema/admin/hall_form.html', context)


@admin_required
def admin_hall_delete(request, pk):
    """Удаление зала"""
    hall = get_object_or_404(Hall, pk=pk)
    hall.delete()
    messages.success(request, 'Зал успешно удален!')
    return redirect('cinema:admin_halls')


@admin_required
def admin_promotions(request):
    """Управление акциями"""
    promotions = Promotion.objects.all().order_by('-start_date')
    
    context = {
        'promotions': promotions,
    }
    return render(request, 'cinema/admin/promotions.html', context)


@admin_required
def admin_promotion_create(request):
    """Создание акции"""
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Акция успешно создана!')
            return redirect('cinema:admin_promotions')
    else:
        form = PromotionForm()
    
    context = {
        'form': form,
        'title': 'Создать акцию',
    }
    return render(request, 'cinema/admin/promotion_form.html', context)


@admin_required
def admin_promotion_edit(request, pk):
    """Редактирование акции"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Акция успешно обновлена!')
            return redirect('cinema:admin_promotions')
    else:
        form = PromotionForm(instance=promotion)
    
    context = {
        'form': form,
        'promotion': promotion,
        'title': 'Редактировать акцию',
    }
    return render(request, 'cinema/admin/promotion_form.html', context)


@admin_required
def admin_promotion_delete(request, pk):
    """Удаление акции"""
    promotion = get_object_or_404(Promotion, pk=pk)
    promotion.delete()
    messages.success(request, 'Акция успешно удалена!')
    return redirect('cinema:admin_promotions')


@admin_required
def admin_rules(request):
    """Управление правилами"""
    rules = Rule.objects.all().order_by('order', 'title')
    
    context = {
        'rules': rules,
    }
    return render(request, 'cinema/admin/rules.html', context)


@admin_required
def admin_rule_create(request):
    """Создание правила"""
    if request.method == 'POST':
        form = RuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Правило успешно создано!')
            return redirect('cinema:admin_rules')
    else:
        form = RuleForm()
    
    context = {
        'form': form,
        'title': 'Создать правило',
    }
    return render(request, 'cinema/admin/rule_form.html', context)


@admin_required
def admin_rule_edit(request, pk):
    """Редактирование правила"""
    rule = get_object_or_404(Rule, pk=pk)
    
    if request.method == 'POST':
        form = RuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Правило успешно обновлено!')
            return redirect('cinema:admin_rules')
    else:
        form = RuleForm(instance=rule)
    
    context = {
        'form': form,
        'rule': rule,
        'title': 'Редактировать правило',
    }
    return render(request, 'cinema/admin/rule_form.html', context)


@admin_required
def admin_rule_delete(request, pk):
    """Удаление правила"""
    rule = get_object_or_404(Rule, pk=pk)
    rule.delete()
    messages.success(request, 'Правило успешно удалено!')
    return redirect('cinema:admin_rules')


@admin_required
def admin_users(request):
    """Управление пользователями"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
    }
    return render(request, 'cinema/admin/users.html', context)


@admin_required
def admin_user_create(request):
    """Создание нового пользователя администратором"""
    from django.contrib.auth.forms import UserCreationForm
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'user')
        phone = request.POST.get('phone', '')
        
        if username and password:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.role = role if role in ['user', 'staff', 'admin'] else 'user'
                user.phone = phone
                user.save()
                messages.success(request, f'Пользователь {username} успешно создан!')
                return redirect('cinema:admin_users')
            except Exception as e:
                messages.error(request, f'Ошибка создания пользователя: {str(e)}')
    
    context = {
        'title': 'Создать пользователя',
    }
    return render(request, 'cinema/admin/user_create.html', context)


@admin_required
def admin_user_edit(request, pk):
    """Редактирование пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if role in ['user', 'staff', 'admin']:
            user.role = role
        user.email = email
        user.phone = phone
        user.is_active = is_active
        user.save()
        messages.success(request, 'Данные пользователя успешно обновлены!')
        return redirect('cinema:admin_users')
    
    context = {
        'edited_user': user,
    }
    return render(request, 'cinema/admin/user_edit.html', context)


@admin_required
def admin_user_reset_password(request, pk):
    """Сброс пароля пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Пароль пользователя {user.username} успешно изменен!')
        return redirect('cinema:admin_users')
    
    context = {
        'edited_user': user,
    }
    return render(request, 'cinema/admin/user_reset_password.html', context)


@admin_required
def admin_user_delete(request, pk):
    """Удаление пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    if user.id == request.user.id:
        messages.error(request, 'Вы не можете удалить свой собственный аккаунт!')
        return redirect('cinema:admin_users')
    
    username = user.username
    user.delete()
    messages.success(request, f'Пользователь {username} успешно удален!')
    return redirect('cinema:admin_users')


@admin_required
def admin_analytics(request):
    """Аналитика и отчеты"""
    today = timezone.now().date()
    
    # Продажи за последние 30 дней
    last_30_days = today - timedelta(days=30)
    tickets_data = Ticket.objects.filter(
        booking_date__date__gte=last_30_days,
        status__in=['booked', 'paid']
    ).values('booking_date__date').annotate(
        count=Count('id'),
        revenue=Sum('price')
    ).order_by('booking_date__date')
    
    # Самые популярные фильмы
    popular_movies = Movie.objects.annotate(
        tickets_count=Count('showtimes__tickets')
    ).order_by('-tickets_count')[:10]
    
    # Статистика по кинотеатрам
    cinema_stats = Cinema.objects.annotate(
        tickets_count=Count('halls__showtimes__tickets')
    ).order_by('-tickets_count')
    
    # Общая статистика
    total_revenue = Ticket.objects.filter(
        status__in=['booked', 'paid']
    ).aggregate(total=Sum('price'))['total'] or 0
    
    total_tickets = Ticket.objects.filter(
        status__in=['booked', 'paid']
    ).count()
    
    context = {
        'tickets_data': tickets_data,
        'popular_movies': popular_movies,
        'cinema_stats': cinema_stats,
        'total_revenue': total_revenue,
        'total_tickets': total_tickets,
    }
    return render(request, 'cinema/admin/analytics.html', context)


@admin_required
def admin_tickets(request):
    """Управление билетами"""
    from django.core.paginator import Paginator
    
    # Фильтры
    tickets = Ticket.objects.select_related('user', 'showtime__movie', 'showtime__hall__cinema').all()
    
    # Фильтр по пользователю
    user_query = request.GET.get('user')
    if user_query:
        tickets = tickets.filter(
            Q(user__username__icontains=user_query) |
            Q(user__email__icontains=user_query)
        )
    
    # Фильтр по фильму
    movie_id = request.GET.get('movie')
    if movie_id:
        tickets = tickets.filter(showtime__movie_id=movie_id)
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)
    
    # Фильтр по дате
    date_str = request.GET.get('date')
    if date_str:
        from datetime import datetime
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            tickets = tickets.filter(booking_date__date=selected_date)
        except ValueError:
            pass
    
    # Сортировка
    tickets = tickets.order_by('-booking_date')
    
    # Пагинация (50 билетов на страницу)
    paginator = Paginator(tickets, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Список фильмов для фильтра
    movies = Movie.objects.filter(is_active=True).order_by('title')
    
    context = {
        'tickets': page_obj,
        'page_obj': page_obj,
        'movies': movies,
        'total_count': paginator.count,
        'now': timezone.now(),
    }
    return render(request, 'cinema/admin/tickets.html', context)


@admin_required
def admin_ticket_cancel(request, pk):
    """Отмена билета администратором"""
    if request.method != 'POST':
        messages.error(request, 'Неверный метод запроса.')
        return redirect('cinema:admin_tickets')
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if ticket.status == 'cancelled':
        messages.warning(request, 'Билет уже отменен.')
    else:
        old_status = ticket.get_status_display()
        ticket.status = 'cancelled'
        ticket.save()
        messages.success(request, f'Билет #{ticket.id} пользователя {ticket.user.username} успешно отменен! (был: {old_status})')
    
    return redirect('cinema:admin_tickets')
