from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sign-in/", views.login, name="login"),
    path("verify/", views.verify, name="verify"),
    path("sign-out/", views.logout, name="logout"),
    path("games/<int:game_id>/", views.dashboard, name="dashboard"),
    path("cards/<int:card_id>/", views.question, name="question"),
    path("games/<int:game_id>/result/", views.result, name="result"),
]
