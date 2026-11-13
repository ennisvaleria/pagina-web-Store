from functools import wraps
 
from django.contrib import messages
from django.db import DatabaseError
from django.shortcuts import redirect

from .models import Cliente
 
 
def admin_requerido(vista):
    """Deja pasar solo a quien tenga rol 'admin' guardado en la sesión.
    La Persona 2 guarda request.session['rol'] al iniciar sesión."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        # PARA PROBAR antes de que exista el login real, descomenta la línea de abajo
        # (y bórrala antes de entregar):
        # request.session['rol'] = 'admin'
        if request.session.get('rol') != 'admin':
            messages.error(request, 'No tienes permiso para entrar al panel.')
            return redirect('login')
        return vista(request, *args, **kwargs)
    return envoltura


def cliente_actual(request):
    """Devuelve el Cliente de la sesión (según el correo guardado) o None."""
    correo = request.session.get('usuario')
    if not correo:
        return None
    try:
        return Cliente.objects.filter(correo=correo).first()
    except DatabaseError:
        return None


def cliente_requerido(vista):
    """Exige haber iniciado sesión. Deja el Cliente en request.cliente.
    Úsenlo en /perfil, /mis-pedidos, /checkout, etc."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        cliente = cliente_actual(request)
        if cliente is None:
            request.session.flush()  # sesión vieja (por ejemplo, cuenta ya eliminada)
            messages.error(request, 'Inicia sesión para continuar.')
            return redirect('login')
        request.cliente = cliente
        return vista(request, *args, **kwargs)
    return envoltura
