from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, RegistroForm


def inicio(request):
    return render(request, 'principal.html')

def login(request):
    return render(request, 'log_ing.html')

USUARIOS = {}

def inicio(request):
    user = USUARIOS.get(request.session.get('usuario'))
    nombre = f"{user['nombre']} {user['apellido']}" if user else 'Invitado'
    return render(request, 'principal.html', {'usuario': nombre})

def login(request):
    error_login = None
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo'].lower()
            user = USUARIOS.get(correo)
            if user and user['password'] == form.cleaned_data['password']:
                request.session['usuario'] = correo
                return redirect('inicio')
            error_login = 'Correo o contraseña incorrectos.'
    return render(request, 'log_ing.html', {'form': form, 'erro_login': error_login})

def registro(request):
    if request.method != 'POST':
        return redirect('login')

    form = RegistroForm(request.POST)
    if form.is_valid():
        correo = form.cleaned_data['correo'].lower()
        if correo in USUARIOS:
            form.add_error('correo', 'El correo ya está registrado.')
        else:
            USUARIOS[correo] = {
                'nombre': form.cleaned_data['nombre'],
                'apellido': form.cleaned_data['apellido'],
                'direccion': form.cleaned_data['direccion'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
            return redirect('login')

    return render(request, 'log_ing.html', {
        'form': LoginForm(),
        'registro_form': form,
        'mostrar_registro': True,
    })


def logout(request):
    request.session.flush()
    return redirect('login')