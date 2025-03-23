# forms.py
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario, Custo, Parametro

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,  # Não obrigatório na edição
        help_text="Deixe em branco para manter a senha atual (ao editar)."
    )
    
    class Meta:
        model = Usuario
        # Ajuste estes campos para corresponder ao seu modelo Usuario
        fields = ['username', 'email', 'password', 'nivel']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se for uma edição, a senha não é obrigatória
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
    
    def clean_password(self):
        """
        Processa o campo de senha:
        - Se for um novo usuário, a senha é obrigatória
        - Se for edição e senha estiver vazia, mantém a senha atual
        - Se for edição e senha for fornecida, criptografa a nova senha
        """
        password = self.cleaned_data.get('password')
        if self.instance.pk and not password:
            # Se é edição e senha vazia, retorna a senha existente
            return self.instance.password
        elif password:
            # Se senha fornecida, criptografa
            return make_password(password)
        return password
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Apenas define a senha se foi fornecida no formulário
        password = self.cleaned_data.get('password')
        if password:
            usuario.password = password
            
        if commit:
            usuario.save()
        return usuario
class CustoForm(forms.ModelForm):
    class Meta:
        model = Custo
        fields = ['codigo', 'descricao', 'unidade', 'valor']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'unidade': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
        }

class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = ['parametro', 'valor']
        widgets = {
            'parametro': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'valor': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }