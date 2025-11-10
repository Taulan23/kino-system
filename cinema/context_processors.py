from .models import City


def city_processor(request):
    """Добавляет список городов в контекст всех шаблонов"""
    cities = City.objects.filter(is_active=True)
    
    # Получить выбранный город из сессии
    selected_city_id = request.session.get('selected_city_id')
    selected_city = None
    
    if selected_city_id:
        try:
            selected_city = City.objects.get(id=selected_city_id, is_active=True)
        except City.DoesNotExist:
            pass
    
    return {
        'cities': cities,
        'selected_city': selected_city,
    }
