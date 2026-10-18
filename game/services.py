"""Game transitions are atomic and always scoped to the verified player."""

from datetime import timedelta
import secrets
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest, Least
from django.utils import timezone
from .models import Player, Question, Game, Card


class GameRuleError(Exception):
    pass


def _finish(game, now):
    if game.status == "active":
        game.status = "finished"
        game.finished_at = now
        game.save(update_fields=["status", "finished_at"])
        Player.objects.filter(pk=game.player_id).update(
            best_score=Greatest(F("best_score"), game.score)
        )
    return game


@transaction.atomic
def start_game(player_id):
    player = Player.objects.select_for_update().get(pk=player_id)
    now = timezone.now()
    active = (
        Game.objects.select_for_update().filter(player=player, status="active").first()
    )
    if active:
        return active if active.expires_at > now else _finish(active, now)
    if player.games.count() >= 3:
        raise GameRuleError("You have used all three game attempts.")
    selected = []
    for level in range(1, 5):
        available = list(Question.objects.filter(level=level).order_by("pk"))
        if len(available) < 5 - level:
            raise GameRuleError(
                "The question bank is not ready. Please contact the administrator."
            )
        selected.extend(secrets.SystemRandom().sample(available, 5 - level))
    game = Game.objects.create(player=player, expires_at=now + timedelta(minutes=90))
    Card.objects.bulk_create(
        [Card(game=game, question=question) for question in selected]
    )
    return game


@transaction.atomic
def current_game(player_id, game_id):
    game = Game.objects.select_for_update().get(pk=game_id, player_id=player_id)
    if game.status == "active" and game.expires_at <= timezone.now():
        _finish(game, timezone.now())
    return game


@transaction.atomic
def submit_answer(player_id, card_id, answer):
    if isinstance(answer, bool) or answer not in (1, 2, 3, 4):
        raise GameRuleError("Choose one of the four answers.")
    card = Card.objects.select_related("question").get(
        pk=card_id, game__player_id=player_id
    )
    game = Game.objects.select_for_update().get(pk=card.game_id, player_id=player_id)
    now = timezone.now()
    if game.status != "active":
        return game
    if game.expires_at <= now:
        return _finish(game, now)
    correct = answer == card.question.correct_answer
    changed = Card.objects.filter(pk=card.pk, answered_at__isnull=True).update(
        selected_answer=answer, correct=correct, answered_at=now
    )
    if changed and correct:
        Game.objects.filter(pk=game.pk).update(
            score=Least(F("score") + card.points, 20)
        )
    game.refresh_from_db()
    if game.score >= 20 or not game.cards.filter(answered_at__isnull=True).exists():
        _finish(game, now)
    return game


@transaction.atomic
def finish_game(player_id, game_id):
    game = Game.objects.select_for_update().get(pk=game_id, player_id=player_id)
    return _finish(game, timezone.now())
