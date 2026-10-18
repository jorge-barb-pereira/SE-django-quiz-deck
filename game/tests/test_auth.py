import re
import time
from unittest.mock import patch
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from game.models import Player


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class AuthenticationTests(TestCase):
    def setUp(self):
        cache.clear()

    def issue(self, client=None):
        client = client or self.client
        response = client.post(
            reverse("login"),
            {"name": "Fictional Player", "email": "PLAYER@example.invalid"},
        )
        self.assertRedirects(response, reverse("verify"))
        return re.search(r"code is (\d{6})", mail.outbox[-1].body)[1]

    def test_code_is_emailed_and_hash_only_is_stored(self):
        code = self.issue()
        pending = self.client.session["pending_login"]
        self.assertEqual(pending["email"], "player@example.invalid")
        self.assertNotEqual(pending["code_hash"], code)
        self.assertNotIn("code", pending)
        self.assertEqual(Player.objects.count(), 0)

    def test_success_rotates_session_and_consumes_challenge(self):
        code = self.issue()
        old_key = self.client.session.session_key
        self.assertRedirects(
            self.client.post(reverse("verify"), {"code": code}), reverse("home")
        )
        session = self.client.session
        self.assertNotEqual(session.session_key, old_key)
        self.assertNotIn("pending_login", session)
        self.assertEqual(Player.objects.count(), 1)
        self.assertEqual(session["player_id"], Player.objects.get().pk)

    def test_malformed_code_is_validation_error_not_server_error(self):
        self.issue()
        self.assertEqual(
            self.client.post(reverse("verify"), {"code": "abcdef"}).status_code, 200
        )
        self.assertEqual(Player.objects.count(), 0)

    def test_expired_code_cannot_authenticate(self):
        code = self.issue()
        session = self.client.session
        pending = session["pending_login"]
        pending["issued_at"] = time.time() - 301
        session["pending_login"] = pending
        session.save()
        self.assertRedirects(
            self.client.post(reverse("verify"), {"code": code}), reverse("login")
        )
        self.assertEqual(Player.objects.count(), 0)

    def test_five_failures_revoke_code_and_limit_new_sessions(self):
        code = self.issue()
        wrong = "000000" if code != "000000" else "111111"
        for _ in range(5):
            self.client.post(reverse("verify"), {"code": wrong})
        self.assertNotIn("pending_login", self.client.session)
        another = Client()
        response = another.post(
            reverse("login"),
            {"name": "Fictional Player", "email": "player@example.invalid"},
        )
        self.assertContains(response, "Too many incorrect codes")
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_cooldown(self):
        self.issue()
        response = self.client.post(
            reverse("login"),
            {"name": "Fictional Player", "email": "player@example.invalid"},
        )
        self.assertContains(response, "wait one minute")
        self.assertEqual(len(mail.outbox), 1)

    def test_email_identity_cannot_be_changed_without_another_code(self):
        code = self.issue()
        self.client.post(
            reverse("verify"),
            {"code": code, "email": "other@example.invalid", "player_id": "999"},
        )
        self.assertEqual(Player.objects.get().email, "player@example.invalid")

    def test_logout_flushes_verified_session(self):
        code = self.issue()
        self.client.post(reverse("verify"), {"code": code})
        self.client.post(reverse("logout"))
        self.assertNotIn("player_id", self.client.session)
        self.assertRedirects(self.client.get(reverse("home")), reverse("login"))

    def test_verification_has_no_effect_without_session_challenge(self):
        self.assertRedirects(
            self.client.post(reverse("verify"), {"code": "123456"}), reverse("login")
        )
        self.assertEqual(Player.objects.count(), 0)
