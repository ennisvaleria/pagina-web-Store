"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import views_admin
from . import views_pedidos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name="login"),
    path('registro', views.registro, name='registro'),
    path('principal', views.inicio, name='inicio'),
    path('logout', views.logout, name='logout'),
    path('api/productos', views.api_productos, name='api_productos'),
    path('api_productos', views.api_productos),
    path('api/usuario', views.api_usuario, name='api_usuario'),
    path('checkout', views_pedidos.checkout, name='checkout'),
    path('mis-pedidos', views_pedidos.mis_pedidos, name='mis_pedidos'),

    path('panel/', views_admin.panel, name='panel'),
    path('panel/productos/', views_admin.panel_productos, name='panel_productos'),
    path('panel/productos/nuevo/', views_admin.producto_crear, name='panel_producto_crear'),
    path('panel/productos/<int:pk>/editar/', views_admin.producto_editar, name='panel_producto_editar'),
    path('panel/productos/<int:pk>/eliminar/', views_admin.producto_eliminar, name='panel_producto_eliminar'),
    path('panel/categorias/', views_admin.panel_categorias, name='panel_categorias'),
    path('panel/categorias/nueva/', views_admin.categoria_crear, name='panel_categoria_crear'),
    path('panel/categorias/<int:pk>/editar/', views_admin.categoria_editar, name='panel_categoria_editar'),
    path('panel/categorias/<int:pk>/eliminar/', views_admin.categoria_eliminar, name='panel_categoria_eliminar'),
    path('panel/pedidos/', views_pedidos.panel_pedidos, name='panel_pedidos'),
    path('panel/pedidos/<int:pk>/', views_pedidos.panel_pedido_detalle, name='panel_pedido_detalle'),
    path('panel/clientes/', views_pedidos.panel_clientes, name='panel_clientes'),
    path('panel/clientes/<int:pk>/eliminar/', views_pedidos.panel_cliente_eliminar, name='panel_cliente_eliminar'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
