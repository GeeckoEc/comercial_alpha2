from django.db import models
from django.db.models import Sum, Count, Min, Max

# Create your models here.
class Proveedor (models.Model):
    estado          =   models.BooleanField(default=True)
    nombre          =   models.CharField(max_length=100)
    identificacion  =   models.CharField(max_length=20, unique=True)
    descripcion     =   models.TextField(blank=True, null=True)
    direccion       =   models.CharField(max_length=200)
    ciudad          =   models.CharField(max_length=100)
    telefono        =   models.CharField(max_length=20)
    celular         =   models.CharField(max_length=20)
    correo          =   models.EmailField()

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"
    

class Compra (models.Model): ## TO-DO 
    proveedor       =   models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    estado          =   models.BooleanField(default=True)
    factura         =   models.CharField(max_length=50)
    fecha           =   models.DateField(auto_now_add=True)
    total           =   models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.fecha}"
    

class Marca (models.Model):
    estado          =   models.BooleanField(default=True)
    nombre          =   models.CharField(max_length=100)
    descripcion     =   models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    

class Producto (models.Model):
    estado          =   models.BooleanField(default=True)
    codigo          =   models.CharField(max_length=50, default="---", unique=True)
    marca           =   models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True, related_name='productos')
    nombre          =   models.CharField(max_length=100)
    presentacion    =   models.CharField(max_length=100, blank=True, null=True)
    descripcion     =   models.TextField(blank=True, null=True)
    precio          =   models.DecimalField(max_digits=10, decimal_places=2)
    stock           =   models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - {self.marca.nombre} - {self.presentacion} - ${self.precio} - {self.stock} unidades."

    def deshabilitar (self):
        self.estado = False
        self.save()

    def habilitar (self):
        self.estado = True
        self.save()
    
    def calcular_stock (self):
        compras = Kardex.objects.filter(detalle = 'Compra', producto = self).aggregate(Sum('cantidad'))['cantidad__sum']
        ventas  = Kardex.objects.filter(detalle = 'Venta', producto = self).aggregate(Sum('cantidad'))['cantidad__sum']
        if compras is None: 
            compras = 0
        if ventas is None:
            ventas = 0
        self.stock = (compras - ventas)
        self.save()


class Item_Compra (models.Model):
    compra          =   models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto        =   models.ForeignKey(Producto, on_delete=models.CASCADE)
    estado          =   models.BooleanField(default=True)
    cantidad        =   models.IntegerField()
    costo           =   models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.compra.proveedor.nombre}"


class Kardex (models.Model):
    detalles        =   [('Compra','Compra'), ('Venta','Venta')]

    producto        =   models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='kardex')
    detalle         =   models.CharField(max_length=20, choices=detalles, default='Compra')
    fecha           =   models.DateField()
    cantidad        =   models.IntegerField(default=0)
    saldo           =   models.IntegerField(default=0)
    precio          =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        ## return f"{self.producto.nombre} - {self.fecha}"
        return f"Operación: {self.detalle} - Fecha: {self.fecha} - Cantidad: {self.cantidad} - Existencias: {self.saldo}"
    
    def guardar_calcular_saldo(self):
        self.save()
        self.producto.calcular_stock()
        self.saldo = self.producto.stock
        self.save()


class Cliente (models.Model):
    tipo                =   [("cedula", "Cédula"), ("ruc", "RUC")]

    estado              =   models.BooleanField(default=True)
    nombre              =   models.CharField(max_length=100)
    apellido            =   models.CharField(max_length=100)
    tipo_identificacion =   models.CharField(max_length=20, choices=tipo)
    identificacion      =   models.CharField(max_length=20, unique=True)
    direccion           =   models.CharField(max_length=200)
    ciudad              =   models.CharField(max_length=100)
    telefono            =   models.CharField(max_length=20)
    celular             =   models.CharField(max_length=20)
    correo              =   models.EmailField()

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.identificacion}"
    

class Venta (models.Model):
    estado          =   models.BooleanField(default=True)
    cliente         =   models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha           =   models.DateField()
    factura         =   models.CharField(max_length=50)
    total           =   models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fecha} - {self.total}"

class Item_Venta (models.Model):
    estado          =   models.BooleanField(default=True)
    venta           =   models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto        =   models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad        =   models.IntegerField()
    precio          =   models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio}"  