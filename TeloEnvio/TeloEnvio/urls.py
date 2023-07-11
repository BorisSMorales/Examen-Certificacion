"""
URL configuration for TeloEnvio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from tienda_app.views import inicio, Ingreso, RegistroView, ListaPedidosView, PedidoGestionView, DetallePedidoGestionView, AgregarDetallePedidoView, ListaProductosView,  AgregarProductoPedidoView,EliminarPedidoView, ActualizarEstadoPedidoView, CrearProductoView, EliminarProductoView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='Home'),
    path('login/',Ingreso.as_view(), name='Login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/',RegistroView.as_view(), name= 'Registro'),
    path('pedidos/', ListaPedidosView.as_view(), name='lista_pedidos'),
    path('agregar_pedido_gestion/', PedidoGestionView.as_view(), name='agregar_pedido'),  
    path('detalle-pedido_gestion/<int:pedido_id>/', DetallePedidoGestionView.as_view(), name='detalles_pedido'),
    path('agregar-detalle-pedido/<int:pedido_id>/', AgregarDetallePedidoView.as_view(), name='agregar_detalle_pedido'),
    path('productos/', ListaProductosView.as_view(), name='lista_productos'),
    path('agregar_pedido_cliente/', AgregarProductoPedidoView.as_view(), name='crear_pedido'),
    path('eliminar_pedido/<int:pedido_id>/', EliminarPedidoView.as_view(), name='eliminar_pedido'),
    path('pedidos/actualizar_estado/<int:pedido_id>/', ActualizarEstadoPedidoView.as_view(), name='actualizar_estado_pedido'),
    path('productos/crear/', CrearProductoView.as_view(), name='crear_producto'),
    path('productos/eliminar/<int:producto_id>/', EliminarProductoView.as_view(), name='eliminar_producto'),







]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)