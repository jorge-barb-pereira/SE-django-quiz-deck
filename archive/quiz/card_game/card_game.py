from django import forms

class FirstStepForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nome Completo")
    student_id = forms.CharField(max_length=10, label="Número de Estudante")

class SecondStepForm(forms.Form):
    verification_code = forms.CharField(max_length=6, label="Código de Verificação")
