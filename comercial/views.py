import time
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
# from django_ajax.decorators import ajax

from .models import Producto, Kardex, Marca, Compra, Item_Compra, Proveedor

# Create your views here.
def vista_productos (request, producto_id):
    producto    = get_object_or_404(Producto, id=producto_id)
    kardex      = producto.kardex.all()
    contenido   = {
        'producto': producto,
        'kardex': kardex,
    }   
    return render(request, 'productos/info.html', contenido)

#@ajax
def lista_productos (request):
    productos   = Producto.objects.all()
    marcas      = Marca.objects.all()
    contenido   = {
        'productos': productos,
        'marcas': marcas,
    }
    return render(request, 'productos/lista.html', contenido)

""" def crear_producto (request):
    print(request.POST)
    if request.method == 'POST':
        producto                =   Producto()
        producto.codigo         =   request.POST['codigo']
        producto.marca          =   Marca.objects.get(id=request.POST['marca'])
        producto.nombre         =   request.POST['nombre']
        producto.presentacion   =   request.POST['presentacion']
        producto.descripcion    =   request.POST['descripcion']
        producto.precio         =   request.POST['precio']
        producto.save()
        time.sleep(3)
        return HttpResponseRedirect(reverse('lista_productos'))
    return HttpResponse('Error de método.') """

def crear_producto (request):
    if request.method == 'POST':
        try:
            """ producto                =   Producto()
            producto.codigo         =   request.POST['codigo']
            producto.marca          =   Marca.objects.get(id=request.POST['marca'])
            producto.nombre         =   request.POST['nombre']
            producto.presentacion   =   request.POST['presentacion']
            producto.descripcion    =   request.POST['descripcion']
            producto.precio         =   request.POST['precio']
            producto.save() """
            response_data = {
                'success': True,
                'message': 'Producto creado correctamente.'
            }
            return JsonResponse(response_data, status=201)
        except Exception as e:
            response_data = {
                'success': False,
                'message': 'Error al crear el  producto: {}'.format(str(e))
            }
            return JsonResponse(response_data, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
            

def crear_compra (request):
    contenido   = {}
    contenido['proveedores']    =   Proveedor.objects.all()
    if request.method == 'POST':
        ## compra.fecha   =   request.POST['fecha']
        factura         =   request.POST['factura']
        proveedor_id    =   request.POST['proveedor_id']
        proveedor       =   Proveedor.objects.get(id=proveedor_id)
        compra          =   Compra(proveedor=proveedor, factura=factura)
        compra.save()
        contenido['compra']     =   compra
    return render(request, 'compras/crear.html', contenido)