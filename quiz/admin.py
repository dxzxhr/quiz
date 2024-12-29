from django.contrib import admin
from .models import Quiz, Question, Answer

# Создаем класс для настройки отображения модели Question в админке
class QuestionAdmin(admin.ModelAdmin):
    # Указываем, какие поля отображать в списке вопросов
    list_display = ('question_text', 'quiz', 'is_multiple_choice')  
    # Добавляем фильтры для удобного поиска по полям `quiz` и `is_multiple_choice`
    list_filter = ('quiz', 'is_multiple_choice')  
    # Разрешаем поиск по тексту вопроса
    search_fields = ('question_text',)  

# Регистрируем модель Quiz в админке с настройками по умолчанию
admin.site.register(Quiz)  

# Регистрируем модель Question в админке с использованием настроек из класса QuestionAdmin
admin.site.register(Question, QuestionAdmin)  

# Регистрируем модель Answer в админке с настройками по умолчанию
admin.site.register(Answer)  
