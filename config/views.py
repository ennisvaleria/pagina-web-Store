import unicodedata

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import DatabaseError, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from .decorators import cliente_actual
from .forms import LoginForm, RegistroForm
from .models import Cliente, Producto


def _formato_precio(valor):
    return "$" + f"{valor:,}".replace(",", ".")


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _productos_para_mostrar(busqueda=""):
    q = _normalizar(busqueda.strip())
    productos = Producto.objects.filter(activo=True).order_by("nombre")
    if q:
        productos = [
            producto for producto in productos
            if q in _normalizar(f"{producto.nombre} {producto.descripcion}")
        ]
    return productos


@ensure_csrf_cookie
def inicio(request):
    cliente = cliente_actual(request)
    return render(request, "principal.html", {
        "usuario": f"{cliente.nombre} {cliente.apellido}" if cliente else "Invitado",
        "es_admin": bool(cliente and cliente.rol == "admin"),
        "productos": _productos_para_mostrar(),
    })


def login(request):
    error_login = None
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"].lower()
            try:
                cliente = Cliente.objects.filter(correo__iexact=correo).first()
            except DatabaseError:
                error_login = "No pudimos consultar la base de datos. Intenta de nuevo."
            else:
                if cliente and check_password(form.cleaned_data["password"], cliente.password):
                    request.session.cycle_key()
                    request.session["usuario"] = cliente.correo
                    request.session["rol"] = cliente.rol
                    return redirect("panel" if cliente.rol == "admin" else "inicio")
                error_login = "Correo o contraseña incorrectos."
    return render(request, "log_ing.html", {"form": form, "error_login": error_login})


def registro(request):
    if request.method != "POST":
        return redirect("login")

    form = RegistroForm(request.POST)
    if form.is_valid():
        correo = form.cleaned_data["correo"].lower()
        try:
            if Cliente.objects.filter(correo__iexact=correo).exists():
                form.add_error("correo", "El correo ya está registrado.")
            else:
                Cliente.objects.create(
                    nombre=form.cleaned_data["nombre"],
                    apellido=form.cleaned_data["apellido"],
                    direccion=form.cleaned_data["direccion"],
                    correo=correo,
                    password=make_password(form.cleaned_data["password"]),
                )
                messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
                return redirect("login")
        except IntegrityError:
            form.add_error("correo", "El correo ya está registrado.")
        except DatabaseError:
            form.add_error(None, "No pudimos guardar tu cuenta. Intenta de nuevo.")

    return render(request, "log_ing.html", {
        "form": LoginForm(),
        "registro_form": form,
        "mostrar_registro": True,
    })


def logout(request):
    request.session.flush()
    return redirect("login")


def api_productos(request):
    """GET /api/productos -> lista productos activos; acepta ?q=texto."""
    productos = [
        {
            "id": producto.pk,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": producto.precio,
            "precio_txt": _formato_precio(producto.precio),
            "imagen": producto.imagen.url if producto.imagen else "",
            "stock": producto.stock,
        }
        for producto in _productos_para_mostrar(request.GET.get("q", ""))
    ]
    return JsonResponse(
        {"total": len(productos), "productos": productos},
        json_dumps_params={"ensure_ascii": False},
    )


def api_usuario(request):
    """GET /api/usuario -> datos del cliente autenticado, sin contraseña."""
    cliente = cliente_actual(request)
    if not cliente:
        return JsonResponse({"autenticado": False})
    return JsonResponse({
        "autenticado": True,
        "id": cliente.id,
        "correo": cliente.correo,
        "nombre": cliente.nombre,
        "apellido": cliente.apellido,
        "direccion": cliente.direccion,
        "rol": cliente.rol,
        "fecha_registro": cliente.fecha_registro.isoformat(),
    }, json_dumps_params={"ensure_ascii": False})
