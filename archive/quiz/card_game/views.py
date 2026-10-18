import random
from .models import Student, Game, Card, Question
from .forms import FirstStepForm, SecondStepForm
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_control

def init(request):
    request.session.flush()
    return redirect('first_step')

#Autentication Step 1
def first_step(request):

    if request.method == "POST":
        form = FirstStepForm(request.POST)
        if form.is_valid():
            name_ss = form.cleaned_data['name']
            student_id_ss = form.cleaned_data['student_id']

            # Construir inst_email a partir do ID do estudante
            inst_email_ss = f"up{student_id_ss}@example.invalid"

            # Gerar código de verificação
            verification_code_ss = random.randint(100000, 999999)
            request.session['verification_code'] = verification_code_ss
            request.session['student_name'] = name_ss
            request.session['student_id'] = student_id_ss
            request.session['inst_email'] = inst_email_ss

            # Enviar e-mail com código de verificação
            print(f'Your code is {verification_code_ss}')
            # send_mail(
            # 'Your Verification Code',
            # f'Your code is {verification_code}',
            #      'no-reply@game.com',
            #      [inst_email],
            #      fail_silently=False,
            # )

            return redirect('second_step')
    
    else:
        form = FirstStepForm()

    return render(request, 'auth/first_step.html', {'form': form})

#Autentication Step 2
# View para a segunda etapa de autenticação
def second_step(request):
    if 'verification_code' not in request.session:
        return redirect('first_step')
    
    if request.method == 'POST':
        form_ss = SecondStepForm(request.POST)

        if form_ss.is_valid():
            verification_code_ss = form_ss.cleaned_data['verification_code']
            correct_code_ss = request.session.get('verification_code')

            # Verifique o código de verificação
            # Supondo que a lógica de verificação do código seja feita aqui
            if int(verification_code_ss) == correct_code_ss:
                # A autenticação foi bem-sucedida, busque ou crie o estudante
                student_id_ss = request.session.get('student_id')
                student_name_ss = request.session.get('student_name')
                inst_email_ss = request.session.get('inst_email')
                student_ss, created = Student.objects.get_or_create(student_id=student_id_ss,
                                                                 defaults={
                                                                    'name' : student_name_ss,
                                                                    'inst_email' : inst_email_ss,
                                                                    }
                                                                )
                # Armazene a autenticação na sessão
                request.session['authenticated'] = True
                request.session['student_id'] = student_id_ss  # ou outra forma de identificação
    
                return redirect('game_instructions')
            
            else:
                form_ss.add_error('verification_code', 'Código incorreto. Tente novamente.')
    else:
        form_ss = SecondStepForm()
    return render(request, 'auth/second_step.html', {'form': form_ss})

# View para as instruções do jogo
def game_instructions(request):
    # Supomos que o aluno já está autenticado e sua instância está disponível na sessão
    student_id = request.session.get('student_id')  # Assumindo que o ID do aluno está na sessão

    # Recuperar o estudante do banco de dados com base no ID
    student = Student.objects.get(student_id=student_id)

    # Passar os dados do estudante para o template
    context = {
        'name': student.name,
        'student_id': student_id,
        'n_games': student.n_games,
        'max_score': student.mxm_score
    }

    if request.method == 'POST':
        if student.n_games >= 3:
            return redirect('max_attempts_exceeded')

        game = initialize_game(student)
        request.session['game_id'] = game.id

        return redirect('game_dashboard')

    return render(request, 'game/instructions.html', context)

def initialize_game(student):
    # Verifica se o aluno tem um jogo em andamento
    ongoing_game = Game.objects.filter(student=student, status='on going').first()
    
    if ongoing_game:
        return ongoing_game

    # Cria um novo jogo
    new_game = Game.objects.create(student=student)
    student.n_games += 1
    student.save()

    # Amostra de perguntas por nível e Atribui as perguntas às cartas
    lvls = [1,2,3,4]
    for level in lvls:
        quests = random.sample(list(Question.objects.filter(level=level).order_by('?')), k=5-level)
        for question in quests:
            Card.objects.create(game=new_game, question=question, level=level)

    return new_game

# View para quando o número máximo de tentativas foi excedido
def max_attempts_exceeded(request):
    # Suponha que o ID do estudante logado esteja na sessão
    student_id = request.session.get('student_id')

    # Recuperar o estudante pelo ID
    student = Student.objects.get(student_id=student_id)
    name = student.name
    n_games = student.n_games  # Número de tentativas já usadas
    max_score = student.mxm_score  # Pontuação máxima

    context = {
        'name': name,
        'student_id': student_id,
        'n_games': n_games,
        'max_score': max_score,
    }
    if request.method == 'POST':
        return redirect('init')
    
    return render(request, 'game/max_attempts_exceeded.html', context)

# View para iniciar o jogo (apenas redireciona)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def game_dashboard(request):

    game_id = request.session.get('game_id')

    # Recupera o jogo do banco de dados usando o ID
    game = get_object_or_404(Game, id=game_id)


    # # # Tempo restante
    all_time_left_seconds = game.duration_s - (timezone.now() - game.start_time).seconds

    if (game.score >= 20) or (all_time_left_seconds) <= 0 or request.method == 'POST':
        game = end_game(game)
        return redirect('end')  # Redireciona para a página de fim de jogo
    
        # Organiza as cartas por nível
    level_1 = game.cards.filter(level=1)
    level_2 = game.cards.filter(level=2)
    level_3 = game.cards.filter(level=3)
    level_4 = game.cards.filter(level=4)


    return render(request, 'game/dashboard.html', {
        'game': game,
        'level_1': level_1,
        'level_2': level_2,
        'level_3': level_3,
        'level_4': level_4,
        'start_time': game.start_time,
        'duration_s' : game.duration_s
    })


def end_game(game):
        
    game.status = 'finish'  # Define o status do jogo como finalizado
    game.save()
    if game.score >= 20:
        game.student.mxm_score = 20
    elif game.score >= game.student.mxm_score:
        game.student.mxm_score = game.score
    game.student.save()
    Card.objects.filter(game=game).delete()
    return (game)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def card_question(request, card_id):
    # Recupera a carta e a questão associada
    card = get_object_or_404(Card, id=card_id)
    question = card.question

    if card.status != 'unanswered':  # Exemplo de status: 'unanswered', 'correct', 'wrong'
        return redirect('game_dashboard')

    if request.method == 'POST':
        
        # Lógica de verificação da resposta
        selected_option = request.POST.get('selected_option')

        if not selected_option:
            return redirect('game_card_question',card_id)
        
        selected_option = int(selected_option)  # Obtém a opção selecionada (1-4)

        if selected_option == question.correct_answer:
            card.status = 'correct'
            card.game.score += card.level + 1  # Incrementa o score com base no nível
        else:
            card.status = 'wrong'

        # Registra a resposta selecionada no campo `answered` da classe Game
        card.game.selected_answers[question.id] = selected_option
        card.save()
        card.game.save()

        # Redireciona de volta para a dashboard
        return redirect('game_dashboard')

    return render(request, 'game/question.html', {
        'card': card,
        'question': question,  # Passa a pergunta associada
        'answers': [question.answer_1, question.answer_2, question.answer_3, question.answer_4],  # Passa as respostas
        'game': card.game
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def end(request):

    game_id = request.session.get('game_id')

    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        return redirect('game_instructions')
    return render(request, 'game/end.html', {
        'game': game,
    })
