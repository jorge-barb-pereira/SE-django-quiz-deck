from django.contrib import admin
from .models import Student, Question, Game, Card  # Importe seus modelos aqui

# Registra o modelo Student no admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'inst_email', 'n_games')  # Campos a serem exibidos
    search_fields = ('name', 'student_id', 'inst_email')  # Campos para pesquisa

# Registra o modelo Question no admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('level', 'question_text')
    search_fields = ('question_text',)

# Registra o modelo Game no admin
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('student', 'score', 'start_time')
    search_fields = ('student__name',)

# Registra o modelo Card no admin
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('game', 'question', 'level')
    search_fields = ('game__student__name', 'question__question_text')
