# forms.py
from django import forms
from .models import Usuario, Custo, Parametro

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'nivel']
        widgets = {
            'password': forms.PasswordInput(),
        }

class CustoForm(forms.ModelForm):
    class Meta:
        model = Custo
        fields = ['codigo', 'descricao', 'unidade', 'valor']

class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = ['parametro', 'valor']