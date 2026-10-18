from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

class IndexView(TemplateView):
    template_name = 'index.html'
