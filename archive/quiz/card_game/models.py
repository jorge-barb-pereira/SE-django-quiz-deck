#Auth Models
from django.db import models

# This Student class is created or retrieved after the student is correctly authenticated
#
# name -> student's name
# student_id -> institutional number
# inst_email -> institutional email (created from student_id)
# mxm_score -> maximum score obtained by the student in the game
# n_games -> number of times the student has played a full game
class Student(models.Model):
    name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, unique=True)
    inst_email = models.EmailField(unique=True)
    mxm_score = models.IntegerField(default=0)
    n_games = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


#Game Models   
from django.utils import timezone

# This Question class should be created by the admin by importing several questions of different levels to the database
# The questions present in the database are randomly sampled at each game initialization and assigned to a certain card based on their level
#
# level -> question level
# question_text -> question text (should correctly handle markdown)
# answer_i {1,2,3,4} -> 4 answer texts (should correctly handle markdown)
# correct_answer = i -> correct answer index

class Question(models.Model):
    LEVEL_CHOICES = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
    ]

    level = models.IntegerField(choices=LEVEL_CHOICES)
    question_text = models.TextField()  # Pergunta escrita em Markdown
    answer_1 = models.CharField(max_length=255)
    answer_2 = models.CharField(max_length=255)
    answer_3 = models.CharField(max_length=255)
    answer_4 = models.CharField(max_length=255)
    correct_answer = models.IntegerField()  # Índice da resposta correta (1-4)

    def __str__(self):
        return f"Level {self.level}: {self.question_text[:50]}"

# This Game class is created or retrieved after the student presses the 'start game' button
# This class keeps track of the student's game session.
#
# student -> Student class that is taking the game
# score -> current score obtained by the student in the present game session
# start_time -> time at which the game session was initialized
# selected_answers -> track of the answers selected by the student (history)
# status -> status of the game session (ongoing or finished)
# [If a student is suddenly logged off and it was an ongoing game session, they should be able to continue playing the ongoing game session]

class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ('on going', 'Em andamento'),
        ('finish', 'Finalizado'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    duration_s = models.IntegerField(default=3600 * 1.5)
    selected_answers = models.JSONField(default=dict)  # Armazena as cartas respondidas, com status correto/incorreto
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='on going')
        
    def __str__(self):
        return f"Game for {self.student.name}"

# This Card class is created or retrieved after the student presses the 'start game' button
# This class keeps track of the student's game session.
#
# student -> Student class that is taking the game
# score -> current score obtained by the student in the present game session
# start_time -> time at which the game session was initialized
# selected_answers -> track of the answers selected by the student (history)
# status -> status of the game session (ongoing or finished)
# [If a student is suddenly logged off and it was an ongoing game session, they should be able to continue playing the ongoing game session]


class Card(models.Model):
    LEVEL_CHOICES = [
        (1, 'Nível 1'),
        (2, 'Nível 2'),
        (3, 'Nível 3'),
        (4, 'Nível 4'),
    ]
    STATUS_CHOICES = [
        ('unanswered', 'Sem Resposta'),
        ('correct', 'Resposta Correta'),
        ('wrong', 'Resposta Errada'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='cards')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unanswered')

    def __str__(self):
        return f"Card {self.id} - Level {self.level} - Status: {self.status}"
