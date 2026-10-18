from django.urls import path
from . import views

urlpatterns = [
    # Primeira etapa: Nome e ID
    path('', views.init, name='init'),
    path('auth/step-1/', views.first_step, name='first_step'),
    
    # Segunda etapa: Verificação do código
    path('auth/step-2/', views.second_step, name='second_step'),
    
    # Páginas de redirecionamento
    path('game/instructions/', views.game_instructions, name='game_instructions'),
    path('game/max-attempts-exceeded/', views.max_attempts_exceeded, name='max_attempts_exceeded'),
    path('game/dashboard/', views.game_dashboard, name='game_dashboard'),
    path('game/card/<int:card_id>/', views.card_question, name='game_card_question'),  # Responder a pergunta
    path('game/end/', views.end, name='end'),  # Fim do jogo
]
