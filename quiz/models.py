from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Profile(models.Model):
    """
    Профиль пользователя с дополнительными полями.
    Этот класс расширяет встроенную модель User, добавляя возможность
    привязать дополнительные данные, специфичные для пользователя.
    """
    user = models.OneToOneField(
        User,  # Связь один к одному с пользователем
        on_delete=models.CASCADE,  # При удалении пользователя удаляется и профиль
        related_name="profile"  # Связь позволяет обращаться к профилю как `user.profile`
    )

    def __str__(self):
        # Представление профиля в читаемом формате
        return f"Профиль пользователя: {self.user.username}"


class Quiz(models.Model):
    """
    Модель теста.
    Хранит основные данные о тесте, такие как заголовок, описание, автор и дата создания.
    """
    title = models.CharField(
        max_length=255,  # Максимальная длина заголовка
        verbose_name="Заголовок теста"
    )
    description = models.TextField(
        blank=True,  # Поле может быть пустым
        verbose_name="Описание теста"
    )
    created_by = models.ForeignKey(
        User,  # Связь "многие к одному" с пользователем
        on_delete=models.CASCADE,  # Если пользователь удален, удаляются и его тесты
        verbose_name="Создатель теста"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,  # Устанавливается автоматически при создании
        verbose_name="Дата создания"
    )
    
    def __str__(self):
        # Представление теста в читаемом формате
        return self.title


class Question(models.Model):
    """
    Модель вопроса.
    Связана с определенным тестом и хранит текст вопроса, а также информацию
    о типе выбора ответа (множественный или одиночный).
    """
    QUIZ_TYPE_CHOICES = (
        (True, "Множественный выбор"),  # Вариант ответа с несколькими правильными вариантами
        (False, "Одиночный выбор")  # Только один правильный ответ
    )
    quiz = models.ForeignKey(
        Quiz,  # Связь "многие к одному" с тестом
        on_delete=models.CASCADE,  # Если тест удаляется, удаляются и связанные вопросы
        related_name="questions",  # Связь позволяет обращаться к вопросам как `quiz.questions`
        verbose_name="Тест"
    )
    question_text = models.CharField(
        max_length=500,  # Максимальная длина текста вопроса
        verbose_name="Текст вопроса"
    )
    is_multiple_choice = models.BooleanField(
        choices=QUIZ_TYPE_CHOICES,  # Выбор типа вопроса
        default=False,  # По умолчанию одиночный выбор
        verbose_name="Тип вопроса"
    )

    def __str__(self):
        # Представление вопроса в читаемом формате
        return f"Вопрос: {self.question_text}"


class Answer(models.Model):
    """
    Модель ответа.
    Связана с определенным вопросом и хранит текст ответа, а также информацию
    о его правильности.
    """
    question = models.ForeignKey(
        Question,  # Связь "многие к одному" с вопросом
        on_delete=models.CASCADE,  # Если вопрос удаляется, удаляются и связанные ответы
        related_name="answers",  # Связь позволяет обращаться к ответам как `question.answers`
        verbose_name="Вопрос"
    )
    answer_text = models.TextField(
        verbose_name="Текст ответа"  # Содержит текст ответа
    )
    is_correct = models.BooleanField(
        default=False,  # По умолчанию ответ считается неправильным
        verbose_name="Правильный ответ"  # Указывает, является ли этот ответ правильным
    )

    def __str__(self):
        # Представление ответа в читаемом формате
        return f"Ответ: {self.answer_text} ({'Правильный' if self.is_correct else 'Неправильный'})"
