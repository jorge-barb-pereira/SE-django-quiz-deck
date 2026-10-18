from django.contrib import admin
from .models import Player, Question, Game, Card


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "level", "correct_answer"]
    list_filter = ["level"]
    search_fields = ["text"]


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "best_score"]


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    can_delete = False
    readonly_fields = ["question", "selected_answer", "correct", "answered_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "score", "status", "started_at"]
    readonly_fields = [
        "player",
        "score",
        "status",
        "started_at",
        "expires_at",
        "finished_at",
    ]
    inlines = [CardInline]

    def has_add_permission(self, request):
        return False
