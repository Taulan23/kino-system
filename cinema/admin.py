from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, City, Genre, Movie, Cinema, Hall,
    ShowTime, Ticket, Review, Promotion, Rule
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'city', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'city']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'birth_date', 'city')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'birth_date', 'city')
        }),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'duration', 'rating', 'age_restriction', 'is_active']
    list_filter = ['is_active', 'genres', 'release_date']
    search_fields = ['title', 'director', 'cast']
    filter_horizontal = ['genres']
    date_hierarchy = 'release_date'


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'is_active']
    list_filter = ['city', 'is_active']
    search_fields = ['name', 'address']


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['name', 'cinema', 'rows', 'seats_per_row', 'total_seats']
    list_filter = ['cinema']
    search_fields = ['name', 'cinema__name']


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ['movie', 'hall', 'start_time', 'price', 'get_available_seats', 'is_active']
    list_filter = ['is_active', 'hall__cinema', 'start_time']
    search_fields = ['movie__title', 'hall__name']
    date_hierarchy = 'start_time'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'showtime', 'user', 'row', 'seat', 'price', 'status', 'booking_date']
    list_filter = ['status', 'booking_date']
    search_fields = ['user__username', 'showtime__movie__title']
    date_hierarchy = 'booking_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['user__username', 'movie__title', 'text']
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = 'Снять одобрение с выбранных отзывов'


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'discount_percent', 'start_date', 'end_date', 'is_active', 'is_valid']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'content']
    ordering = ['order', 'title']
