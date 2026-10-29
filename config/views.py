from django.http import HttpResponse
from django.http import JsonResponse
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
    return render(request, 'principal.html', {'usuario': nombre, 'productos': PRODUCTOS})

def api_productos(request):
    return JsonResponse(PRODUCTOS, safe=False)

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

PRODUCTOS = [
    {'nombre': 'Mouse Gamer Scyrox V8 Yellow', 'precio': '$85.990', 'imagen': 'images/scyrox_v8s_yellow.png',
     'descripcion': 'El Scyrox V8 es un mouse gamer diseñado para ofrecer un alto rendimiento tanto en modo inalámbrico como cableado.'},
    {'nombre': 'Mouse Gamer Logitech G PRO X Superlight 2', 'precio': '$135.990', 'imagen': 'images/Logitech_Pro_X_Superlight_2_Lightspeed.jpg',
     'descripcion': 'La nueva evolución de un ícono de los juegos profesionales, con mayor velocidad y precisión.'},
    {'nombre': 'Teclado Gamer Logitech G PRO X 60', 'precio': '$178.990', 'imagen': 'images/Teclado_Gamer_Logitech_G_PRO_X_60.png',
     'descripcion': 'Teclado inalámbrico para juegos LIGHTSPEED con un 60 % menos de tamaño, KEYCONTROL y LIGHTSYNC RGB.'},
    {'nombre': 'Auriculares Gamer Logitech Astro A50 X Blanco Wireless', 'precio': '$335.990', 'imagen': 'images/Auriculares_Gamer_Logitech_Astro_A50_X_Blanco_Wireless.png',
     'descripcion': 'Diseñados para jugar con la innovadora tecnología PLAYSYNC.'},
    {'nombre': 'Silla Gamer Ergonómica Pro', 'precio': '$159.990', 'imagen': 'images/silla_gamer_economica_pro.png',
     'descripcion': 'Soporte lumbar ajustable y materiales transpirables para largas sesiones de juego.'},
    {'nombre': 'Monitor Gamer 24" 144Hz', 'precio': '$199.990', 'imagen': 'images/Monitor_144_economico.png',
     'descripcion': 'Experiencia fluida con tasa de refresco de 144Hz y tiempo de respuesta de 1ms.'},
    {'nombre': 'Alfombrilla Gamer XXL RGB', 'precio': '$25.990', 'imagen': 'images/Alfombrilla_xxl_rgb.png',
     'descripcion': 'Superficie optimizada para sensores ópticos con iluminación RGB perimetral.'},
    {'nombre': 'Micrófono Gamer USB Pro', 'precio': '$65.990', 'imagen': 'images/Microfono_gamer_usb.png',
     'descripcion': 'Audio cristalino para tus streams y llamadas con cancelación de ruido integrada.'},
]