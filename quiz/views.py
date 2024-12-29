from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quiz, Question, Answer, Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.contrib.sessions.models import Session


def first(request):
    return render(request, 'quiz/first.html')

def home(request):
    # Если пользователь авторизован, но сессии ранее не было, разлогинить его
    if request.user.is_authenticated and not request.session.get('user_logged_in'):
        logout(request)  # Разлогин текущего пользователя
        request.session['user_logged_in'] = False  # Установить сессию для следующих проверок
    
    # Логика для входа, регистрации и т.д.
    if 'register' in request.POST:  # Регистрация пользователя
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:  # Проверка совпадения паролей
            messages.error(request, 'Пароли не совпадают.')
        elif User.objects.filter(username=username).exists():  # Проверка уникальности имени
            messages.error(request, 'Пользователь с таким именем уже существует.')
        else:
            user = User.objects.create_user(username=username, password=password1)  # Создание пользователя
            user.save()
            login(request, user)  # Сразу авторизуем нового пользователя
            request.session['user_logged_in'] = True  # Пометить пользователя как вошедшего
            messages.success(request, 'Регистрация прошла успешно. Вы вошли в систему.')
            return redirect('home')  # Редирект на главную

    if 'login' in request.POST:  # Вход в систему
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['user_logged_in'] = True  # Пометить пользователя как вошедшего
            messages.success(request, 'Вы вошли в систему.')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    if request.method == "POST":
        if 'logout' in request.POST:  # Разлогин
            logout(request)
            messages.success(request, "Вы вышли из системы.")
            return redirect('home')

    return render(request, 'quiz/home.html')


def custom_register(request):
    """
    Регистрирует пользователя через стандартную форму `UserCreationForm`.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():  # Проверка формы на корректность
            form.save()
            messages.success(request, 'Ваш аккаунт был создан успешно!')
            return redirect('login')
    else:
        form = UserCreationForm()  # Пустая форма
    return render(request, 'quiz/register.html', {'form': form})


def quiz_list(request):
    """
    Страница списка тестов.
    - Суперпользователь видит все тесты.
    - Обычные пользователи видят только тесты, созданные суперпользователями.
    """
    if request.user.is_superuser:
        quizzes = Quiz.objects.all()  # Все тесты для суперпользователя
    else:
        quizzes = Quiz.objects.filter(created_by__is_superuser=True)  # Тесты, созданные администратором
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


@user_passes_test(lambda u: u.is_superuser)
def delete_quiz(request, quiz_id):
    """
    Удаляет тест.
    - Доступно только суперпользователям.
    - Возвращает 403, если доступ к функции у обычного пользователя.
    """
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, id=quiz_id)  # Получение теста
        quiz.delete()  # Удаление теста
        return redirect('quiz_list')  # Перенаправление на список тестов
    return HttpResponseForbidden("Только суперпользователи могут удалять тесты.")


def quiz_detail(request, pk):
    """
    Детальная страница теста с отображением вопросов.
    """
    quiz = get_object_or_404(Quiz, pk=pk)  # Получение теста по идентификатору
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})


def check_results(request, pk):
    """
    Проверка результатов прохождения теста.
    - Рассчитывает количество правильных ответов.
    - Для вопросов с множественным выбором проверяет совпадение всех выбранных ответов.
    """
    quiz = get_object_or_404(Quiz, pk=pk)
    score = 0  # Начальный счет
    total_questions = quiz.questions.count()  # Общее количество вопросов

    if request.method == "POST":
        for question in quiz.questions.all():
            correct_answers = question.answers.filter(is_correct=True).values_list('id', flat=True)  # Идентификаторы правильных ответов
            if question.is_multiple_choice:
                selected_answers = request.POST.getlist(f"question_{question.id}[]")  # Выбранные ответы
                selected_answers = list(map(int, selected_answers))
                if set(selected_answers) == set(correct_answers):  # Проверка совпадения множественных ответов
                    score += 1
            else:
                selected_answer = request.POST.get(f"question_{question.id}")  # Ответ для одиночного выбора
                if selected_answer and int(selected_answer) in correct_answers:
                    score += 1

    return render(request, 'quiz/results.html', {
        'quiz': quiz,
        'score': score,
        'total_questions': total_questions,
    })


@user_passes_test(lambda u: u.is_superuser)
def create_quiz(request):
    """
    Создание нового теста.
    - Доступно только суперпользователям.
    - Обрабатывает динамическое добавление вопросов и ответов.
    """
    if request.method == 'POST':
        quiz = Quiz.objects.create(
            title=request.POST['title'],  # Заголовок теста
            description=request.POST['description'],  # Описание теста
            created_by=request.user  # Создатель теста
        )

        question_index = 0
        while f'question_text_{question_index}' in request.POST:
            question_text = request.POST[f'question_text_{question_index}']  # Текст вопроса
            is_multiple_choice = request.POST.get(f'is_multiple_choice_{question_index}') == 'multiple'
            question = Question.objects.create(
                quiz=quiz,
                question_text=question_text,
                is_multiple_choice=is_multiple_choice
            )

            answer_index = 0
            while f'answer_text_{question_index}_{answer_index}' in request.POST:
                answer_text = request.POST[f'answer_text_{question_index}_{answer_index}']  # Текст ответа
                is_correct = f'is_correct_{question_index}_{answer_index}' in request.POST  # Проверка правильности ответа
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    is_correct=is_correct
                )
                answer_index += 1

            question_index += 1

        return redirect('quiz_list')  # Перенаправление на список тестов

    return render(request, 'quiz/create_quiz.html')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал: создаёт профиль пользователя при регистрации.
    - Вызывается автоматически после сохранения объекта User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сигнал: сохраняет профиль пользователя при изменении модели User.
    """
    instance.profile.save()
