"""Maintained schema. Historical SQLite files are not compatible or required."""

from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    best_score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(best_score__lte=20), name="player_best_at_most_twenty"
            )
        ]

    def __str__(self):
        return self.name


class Question(models.Model):
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    text = models.TextField()
    answer_1 = models.CharField(max_length=255)
    answer_2 = models.CharField(max_length=255)
    answer_3 = models.CharField(max_length=255)
    answer_4 = models.CharField(max_length=255)
    correct_answer = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(level__gte=1, level__lte=4), name="question_valid_level"
            ),
            models.CheckConstraint(
                condition=Q(correct_answer__gte=1, correct_answer__lte=4),
                name="question_valid_answer",
            ),
        ]

    def __str__(self):
        return f"Level {self.level}: {self.text[:60]}"


class Game(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="games")
    score = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=8,
        choices=[("active", "Active"), ("finished", "Finished")],
        default="active",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(status="active"),
                name="one_active_game_per_player",
            ),
            models.CheckConstraint(
                condition=Q(score__lte=20), name="game_score_at_most_twenty"
            ),
        ]


class Card(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="cards")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_answer = models.PositiveSmallIntegerField(null=True, blank=True)
    correct = models.BooleanField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "question"], name="unique_game_question"
            ),
            models.CheckConstraint(
                condition=Q(selected_answer__isnull=True)
                | Q(selected_answer__gte=1, selected_answer__lte=4),
                name="card_valid_answer",
            ),
        ]

    @property
    def points(self):
        return self.question.level + 1

    @property
    def status_label(self):
        return (
            "Correct"
            if self.correct
            else ("Incorrect" if self.answered_at else "Unanswered")
        )
