from django.db import models

# Create your models here.
class Proveedor (models.Model):
    nombre          = models.CharField(max_length=100)
    identificacion  = models.CharField(max_length=20, unique=True)
    descripcion     = models.TextField(blank=True, null=True)
    direccion       = models.CharField(max_length=200)
    ciudad          = models.CharField(max_length=100)
    telefono        = models.CharField(max_length=20)
    celular         = models.CharField(max_length=20)
    correo          = models.EmailField()

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"
    
    def nuevo (nombre, identificacion, descripcion, direccion, ciudad, telefono, celular, correo):
        Proveedor.save()
        Proveedor.objects.create(
            nombre=nombre, 
            identificacion=identificacion, 
            descripcion=descripcion, 
            direccion=direccion, 
            ciudad=ciudad, 
            telefono=telefono, 
            celular=celular, 
            correo=correo
        )

class Adquiscion (models.Model):
    proveedor   = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    factura     = models.CharField(max_length=50)
    fecha       = models.DateField()
    total       = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.fecha}"
    

class Producto (models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio      = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad    = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} - {self.precio}"


class Item_Adquiscion (models.Model):
    adquiscion  = models.ForeignKey(Adquiscion, on_delete=models.CASCADE)
    producto    = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad    = models.IntegerField()
    precio      = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.adquiscion.proveedor.nombre}"


class Kardex (models.Model):
    detalles    =   [('Compra','Compra'), ('Venta','Venta'), ('Baja','Baja'), ('Alta','Alta')]

    producto    = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='kardex')
    detalle     = models.CharField(max_length=20, choices=detalles, default='Compra')
    fecha       = models.DateField()
    cantidad    = models.IntegerField(default=0)
    saldo       = models.IntegerField(default=0)
    precio      = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        ## return f"{self.producto.nombre} - {self.fecha}"
        return f"Operación: {self.detalle} - Fecha: {self.fecha} - Cantidad: {self.cantidad} - Existencias: {self.saldo}"


class Cliente (models.Model):
    tipo            = [("cedula", "Cédula"), ("ruc", "RUC")]

    nombre              = models.CharField(max_length=100)
    apellido            = models.CharField(max_length=100)
    tipo_identificacion = models.CharField(max_length=20, choices=tipo)
    identificacion      = models.CharField(max_length=20, unique=True)
    direccion           = models.CharField(max_length=200)
    ciudad              = models.CharField(max_length=100)
    telefono            = models.CharField(max_length=20)
    celular             = models.CharField(max_length=20)
    correo              = models.EmailField()

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.identificacion}"
    

class Venta (models.Model):
    cliente     = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha       = models.DateField()
    factura     = models.CharField(max_length=50)
    total       = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fecha} - {self.total}"

class Item_Venta (models.Model):
    venta       = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto    = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad    = models.IntegerField()
    precio      = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio}"  