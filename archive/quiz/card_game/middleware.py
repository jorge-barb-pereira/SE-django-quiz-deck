# my_app/middleware.py

# This middleware tries to check on every page if the student is correctly authenticated.
# That is, if the student proved their authenticity through the correct input of their personal verification code
# That is, if the student successfully passed the authentication step-2 => request.session.get('authenticated') = True
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .models import Game

class AuthenticationRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #print(request.session.get('authenticated'))
        if not request.session.get('authenticated'):
            if request.path not in ["/auth/step-1/", "/auth/step-2/"]:
                return redirect('/auth/step-1/')  # Nome da view da primeira etapa

        response = self.get_response(request)
        return response
    
class QuestionAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se a URL acessada é do padrão game/card/<id>
        resolver_match = request.resolver_match
        if resolver_match and resolver_match.url_name == 'game_card':
            card_id = resolver_match.kwargs.get('card_id')
            
            if card_id:
                # Obtenha o jogo do aluno autenticado
                game = Game.objects.get(student=request.user.student, status='on going')

                # Obtenha a carta e verifique o status
                card = game.cards.get(id=card_id)
                if card.status != 'unanswered':
                    return redirect('game_dashboard')  # Redireciona se a carta já foi respondida

        # Continua o processamento normal da requisição
        response = self.get_response(request)
        return response
