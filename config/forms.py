from django import forms

class LoginForm(forms.Form):
    correo = forms.EmailField(max_length=50, label='Correo')
    password = forms.CharField(min_length=6, label='Contraseña')

class RegistroForm(forms.Form):
    nombre = forms.CharField(min_length=3, max_length=50, label='Nombre')
    apellido = forms.CharField(min_length=3, max_length=50, label='Apellido')
    direccion = forms.CharField(min_length=3, max_length=50, label='Dirección')
    correo = forms.EmailField(max_length=50, label='Correo')
    password = forms.CharField(min_length=6, label='Contraseña')