from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, DESIGNATION_CHOICES, Department

class RegisterForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="select")
    designation = forms.ChoiceField(choices=[('', 'select')] + DESIGNATION_CHOICES)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'department', 'designation', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password']:
            self.fields[fieldname].help_text = None
