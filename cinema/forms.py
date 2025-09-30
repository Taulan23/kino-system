from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Review, Movie, ShowTime, Cinema, Hall, Promotion, Rule


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Телефон'
        })
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'birth_date', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })


class UserLoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
        }


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 11)],
                attrs={'class': 'form-select'}
            ),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваш отзыв...'
            }),
        }
        labels = {
            'rating': 'Оценка (1-10)',
            'text': 'Текст отзыва',
        }


class MovieForm(forms.ModelForm):
    """Форма для создания/редактирования фильма"""
    class Meta:
        model = Movie
        fields = [
            'title', 'description', 'duration', 'release_date',
            'director', 'cast', 'genres', 'rating', 'age_restriction',
            'poster_url', 'trailer_url', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'director': forms.TextInput(attrs={'class': 'form-control'}),
            'cast': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'poster_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://i.imgur.com/image.jpg'}),
            'genres': forms.CheckboxSelectMultiple(),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'age_restriction': forms.TextInput(attrs={'class': 'form-control'}),
            'trailer_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'poster_url': 'Ссылка на постер',
            'trailer_url': 'Ссылка на трейлер',
        }


class ShowTimeForm(forms.ModelForm):
    """Форма для создания/редактирования сеанса"""
    class Meta:
        model = ShowTime
        fields = ['movie', 'hall', 'start_time', 'price', 'is_active']
        widgets = {
            'movie': forms.Select(attrs={'class': 'form-select'}),
            'hall': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CinemaForm(forms.ModelForm):
    """Форма для создания/редактирования кинотеатра"""
    class Meta:
        model = Cinema
        fields = ['name', 'city', 'address', 'phone', 'description', 'facilities', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'facilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://i.imgur.com/cinema.jpg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'image_url': 'Ссылка на изображение',
        }


class HallForm(forms.ModelForm):
    """Форма для создания/редактирования зала"""
    class Meta:
        model = Hall
        fields = ['cinema', 'name', 'rows', 'seats_per_row']
        widgets = {
            'cinema': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rows': forms.NumberInput(attrs={'class': 'form-control'}),
            'seats_per_row': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PromotionForm(forms.ModelForm):
    """Форма для создания/редактирования акции"""
    class Meta:
        model = Promotion
        fields = ['title', 'description', 'discount_percent', 'start_date', 'end_date', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RuleForm(forms.ModelForm):
    """Форма для создания/редактирования правила"""
    class Meta:
        model = Rule
        fields = ['title', 'content', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
