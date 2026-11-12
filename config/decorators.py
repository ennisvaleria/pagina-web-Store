from functools import wraps
 
from django.contrib import messages
from django.shortcuts import redirect
 
 
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