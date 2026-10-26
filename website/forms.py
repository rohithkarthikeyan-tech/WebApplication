from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': 'Your Full Name',
                'id': 'contact-name',
                'autocomplete': 'name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'glass-input',
                'placeholder': 'name@example.com',
                'id': 'contact-email',
                'autocomplete': 'email',
                'required': 'required',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': "What is this regarding?",
                'id': 'contact-subject',
                'required': 'required',
            }),
            'message': forms.Textarea(attrs={
                'class': 'glass-input glass-textarea',
                'placeholder': 'Tell us more about your ideas, questions, or project...',
                'id': 'contact-message',
                'rows': 5,
                'required': 'required',
            }),
        }


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Choose a username',
            'id': 'register-username',
            'autocomplete': 'username',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Enter your email address',
            'id': 'register-email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Create a secure password',
            'id': 'register-password',
            'autocomplete': 'new-password',
        })
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Confirm your password',
            'id': 'register-password-confirm',
            'autocomplete': 'new-password',
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match. Please verify and try again.")
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Enter username',
            'id': 'login-username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'glass-input',
            'placeholder': 'Enter password',
            'id': 'login-password',
            'autocomplete': 'current-password',
        })
    )
