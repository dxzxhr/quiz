from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.first, name='first'),  # Главная приветственная страница
    path('home/', views.home, name='home'),  # Основная страница
    # Страница входа (используется стандартный класс LoginView)
    path('login/', auth_views.LoginView.as_view(), name='login'),
    # Страница выхода (используется стандартный класс LogoutView)
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Разлогин
    # Страница регистрации (обрабатывается кастомной функцией `custom_register`)
    path('register/', views.custom_register, name='register'),
    # Страница со списком тестов (доступна всем пользователям)
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    # Страница создания теста (доступна только суперпользователям)
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    # Детальная страница теста, отображает вопросы (доступна всем)
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    # Проверка результатов теста после его прохождения (обрабатывает ответы пользователя)
    path('quiz/<int:pk>/check_results/', views.check_results, name='check_results'),
    # Удаление теста (доступно только суперпользователям)
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
]
