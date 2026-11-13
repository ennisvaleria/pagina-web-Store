from django.contrib import messages
from django.db import DatabaseError
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
 
from .decorators import admin_requerido
from .forms_admin import CategoriaForm, ProductoForm
from .models import Categoria, Producto
 
 
@admin_requerido
def panel(request):
    return redirect('panel_productos')
 
 
# ===== CRUD de productos =====
@admin_requerido
def panel_productos(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
 
    productos = Producto.objects.select_related('categoria').order_by('nombre')
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=categoria_id)
 
    return render(request, 'panel_productos.html', {
        'productos': productos,
        'categorias': Categoria.objects.order_by('nombre'),
        'q': q,
        'categoria_id': categoria_id,
    })
 
 
@admin_requerido
def producto_crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        try:
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado.')
            return redirect('panel_productos')
        except DatabaseError:
            messages.error(request, 'No se pudo guardar el producto. Intenta de nuevo.')
    return render(request, 'panel_form.html', {
        'form': form,
        'titulo': 'Nuevo producto',
        'volver': 'panel_productos',
    })
 
 
@admin_requerido
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado.')
            return redirect('panel_productos')
        except DatabaseError:
            messages.error(request, 'No se pudo actualizar el producto. Intenta de nuevo.')
    return render(request, 'panel_form.html', {
        'form': form,
        'titulo': f'Editar producto: {producto.nombre}',
        'volver': 'panel_productos',
    })
 
 
@admin_requerido
@require_POST
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    nombre = producto.nombre
    try:
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado.')
    except ProtectedError:
        messages.error(
            request,
            f'No se puede eliminar "{nombre}" porque ya aparece en pedidos. '
            'Edítalo y quita la marca "Visible en la tienda" para ocultarlo.'
        )
    except DatabaseError:
        messages.error(request, 'No se pudo eliminar el producto. Intenta de nuevo.')
    return redirect('panel_productos')
 
 
# ===== CRUD de categorías =====
@admin_requerido
def panel_categorias(request):
    return render(request, 'panel_categorias.html', {
        'categorias': Categoria.objects.order_by('nombre'),
    })
 
 
@admin_requerido
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada.')
            return redirect('panel_categorias')
        except DatabaseError:
            messages.error(request, 'No se pudo guardar la categoría. Intenta de nuevo.')
    return render(request, 'panel_form.html', {
        'form': form,
        'titulo': 'Nueva categoría',
        'volver': 'panel_categorias',
    })
 
 
@admin_requerido
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada.')
            return redirect('panel_categorias')
        except DatabaseError:
            messages.error(request, 'No se pudo actualizar la categoría. Intenta de nuevo.')
    return render(request, 'panel_form.html', {
        'form': form,
        'titulo': f'Editar categoría: {categoria.nombre}',
        'volver': 'panel_categorias',
    })
 
 
@admin_requerido
@require_POST
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    nombre = categoria.nombre
    try:
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
    except ProtectedError:
        messages.error(
            request,
            f'No se puede eliminar "{nombre}" porque tiene productos asociados. '
            'Mueve o elimina esos productos primero.'
        )
    except DatabaseError:
        messages.error(request, 'No se pudo eliminar la categoría. Intenta de nuevo.')
    return redirect('panel_categorias')