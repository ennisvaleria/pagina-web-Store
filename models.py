from django.db import models
 
 
class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
 
    def __str__(self):
        return self.nombre
 
 
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/')
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
 
    def __str__(self):
        return self.nombre
 
 
class Cliente(models.Model):
    ROLES = [('cliente', 'Cliente'), ('admin', 'Administrador')]
 
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # guarda el HASH (make_password), nunca texto plano
    telefono = models.CharField(max_length=20, blank=True, default='')
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')
    fecha_registro = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
 
 
class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
 
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    total = models.PositiveIntegerField(default=0)
    metodo_pago = models.CharField(max_length=30, blank=True, default='')
    direccion_envio = models.CharField(max_length=100, blank=True, default='')
 
    def __str__(self):
        return f"Pedido #{self.id} de {self.cliente}"
 
 
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()
 