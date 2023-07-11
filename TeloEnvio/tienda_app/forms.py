from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Cliente, Producto,Pedido, DetallePedido, Productor


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', required=True,
                                max_length=50, min_length=5,
                                error_messages={
                                    'required': 'El usuario es obligatorio',
                                    'max_length': 'El usuario no puede superar los 50 caracteres',
                                    'min_length': 'El usuario debe tener al menos 5 caracteres'
                                },
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'Ingrese su usuario',
                                    'class': 'form-control'
                                })
                                )
    password = forms.CharField(label='Contraseña', required=True,
                                max_length=50, min_length=1,
                                error_messages={
                                    'required': 'La contraseña es obligatoria',
                                    'max_length': 'La contraseña no puede superar los 50 caracteres',
                                    'min_length': 'La contraseña debe tener al menos 1 caracter'
                                },
                                widget=forms.PasswordInput(attrs={
                                    'placeholder': 'Ingrese su contraseña',
                                    'class': 'form-control'
                                })
                                )



class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    fono = forms.CharField(max_length=20, required=True)  # Agregar campo telefono
    direccion = forms.CharField(max_length=100, required=True)
    comuna = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Cliente
        fields = ('username', 'first_name', 'last_name', 'email', 'fono','direccion','comuna', 'password1', 'password2')

class FormPedidogestion(forms.ModelForm):
    OPCIONES_ESTADO = [
        ('Pendiente', 'Pendiente'),
        ('Procesando', 'Procesando'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado')
    ]

    estado = forms.ChoiceField(
        choices=OPCIONES_ESTADO,
        required=True,
        error_messages={'required': 'El estado es requerido'},
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Seleccione el estado del pedido'
    )

    class Meta:
        model = Pedido
        fields = ['cliente', 'estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.all()

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']

    def __init__(self, pedido_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pedido_id = pedido_id

    def save(self, commit=True):
        detalle_pedido = super().save(commit=False)
        detalle_pedido.pedido_id = self.pedido_id
        detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
        if commit:
            detalle_pedido.save()
        return detalle_pedido
    
class AgregarProductoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(stock__gt=0))
    cantidad = forms.IntegerField(min_value=1, max_value=10)

OPCIONES_ESTADO = [
    ('Pendiente', 'Pendiente'),
    ('Procesando', 'Procesando'),
    ('Enviado', 'Enviado'),
    ('Entregado', 'Entregado'),
]

class ActualizarEstadoPedidoForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=OPCIONES_ESTADO)
    
    class Meta:
        model = Pedido
        fields = ['estado']

class ProductoForm(forms.ModelForm):
    productor = forms.ModelChoiceField(
        queryset=Productor.objects.all(),
        to_field_name='nombrecontacto',  # Cambia 'nombre' por el nombre del campo que contiene el nombre del productor
        label='Productor'
    )
    
    
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'descripcion', 'imagen', 'productor']

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen', False)
        if imagen:
            extension = imagen.name.split('.')[-1].lower()
            extensiones_permitidas = ['jpg', 'jpeg', 'png', 'gif']
            if extension not in extensiones_permitidas:
                raise forms.ValidationError(_('Formato de imagen no válido. Las extensiones permitidas son: .jpg, .jpeg, .png, .gif.'))
        return imagen
