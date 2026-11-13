from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import DatabaseError, IntegrityError
from django.shortcuts import redirect, render

from .decorators import cliente_requerido
from .forms_cuenta import CambiarPasswordForm, EliminarCuentaForm, PerfilForm
from .models import Cliente


def _datos_de(cliente):
    return {
        'nombre': cliente.nombre,
        'apellido': cliente.apellido,
        'direccion': cliente.direccion,
        'correo': cliente.correo,
    }


@cliente_requerido
def perfil(request):
    """Mi perfil: ver (GET) y editar / cambiar contraseña / eliminar (POST).

    Un solo formulario por acción, identificado con el campo oculto 'accion'.
    """
    cliente = request.cliente
    f_datos = PerfilForm(initial=_datos_de(cliente))
    f_pass = CambiarPasswordForm()
    f_elim = EliminarCuentaForm()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ----- Editar datos -----
        if accion == 'datos':
            f_datos = PerfilForm(request.POST)
            if f_datos.is_valid():
                correo = f_datos.cleaned_data['correo'].lower()
                try:
                    if Cliente.objects.filter(correo__iexact=correo).exclude(pk=cliente.pk).exists():
                        f_datos.add_error('correo', 'Ese correo ya está en uso.')
                    else:
                        cliente.nombre = f_datos.cleaned_data['nombre']
                        cliente.apellido = f_datos.cleaned_data['apellido']
                        cliente.direccion = f_datos.cleaned_data['direccion']
                        cliente.correo = correo
                        cliente.save()
                        request.session['usuario'] = cliente.correo
                        messages.success(request, 'Tus datos se actualizaron.')
                        return redirect('perfil')
                except IntegrityError:
                    f_datos.add_error('correo', 'Ese correo ya está en uso.')
                except DatabaseError:
                    messages.error(request, 'No se pudieron guardar los cambios. Intenta de nuevo.')

        # ----- Cambiar contraseña -----
        elif accion == 'password':
            f_pass = CambiarPasswordForm(request.POST)
            if f_pass.is_valid():
                if not check_password(f_pass.cleaned_data['actual'], cliente.password):
                    f_pass.add_error('actual', 'La contraseña actual no es correcta.')
                else:
                    try:
                        cliente.password = make_password(f_pass.cleaned_data['nueva'])
                        cliente.save()
                        messages.success(request, 'Tu contraseña se cambió.')
                        return redirect('perfil')
                    except DatabaseError:
                        messages.error(request, 'No se pudo cambiar la contraseña. Intenta de nuevo.')

        # ----- Eliminar cuenta (solo por POST y con la contraseña) -----
        elif accion == 'eliminar':
            f_elim = EliminarCuentaForm(request.POST)
            if f_elim.is_valid():
                if cliente.rol == 'admin':
                    messages.error(request, 'Un administrador no puede eliminar su cuenta desde aquí.')
                elif not check_password(f_elim.cleaned_data['password'], cliente.password):
                    f_elim.add_error('password', 'La contraseña no es correcta.')
                else:
                    try:
                        cliente.delete()
                    except DatabaseError:
                        messages.error(request, 'No se pudo eliminar la cuenta. Intenta de nuevo.')
                    else:
                        request.session.flush()
                        messages.success(request, 'Tu cuenta fue eliminada.')
                        return redirect('login')

        else:
            messages.error(request, 'Acción no válida.')

    return render(request, 'perfil.html', {
        'cliente': cliente,
        'f_datos': f_datos,
        'f_pass': f_pass,
        'f_elim': f_elim,
    })
