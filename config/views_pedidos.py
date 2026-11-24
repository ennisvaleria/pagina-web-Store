import json

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import admin_requerido
from .models import Cliente, DetallePedido, Pedido, Producto


def _cliente_de_sesion(request):
    correo = request.session.get("correo") or request.session.get("usuario")
    if not isinstance(correo, str):
        return None
    return Cliente.objects.filter(correo__iexact=correo, rol="cliente").first()


def _respuesta_error(mensaje, status):
    return JsonResponse({"error": mensaje}, status=status, json_dumps_params={"ensure_ascii": False})


@require_POST
def checkout(request):
    cliente = _cliente_de_sesion(request)
    if cliente is None:
        return _respuesta_error("Inicia sesión con una cuenta de cliente para comprar.", 401)

    try:
        datos = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _respuesta_error("La solicitud de compra no tiene un formato válido.", 400)

    items = datos.get("items") if isinstance(datos, dict) else None
    if not isinstance(items, list) or not items:
        return _respuesta_error("El carrito está vacío o no es válido.", 400)

    cantidades = {}
    for item in items:
        if not isinstance(item, dict):
            return _respuesta_error("Hay un producto inválido en el carrito.", 400)
        producto_id = item.get("id")
        cantidad = item.get("cantidad")
        if type(producto_id) is not int or type(cantidad) is not int or producto_id < 1 or cantidad < 1:
            return _respuesta_error("Los productos y cantidades del carrito no son válidos.", 400)
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

    with transaction.atomic():
        productos = {
            producto.pk: producto
            for producto in Producto.objects.select_for_update().filter(
                pk__in=cantidades, activo=True
            )
        }
        if len(productos) != len(cantidades):
            return _respuesta_error("Uno o más productos ya no están disponibles.", 400)

        total = 0
        for producto_id, cantidad in cantidades.items():
            producto = productos[producto_id]
            if producto.stock < cantidad:
                return _respuesta_error(
                    f"Stock insuficiente para {producto.nombre}. Disponibles: {producto.stock}.",
                    409,
                )
            total += producto.precio * cantidad

        if total > 2_147_483_647:
            return _respuesta_error("El total de la compra supera el máximo permitido.", 400)

        pedido = Pedido.objects.create(cliente=cliente, total=total)
        detalles = []
        for producto_id, cantidad in cantidades.items():
            producto = productos[producto_id]
            detalles.append(DetallePedido(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            ))
            producto.stock -= cantidad
            producto.save(update_fields=["stock"])
        DetallePedido.objects.bulk_create(detalles)

    return JsonResponse(
        {"pedido_id": pedido.pk, "total": pedido.total},
        status=201,
        json_dumps_params={"ensure_ascii": False},
    )


def mis_pedidos(request):
    cliente = _cliente_de_sesion(request)
    if cliente is None:
        messages.error(request, "Inicia sesión para consultar tus pedidos.")
        return redirect("login")

    pedidos = cliente.pedidos.prefetch_related("detalles__producto").order_by("-fecha")
    return render(request, "mis_pedidos.html", {"pedidos": pedidos})


@admin_requerido
def panel_pedidos(request):
    pedidos = Pedido.objects.select_related("cliente").order_by("-fecha")
    return render(request, "panel_pedidos.html", {"pedidos": pedidos})


@admin_requerido
def panel_pedido_detalle(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related("cliente").prefetch_related("detalles__producto"),
        pk=pk,
    )
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        estados_validos = dict(Pedido.ESTADOS)
        if nuevo_estado not in estados_validos:
            messages.error(request, "El estado seleccionado no es válido.")
        else:
            pedido.estado = nuevo_estado
            pedido.save(update_fields=["estado"])
            messages.success(request, f"El pedido #{pedido.pk} fue actualizado.")
            return redirect("panel_pedido_detalle", pk=pedido.pk)

    return render(request, "panel_pedido_detalle.html", {
        "pedido": pedido,
        "estados": Pedido.ESTADOS,
    })


@admin_requerido
def panel_clientes(request):
    clientes = Cliente.objects.filter(rol="cliente").order_by("apellido", "nombre")
    return render(request, "panel_clientes.html", {"clientes": clientes})


@admin_requerido
@require_POST
def panel_cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk, rol="cliente")
    nombre = f"{cliente.nombre} {cliente.apellido}"
    cliente.delete()
    messages.success(
        request,
        f'La cuenta de "{nombre}" fue eliminada junto con sus pedidos.',
    )
    return redirect("panel_clientes")
