import time
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django_ajax.decorators import ajax

from .models import Producto, Kardex, Marca, Adquisicion, Item_Adquisicion, Proveedor

# Create your views here.
def vista_productos (request, producto_id):
    producto    = get_object_or_404(Producto, id=producto_id)
    kardex      = producto.kardex.all()
    contenido   = {
        'producto': producto,
        'kardex': kardex,
    }   
    return render(request, 'productos/info.html', contenido)

@ajax
def lista_productos (request):
    productos   = Producto.objects.all()
    marcas      = Marca.objects.all()
    contenido   = {
        'productos': productos,
        'marcas': marcas,
    }
    return render(request, 'productos/lista.html', contenido)

def crear_producto (request):
    if request.method == 'POST':
        producto                =   Producto()
        producto.codigo         =   request.POST['codigo']
        producto.marca          =   Marca.objects.get(id=request.POST['marca'])
        producto.nombre         =   request.POST['nombre']
        producto.presentacion   =   request.POST['presentacion']
        producto.descripcion    =   request.POST['descripcion']
        producto.precio         =   request.POST['precio']
        producto.save()
        time.sleep(5)
        return HttpResponse(reverse('lista_productos'))
    return HttpResponse('Error de método.')

def crear_adquisicion (request):
    contenido   = {}
    contenido['proveedores'] = Proveedor.objects.all()
    if request.method == 'POST':
        ## adquisicion.fecha   = request.POST['fecha']
        factura             = request.POST['factura']
        proveedor_id           = request.POST['proveedor_id']
        proveedor          = Proveedor.objects.get(id=proveedor_id)
        adquisicion         = Adquisicion(proveedor=proveedor, factura=factura)
        adquisicion.save()
        contenido['adquisicion'] = adquisicion
    return render(request, 'crear_adquisicion.html', contenido)