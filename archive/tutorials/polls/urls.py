from django.urls import path

from . import views

urlpatterns = [
    #path("", views.intro, name="intro"),
    path("hello1/", views.hello_string, name="hello_string"),
    path("hello2/", views.hello_js, name="hello_js"),
    path("hello3/", views.hello_template, name="hello_template"),
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote")
    ]
