from django import forms


class LoginForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Your name",
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Email address", widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class VerificationForm(forms.Form):
    code = forms.RegexField(
        r"^\d{6}$",
        label="Verification code",
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "pattern": "[0-9]{6}",
            }
        ),
    )


class AnswerForm(forms.Form):
    answer = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 5)], coerce=int, widget=forms.RadioSelect
    )
