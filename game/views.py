"""Session-bound email-code demonstration and ownership-checked game views."""

from functools import wraps
import secrets
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import Http404
from django.middleware.csrf import rotate_token
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import salted_hmac
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST
from .forms import LoginForm, VerificationForm, AnswerForm
from .models import Player, Card, Game
from .services import (
    GameRuleError,
    start_game,
    current_game,
    submit_answer,
    finish_game,
)


def player_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        request.player = Player.objects.filter(
            pk=request.session.get("player_id")
        ).first()
        if not request.player:
            request.session.pop("player_id", None)
            return redirect("login")
        return view(request, *args, **kwargs)

    return never_cache(wrapped)


def _key(scope, value):
    return scope + ":" + salted_hmac("quiz-login", value).hexdigest()


@never_cache
@require_http_methods(["GET", "POST"])
def login(request):
    if request.session.get("player_id"):
        return redirect("home")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        cooldown = _key("resend", email)
        ip_key = _key("issuance", request.META.get("REMOTE_ADDR", "unknown"))
        if cache.get(_key("failures", email), 0) >= settings.LOGIN_MAX_ATTEMPTS:
            form.add_error(
                None, "Too many incorrect codes. Please try again in ten minutes."
            )
        elif cache.get(ip_key, 0) >= 10:
            form.add_error(None, "Too many sign-in requests. Please try again later.")
        elif not cache.add(cooldown, True, 60):
            form.add_error(
                None, "Please wait one minute before requesting another code."
            )
        else:
            if not cache.add(ip_key, 1, 3600):
                cache.incr(ip_key)
            code = f"{secrets.randbelow(1000000):06d}"
            send_mail(
                "Your Quiz Deck verification code",
                f"Your code is {code}. It expires in five minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            request.session["pending_login"] = {
                **form.cleaned_data,
                "code_hash": make_password(code),
                "issued_at": time.time(),
                "attempts": 0,
            }
            return redirect("verify")
    return render(
        request,
        "game/login.html",
        {
            "form": form,
            "console_demo": settings.EMAIL_BACKEND.endswith("console.EmailBackend"),
        },
    )


@never_cache
@require_http_methods(["GET", "POST"])
def verify(request):
    pending = request.session.get("pending_login")
    if not pending:
        return redirect("login")
    if time.time() - pending["issued_at"] >= settings.LOGIN_CODE_TTL:
        request.session.pop("pending_login", None)
        messages.error(request, "That code has expired. Request a new one.")
        return redirect("login")
    failures = _key("failures", pending["email"])
    if cache.get(failures, 0) >= settings.LOGIN_MAX_ATTEMPTS:
        request.session.pop("pending_login", None)
        messages.error(request, "Too many incorrect codes. Try again in ten minutes.")
        return redirect("login")
    form = VerificationForm(request.POST or None)
    if request.method == "POST":
        pending["attempts"] += 1
        valid = form.is_valid()
        if valid and check_password(form.cleaned_data["code"], pending["code_hash"]):
            player, _ = Player.objects.get_or_create(
                email=pending["email"], defaults={"name": pending["name"]}
            )
            request.session.pop("pending_login", None)
            request.session.cycle_key()
            rotate_token(request)
            request.session["player_id"] = player.pk
            cache.delete(failures)
            return redirect("home")
        if not cache.add(failures, 1, 600):
            cache.incr(failures)
        if pending["attempts"] >= settings.LOGIN_MAX_ATTEMPTS:
            request.session.pop("pending_login", None)
            messages.error(
                request, "Too many incorrect codes. Request a new one later."
            )
            return redirect("login")
        request.session["pending_login"] = pending
        if valid:
            form.add_error("code", "Incorrect code. Please try again.")
    return render(request, "game/verify.html", {"form": form})


@player_required
@require_http_methods(["GET", "POST"])
def home(request):
    if request.method == "POST":
        try:
            game = start_game(request.player.pk)
        except GameRuleError as exc:
            messages.error(request, str(exc))
        else:
            return redirect("dashboard", game_id=game.pk)
    active = request.player.games.filter(status="active").first()
    if active:
        current_game(request.player.pk, active.pk)
    games = request.player.games.order_by("-started_at")
    request.player.refresh_from_db()
    return render(
        request,
        "game/home.html",
        {
            "player": request.player,
            "games": games,
            "attempts_left": max(0, 3 - games.count()),
            "active": games.filter(status="active").first(),
        },
    )


@player_required
@require_http_methods(["GET", "POST"])
def dashboard(request, game_id):
    get_object_or_404(Game, pk=game_id, player=request.player)
    game = (
        finish_game(request.player.pk, game_id)
        if request.method == "POST"
        else current_game(request.player.pk, game_id)
    )
    if game.status == "finished":
        return redirect("result", game_id=game.pk)
    cards = game.cards.select_related("question").order_by("question__level", "pk")
    return render(request, "game/dashboard.html", {"game": game, "cards": cards})


@player_required
@require_http_methods(["GET", "POST"])
def question(request, card_id):
    card = get_object_or_404(
        Card.objects.select_related("question", "game"),
        pk=card_id,
        game__player=request.player,
    )
    game = current_game(request.player.pk, card.game_id)
    if game.status == "finished":
        return redirect("result", game_id=game.pk)
    if card.answered_at:
        return redirect("dashboard", game_id=game.pk)
    form = AnswerForm(request.POST or None)
    form.fields["answer"].choices = [
        (i, getattr(card.question, f"answer_{i}")) for i in range(1, 5)
    ]
    if request.method == "POST" and form.is_valid():
        game = submit_answer(request.player.pk, card.pk, form.cleaned_data["answer"])
        return redirect(
            "result" if game.status == "finished" else "dashboard", game_id=game.pk
        )
    return render(
        request, "game/question.html", {"game": game, "card": card, "form": form}
    )


@player_required
@require_http_methods(["GET"])
def result(request, game_id):
    get_object_or_404(Game, pk=game_id, player=request.player)
    game = current_game(request.player.pk, game_id)
    if game.status == "active":
        return redirect("dashboard", game_id=game.pk)
    return render(request, "game/result.html", {"game": game})


@require_POST
def logout(request):
    request.session.flush()
    return redirect("login")
