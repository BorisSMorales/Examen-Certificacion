from django.shortcuts import render, redirect, get_object_or_404
import random
from django.http import HttpResponse
import string
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views.generic import TemplateView, FormView, View
from tienda_app.forms import RegistroForm, LoginForm, FormPedidogestion, DetallePedidoForm, AgregarProductoForm, ActualizarEstadoPedidoForm, ProductoForm
from .models import Cliente, Pedido, DetallePedido, Producto
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum


# Create your views here.


def inicio(request):
    return render(request, 'inicio.html')

def lista_clientes(request) -> HttpResponse:
    users = User.objects.all()
    return render(request, 'clientes.html', {'users': users})

class ListaPedidosView(LoginRequiredMixin, TemplateView):
    template_name = 'lista_pedidos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_staff:
            context['pedidos'] = Pedido.objects.all()
        else:
            context['pedidos'] = Pedido.objects.filter(cliente=user.cliente)

        return context

class Ingreso(TemplateView):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, { "form": form })

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('Home')
            form.add_error('username', 'Credenciales incorrectas')
            return render(request, self.template_name, { "form": form })
        else:
            return render(request, self.template_name, { "form": form })


class RegistroView(TemplateView):
    template_name = 'registration/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('Home')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            cliente = Cliente.objects.create(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                fono=form.cleaned_data['fono'],
                comuna=form.cleaned_data['comuna'],
                direccion=form.cleaned_data['direccion']
            )
            cliente.set_password(form.cleaned_data['password1'])
            cliente.save()


            # Autenticar y realizar inicio de sesión
            user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            login(request, user)
            user.groups.add(Group.objects.get(name='grupo1'))  # Asignar usuario al grupo "grupo1"
            
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})
    

class PedidoGestionView(FormView):
    template_name = 'agregar_pedido_gestion.html'
    form_class = FormPedidogestion

    def form_valid(self, form):
        pedido = form.save(commit=False)
        pedido.cliente_id = form.cleaned_data['cliente'].id
        pedido.save()

        return redirect('detalle_pedido', pedido_id=pedido.id)
    
class DetallePedidoGestionView(View):
    template_name = 'detalle_pedido_gestion.html'

    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        detalles = DetallePedido.objects.filter(pedido=pedido)
        pedido.total = DetallePedido.objects.filter(pedido=pedido).aggregate(total=Sum('subtotal'))['total']
        pedido.save()
        return render(request, self.template_name, {'pedido': pedido, 'detalles': detalles})
    
class AgregarDetallePedidoView(FormView):
    template_name = 'agregar_detalle_pedido.html'
    form_class = DetallePedidoForm

    def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['pedido_id'] = int(self.kwargs['pedido_id'])
            return kwargs

    def form_valid(self, form):
            detalle_pedido = form.save(commit=False)
            detalle_pedido.pedido_id = self.kwargs['pedido_id']
            detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
            detalle_pedido.save()

            return redirect('detalles_pedido', pedido_id=detalle_pedido.pedido_id)

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['detalle_form'] = context['form']
            return context

class ListaProductosView(TemplateView):
    template_name = 'lista_productos.html'
    form_class = AgregarProductoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los productos disponibles
        productos = Producto.objects.all()
        context['productos'] = productos
        return context

    def post(self, request, *args, **kwargs):
        for producto in Producto.objects.all():
            form = self.form_class(request.POST, prefix=f'producto_{producto.id}')
            if form.is_valid():
                cantidad = form.cleaned_data['cantidad']

                # Obtener o crear el detalle del pedido
                pedido_id = request.session.get('pedido_id')
                if pedido_id:
                    pedido = Pedido.objects.get(id=pedido_id)
                else:
                    pedido = Pedido.objects.create(cliente=request.user, total=0, estado='Pendiente')

                # Asociar el producto al detalle del pedido
                DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)

        return redirect('lista_productos')

# class CrearPedidoView(TemplateView):
#     template_name = 'crear_pedido.html'

#     def post(self, request, *args, **kwargs):
#         # Crear el pedido
#         pedido = Pedido.objects.create(
#             cliente=Cliente.objects.get(username=request.user.username),
#             total=0,
#             estado='Pendiente'  # Agrega el estado correcto para el pedido
#         )

#         # Establecer la sesión del pedido del cliente
#         request.session['pedido_id'] = pedido.id

#         return redirect('lista_productos')
    
class AgregarProductoPedidoView(FormView):
    template_name = 'pedido_cliente.html'
    form_class = AgregarProductoForm

    def form_valid(self, form):
        producto = form.cleaned_data['producto']
        cantidad = form.cleaned_data['cantidad']

        pedido_id = self.request.session.get('pedido_id')
        if pedido_id:
            pedido = Pedido.objects.get(id=pedido_id)
        else:
            cliente = self.request.user.cliente
            pedido = Pedido.objects.create(cliente=cliente, estado='Pendiente', total=0)
            self.request.session['pedido_id'] = pedido.id

        detalle_pedido = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=producto.precio * cantidad
        )

        pedido.total += detalle_pedido.subtotal
        pedido.save()

        return redirect('detalles_pedido', pedido_id=pedido.id)

class EliminarPedidoView(View):
    template_name = 'eliminar_pedido.html'

    def get(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        return render(request, self.template_name, {'pedido': pedido})

    def post(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('lista_pedidos')
    
class ActualizarEstadoPedidoView(View):
    template_name = 'editar_estado.html'
    form_class = ActualizarEstadoPedidoForm

    def get(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        form = self.form_class(instance=pedido)
        opciones_estado = [
            {'valor': 'pendiente', 'etiqueta': 'Pendiente'},
            {'valor': 'en proceso', 'etiqueta': 'En proceso'},
            {'valor': 'enviado', 'etiqueta': 'Enviado'},
            {'valor': 'entregado', 'etiqueta': 'Entregado'},
        ]
        return render(request, self.template_name, {'pedido': pedido, 'form': form, 'opciones_estado': opciones_estado})

class CrearProductoView(View):
    template_name = 'crear_producto.html'
    form_class = ProductoForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)  # No guardar el objeto todavía
            # Realiza cualquier otra manipulación o validación necesaria en el objeto producto aquí
            producto.save()  # Guarda el objeto producto en la base de datos
            return redirect('lista_productos')

        return render(request, self.template_name, {'form': form})
    
class EliminarProductoView(TemplateView):
    template_name = 'eliminar_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        context['producto'] = producto
        return context

    def post(self, request, *args, **kwargs):
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        producto.delete()
        return redirect('lista_productos')
    