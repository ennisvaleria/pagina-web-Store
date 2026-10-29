from django import forms

class LoginForm(forms.Form):
    correo = forms.EmailField(max_length=50)
    password = forms.CharField(min_length=6)

class RegistroForm(forms.Form):
    nombre = forms.CharField(min_length=3, max_length=50)
    apellido = forms.CharField(min_length=3, max_length=50)
    direccion = forms.CharField(min_length=3, max_length=50)
    correo = forms.EmailField(max_length=50)
    password = forms.CharField(min_length=6)