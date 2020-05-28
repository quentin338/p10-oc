from django import forms


class UserForm(forms.Form):
    email = forms.EmailField(label="Votre email", required=True)
    password = forms.CharField(label="Votre mot de passe", max_length=128,
                               required=True, widget=forms.PasswordInput(attrs={"class": "password-field"}))
