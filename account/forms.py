from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    fullname = forms.CharField()
    class Meta:
        model = User
        fields = ['username', 'fullname', 'password1', 'password2']


    def validate(self, data):
        username = data.cleaned_data.get('username')
        fullname = data.cleaned_data.get('fullname')
        password1 = data.cleaned_data.get('password1')
        password2 = data.cleaned_data.get('password2')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this Username exists")

        if password1 != password2:
            raise forms.ValidationError("Password must be equal")

        if len(fullname.split(" ")) < 2:
            print('this error...')
            raise forms.ValidationError("Ensure to Enter your first and Last name")
        return data.cleaned_data
