from datetime import timedelta
from io import StringIO
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from game.models import Player, Question, Game, Card
from game.services import (
    GameRuleError,
    start_game,
    submit_answer,
    finish_game,
    current_game,
)


class GameTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=StringIO())

    def setUp(self):
        self.player = Player.objects.create(
            name="Demo Player", email="player@example.invalid"
        )

    def test_deal_has_ten_unique_cards_with_expected_levels(self):
        game = start_game(self.player.pk)
        self.assertEqual(game.cards.count(), 10)
        self.assertEqual(
            [game.cards.filter(question__level=n).count() for n in range(1, 5)],
            [4, 3, 2, 1],
        )
        self.assertEqual(game.cards.values("question_id").distinct().count(), 10)

    def test_resume_does_not_consume_attempt(self):
        first = start_game(self.player.pk)
        self.assertEqual(start_game(self.player.pk).pk, first.pk)
        self.assertEqual(self.player.games.count(), 1)

    def test_missing_question_bank_rolls_back_game(self):
        Question.objects.filter(level=4).delete()
        with self.assertRaises(GameRuleError):
            start_game(self.player.pk)
        self.assertEqual(self.player.games.count(), 0)

    def test_attempt_limit_and_third_game_resume(self):
        for _ in range(2):
            finish_game(self.player.pk, start_game(self.player.pk).pk)
        third = start_game(self.player.pk)
        self.assertEqual(start_game(self.player.pk).pk, third.pk)
        finish_game(self.player.pk, third.pk)
        with self.assertRaises(GameRuleError):
            start_game(self.player.pk)
        self.assertEqual(self.player.games.count(), 3)

    def test_correct_answer_awards_points_once(self):
        game = start_game(self.player.pk)
        card = game.cards.select_related("question").first()
        submit_answer(self.player.pk, card.pk, 1)
        submit_answer(self.player.pk, card.pk, 1)
        game.refresh_from_db()
        card.refresh_from_db()
        self.assertEqual(game.score, card.points)
        self.assertTrue(card.correct)
        self.assertEqual(card.selected_answer, 1)

    def test_wrong_answer_is_final_and_earns_zero(self):
        game = start_game(self.player.pk)
        card = game.cards.first()
        submit_answer(self.player.pk, card.pk, 2)
        submit_answer(self.player.pk, card.pk, 1)
        game.refresh_from_db()
        card.refresh_from_db()
        self.assertEqual(game.score, 0)
        self.assertFalse(card.correct)
        self.assertEqual(card.selected_answer, 2)

    def test_expired_game_rejects_answer_after_more_than_a_day(self):
        game = start_game(self.player.pk)
        card = game.cards.first()
        Game.objects.filter(pk=game.pk).update(
            expires_at=timezone.now() - timedelta(days=2)
        )
        result = submit_answer(self.player.pk, card.pk, 1)
        card.refresh_from_db()
        self.assertEqual(result.status, "finished")
        self.assertEqual(result.score, 0)
        self.assertIsNone(card.answered_at)

    def test_current_game_expires_without_using_another_attempt(self):
        game = start_game(self.player.pk)
        Game.objects.filter(pk=game.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(current_game(self.player.pk, game.pk).status, "finished")
        self.assertEqual(self.player.games.count(), 1)

    def test_expired_resume_saves_completion(self):
        game = start_game(self.player.pk)
        Game.objects.filter(pk=game.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(start_game(self.player.pk).status, "finished")
        game.refresh_from_db()
        self.assertEqual(game.status, "finished")

    def test_score_caps_at_twenty_and_records_best(self):
        game = start_game(self.player.pk)
        for card in game.cards.all():
            submit_answer(self.player.pk, card.pk, 1)
        game.refresh_from_db()
        self.player.refresh_from_db()
        self.assertEqual(game.score, 20)
        self.assertEqual(game.status, "finished")
        self.assertEqual(self.player.best_score, 20)

    def test_all_wrong_cards_still_finish_the_game(self):
        game = start_game(self.player.pk)
        for card in game.cards.all():
            submit_answer(self.player.pk, card.pk, 2)
        game.refresh_from_db()
        self.assertEqual(game.status, "finished")

    def test_finished_game_retains_answer_history_and_best(self):
        game = start_game(self.player.pk)
        card = game.cards.first()
        submit_answer(self.player.pk, card.pk, 1)
        finish_game(self.player.pk, game.pk)
        self.assertEqual(game.cards.count(), 10)
        other = start_game(self.player.pk)
        finish_game(self.player.pk, other.pk)
        self.player.refresh_from_db()
        self.assertEqual(self.player.best_score, 2)

    def test_foreign_card_is_rejected_by_service(self):
        game = start_game(self.player.pk)
        other = Player.objects.create(name="Another", email="other@example.invalid")
        with self.assertRaises(Card.DoesNotExist):
            submit_answer(other.pk, game.cards.first().pk, 1)

    def test_invalid_answer_rejected_without_changes(self):
        game = start_game(self.player.pk)
        for value in [0, 5, "1", True, None]:
            with self.subTest(value=value):
                with self.assertRaises(GameRuleError):
                    submit_answer(self.player.pk, game.cards.first().pk, value)
        self.assertEqual(game.cards.filter(answered_at__isnull=False).count(), 0)

    def test_database_rejects_invalid_question_and_duplicate_active_game(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Question.objects.create(level=9, text="Invalid", correct_answer=1)
        game = start_game(self.player.pk)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Game.objects.create(player=self.player, expires_at=game.expires_at)

    def test_seed_is_idempotent_and_imports_no_participants(self):
        before = Question.objects.count()
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Question.objects.count(), before)
        self.assertEqual(Player.objects.count(), 1)


class GameViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=StringIO())

    def setUp(self):
        self.player = Player.objects.create(
            name="Sample", email="sample@example.invalid"
        )
        session = self.client.session
        session["player_id"] = self.player.pk
        session.save()

    def test_anonymous_access_redirects_without_data(self):
        game = start_game(self.player.pk)
        response = Client().get(reverse("dashboard", args=[game.pk]))
        self.assertRedirects(response, reverse("login"))

    def test_foreign_game_and_card_urls_are_not_accessible(self):
        other = Player.objects.create(name="Other", email="other@example.invalid")
        game = start_game(other.pk)
        card = game.cards.first()
        for route, pk in [
            ("dashboard", game.pk),
            ("result", game.pk),
            ("question", card.pk),
        ]:
            for method in ["get", "post"]:
                with self.subTest(route=route, method=method):
                    expected = 405 if route == "result" and method == "post" else 404
                    self.assertEqual(
                        getattr(self.client, method)(
                            reverse(route, args=[pk]), {"answer": "1"}
                        ).status_code,
                        expected,
                    )

    def test_invalid_form_does_not_consume_card(self):
        game = start_game(self.player.pk)
        card = game.cards.first()
        response = self.client.post(
            reverse("question", args=[card.pk]), {"answer": "invalid"}
        )
        self.assertEqual(response.status_code, 200)
        card.refresh_from_db()
        self.assertIsNone(card.answered_at)

    def test_complete_browser_flow_and_no_answer_leak(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        response = self.client.post(reverse("home"))
        game = self.player.games.get()
        self.assertRedirects(response, reverse("dashboard", args=[game.pk]))
        card = game.cards.first()
        response = self.client.get(reverse("question", args=[card.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "correct_answer")
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.client.post(reverse("question", args=[card.pk]), {"answer": "1"})
        self.client.post(reverse("dashboard", args=[game.pk]))
        response = self.client.get(reverse("result", args=[game.pk]))
        self.assertContains(response, "Your result is saved")

    def test_html_content_is_escaped(self):
        game = start_game(self.player.pk)
        card = game.cards.first()
        card.question.text = "<script>alert(1)</script>"
        card.question.save()
        response = self.client.get(reverse("question", args=[card.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_post_requires_csrf_and_logout_does_not_accept_get(self):
        client = Client(enforce_csrf_checks=True)
        session = client.session
        session["player_id"] = self.player.pk
        session.save()
        self.assertEqual(client.post(reverse("home")).status_code, 403)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

    def test_admin_remains_independent_of_player_login(self):
        response = Client().get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/admin/login/"))
