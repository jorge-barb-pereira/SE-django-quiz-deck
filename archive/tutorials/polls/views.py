from django.shortcuts import render
from django.http import HttpResponse
from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    output = ", ".join([q.question_text for q in latest_question_list])
    return HttpResponse(output)

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

# Create your views here.
# !!! Bug, It's everythig in the same line
def intro(request):
    return HttpResponse('''Welcome to the Polls App.
                        
                        You may access the following pages:
                        1. /polls/hello1/ - A simple string response
                        2. /polls/hello2/ - A simple HTML response
                        3. /polls/hello3/ - A simple template response
                        ''')

def hello_string(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def hello_js(request):
    return HttpResponse(
        """
        <html>
            <head>
                <title>My First Web Page</title>
            </head>
            <body>
                <h1>Hello, world. You're at the polls index.</h1>
            </body>
        </html>
        """
        )

def hello_template(request):
    return render(request, "temp1.html",{'name':'George'})
