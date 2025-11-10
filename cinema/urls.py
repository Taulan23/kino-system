from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    
    # Выбор города
    path('select-city/<int:city_id>/', views.select_city, name='select_city'),
    
    # Фильмы
    path('movies/', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:pk>/review/', views.add_review, name='add_review'),
    
    # Расписание
    path('schedule/', views.schedule, name='schedule'),
    
    # Кинотеатры
    path('cinemas/', views.cinema_list, name='cinema_list'),
    path('cinema/<int:pk>/', views.cinema_detail, name='cinema_detail'),
    
    # Акции
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('promotion/<int:pk>/', views.promotion_detail, name='promotion_detail'),
    
    # Правила
    path('rules/', views.rules, name='rules'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    
    # Бронирование билетов
    path('showtime/<int:pk>/book/', views.book_ticket, name='book_ticket'),
    path('ticket/<int:pk>/cancel/', views.cancel_ticket, name='cancel_ticket'),
    
    # Панель сотрудника
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/seats/<int:showtime_id>/', views.staff_seats, name='staff_seats'),
    path('staff/reviews/', views.staff_reviews, name='staff_reviews'),
    path('staff/review/<int:pk>/toggle/', views.toggle_review_approval, name='toggle_review_approval'),
    path('staff/review/<int:pk>/delete/', views.staff_delete_review, name='staff_delete_review'),
    
    # Панель администратора
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Управление фильмами
    path('admin-panel/movies/', views.admin_movies, name='admin_movies'),
    path('admin-panel/movie/create/', views.admin_movie_create, name='admin_movie_create'),
    path('admin-panel/movie/<int:pk>/edit/', views.admin_movie_edit, name='admin_movie_edit'),
    path('admin-panel/movie/<int:pk>/delete/', views.admin_movie_delete, name='admin_movie_delete'),
    
    # Управление сеансами
    path('admin-panel/showtimes/', views.admin_showtimes, name='admin_showtimes'),
    path('admin-panel/showtime/create/', views.admin_showtime_create, name='admin_showtime_create'),
    path('admin-panel/showtime/<int:pk>/edit/', views.admin_showtime_edit, name='admin_showtime_edit'),
    path('admin-panel/showtime/<int:pk>/delete/', views.admin_showtime_delete, name='admin_showtime_delete'),
    
    # Управление кинотеатрами
    path('admin-panel/cinemas/', views.admin_cinemas, name='admin_cinemas'),
    path('admin-panel/cinema/create/', views.admin_cinema_create, name='admin_cinema_create'),
    path('admin-panel/cinema/<int:pk>/edit/', views.admin_cinema_edit, name='admin_cinema_edit'),
    path('admin-panel/cinema/<int:pk>/delete/', views.admin_cinema_delete, name='admin_cinema_delete'),
    
    # Управление залами
    path('admin-panel/halls/', views.admin_halls, name='admin_halls'),
    path('admin-panel/hall/create/', views.admin_hall_create, name='admin_hall_create'),
    path('admin-panel/hall/<int:pk>/edit/', views.admin_hall_edit, name='admin_hall_edit'),
    path('admin-panel/hall/<int:pk>/delete/', views.admin_hall_delete, name='admin_hall_delete'),
    
    # Управление акциями
    path('admin-panel/promotions/', views.admin_promotions, name='admin_promotions'),
    path('admin-panel/promotion/create/', views.admin_promotion_create, name='admin_promotion_create'),
    path('admin-panel/promotion/<int:pk>/edit/', views.admin_promotion_edit, name='admin_promotion_edit'),
    path('admin-panel/promotion/<int:pk>/delete/', views.admin_promotion_delete, name='admin_promotion_delete'),
    
    # Управление правилами
    path('admin-panel/rules/', views.admin_rules, name='admin_rules'),
    path('admin-panel/rule/create/', views.admin_rule_create, name='admin_rule_create'),
    path('admin-panel/rule/<int:pk>/edit/', views.admin_rule_edit, name='admin_rule_edit'),
    path('admin-panel/rule/<int:pk>/delete/', views.admin_rule_delete, name='admin_rule_delete'),
    
    # Управление пользователями
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/user/create/', views.admin_user_create, name='admin_user_create'),
    path('admin-panel/user/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/user/<int:pk>/reset-password/', views.admin_user_reset_password, name='admin_user_reset_password'),
    path('admin-panel/user/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
    # Управление билетами
    path('admin-panel/tickets/', views.admin_tickets, name='admin_tickets'),
    path('admin-panel/ticket/<int:pk>/cancel/', views.admin_ticket_cancel, name='admin_ticket_cancel'),
    
    # Аналитика
    path('admin-panel/analytics/', views.admin_analytics, name='admin_analytics'),
]
