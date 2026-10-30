import unicodedata

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import LoginForm, RegistroForm

# Registro temporal en memoria (Taller 2: aún no se usa base de datos)
USUARIOS = {}

# Catálogo que entrega el backend (antes estaba escrito a mano en el HTML)
PRODUCTOS = [
    {
        'id': 1,
        'nombre': "Mouse Gamer Scyrox V8 Yellow",
        'descripcion': "El Scyrox V8 es un mouse gamer diseñado para ofrecer un alto rendimiento tanto en modo inalámbrico como cableado, ideal para jugadores competitivos en Chile que buscan precisión, velocidad y comodidad.",
        'precio': 85990,
        'imagen': 'images/scyrox_v8s_yellow.png',
    },
    {
        'id': 2,
        'nombre': "Mouse Gamer Logitech G PRO X Superlight 2",
        'descripcion': "El Logitech® G PRO X Superlight 2 es la nueva evolución de un ícono de los juegos profesionales, y te ayuda a llevar tu juego al siguiente nivel con mayor velocidad y precisión.",
        'precio': 135990,
        'imagen': 'images/Logitech_Pro_X_Superlight_2_Lightspeed.jpg',
    },
    {
        'id': 3,
        'nombre': "Teclado Gamer Logitech G PRO X 60",
        'descripcion': "Teclado inalámbrico para juegos LIGHTSPEED con un 60 % menos de tamaño, KEYCONTROL, LIGHTSYNC RGB e interruptores ópticos.",
        'precio': 178990,
        'imagen': 'images/Teclado_Gamer_Logitech_G_PRO_X_60.png',
    },
    {
        'id': 4,
        'nombre': "Auriculares Gamer Logitech Astro A50 X Blanco Wireless",
        'descripcion': "Los Astro A50 X están diseñados para jugar con la innovadora tecnología PLAYSYNC.",
        'precio': 335990,
        'imagen': 'images/Auriculares_Gamer_Logitech_Astro_A50_X_Blanco_Wireless.png',
    },
    {
        'id': 5,
        'nombre': "Silla Gamer Ergonómica Pro",
        'descripcion': "Silla diseñada para largas sesiones de juego con soporte lumbar ajustable y materiales transpirables.",
        'precio': 159990,
        'imagen': 'images/silla_gamer_economica_pro.png',
    },
    {
        'id': 6,
        'nombre': "Monitor Gamer 24\" 144Hz",
        'descripcion': "Experiencia fluida y sin cortes con tasa de refresco de 144Hz y tiempo de respuesta de 1ms.",
        'precio': 199990,
        'imagen': 'images/Monitor_144_economico.png',
    },
    {
        'id': 7,
        'nombre': "Alfombrilla Gamer XXL RGB",
        'descripcion': "Superficie optimizada para sensores ópticos con iluminación RGB perimetral ajustable.",
        'precio': 25990,
        'imagen': 'images/Alfombrilla_xxl_rgb.png',
    },
    {
        'id': 8,
        'nombre': "Micrófono Gamer USB Pro",
        'descripcion': "Captura audio cristalino para tus streams y llamadas con cancelación de ruido integrada.",
        'precio': 65990,
        'imagen': 'images/Microfono_gamer_usb.png',
    },
]


def _formato_precio(valor):
    return "$" + f"{valor:,}".replace(",", ".")


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _productos_para_mostrar(busqueda=""):
    q = _normalizar(busqueda.strip())
    resultado = []
    for p in PRODUCTOS:
        if q in _normalizar(p["nombre"] + " " + p["descripcion"]):
            resultado.append({**p, "precio_txt": _formato_precio(p["precio"])})
    return resultado


def inicio(request):
    user = USUARIOS.get(request.session.get('usuario'))
    nombre = f"{user['nombre']} {user['apellido']}" if user else 'Invitado'
    return render(request, 'principal.html', {
        'usuario': nombre,
        'productos': _productos_para_mostrar(),
    })


def login(request):
    error_login = None
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo'].lower()
            user = USUARIOS.get(correo)
            if user and check_password(form.cleaned_data['password'], user['password']):
                request.session['usuario'] = correo
                return redirect('inicio')
            error_login = 'Correo o contraseña incorrectos.'
    return render(request, 'log_ing.html', {'form': form, 'error_login': error_login})


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
                'password': make_password(form.cleaned_data['password']),
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


# ===== Consultas al backend (JSON) =====
def api_productos(request):
    """GET /api/productos  ->  lista de productos. Acepta ?q=texto para filtrar."""
    productos = [
        {
            "id": p["id"],
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "precio": p["precio"],
            "precio_txt": p["precio_txt"],
            "imagen": static(p["imagen"]),
        }
        for p in _productos_para_mostrar(request.GET.get("q", ""))
    ]
    return JsonResponse({"total": len(productos), "productos": productos},
                        json_dumps_params={"ensure_ascii": False})


def api_usuario(request):
    """GET /api/usuario  ->  datos del usuario con sesión activa (sin contraseña)."""
    correo = request.session.get("usuario")
    user = USUARIOS.get(correo)
    if not user:
        return JsonResponse({"autenticado": False})
    return JsonResponse({
        "autenticado": True,
        "correo": correo,
        "nombre": user["nombre"],
        "apellido": user["apellido"],
        "direccion": user["direccion"],
    }, json_dumps_params={"ensure_ascii": False})
