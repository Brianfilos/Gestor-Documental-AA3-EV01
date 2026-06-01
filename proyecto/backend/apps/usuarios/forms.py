from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Rol


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        }),
        label='Correo electrónico'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        }),
        label='Contraseña'
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label='Contraseña',
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'estado', 'idRol']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'idRol': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'estado': 'Estado',
            'idRol': 'Rol',
        }
