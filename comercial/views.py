import time
import json
from django.core import serializers
from rest_framework import serializers
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
# from django_ajax.decorators import ajax

from .models import Producto, Kardex, Marca, Compra, Item_Compra, Proveedor

# Create your views here.
def info_producto (request, producto_id):
    producto    = get_object_or_404(Producto, id=producto_id)
    kardex      = producto.kardex.all()
    contenido   = {
        'producto': producto,
        'kardex': kardex,
    }   
    return render(request, 'productos/info.html', contenido)

#@ajax
def lista_productos (request):
    ##productos   = Producto.objects.all()
    marcas      = Marca.objects.all()
    contenido   = {
        ## 'productos': productos,
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

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

def gestion_productos (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'crear_producto':
            try:
                producto                =   Producto()
                producto.codigo         =   request.POST['codigo']
                producto.marca          =   Marca.objects.get(id=request.POST['marca'])
                producto.nombre         =   request.POST['nombre']
                producto.presentacion   =   request.POST['presentacion']
                producto.descripcion    =   request.POST['descripcion']
                producto.precio         =   request.POST['precio']
                producto.save()
                response_data = {
                    'success': True,
                    'message': 'El producto fue creado correctamente.',
                }
                return JsonResponse(response_data, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear el producto: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'lista':
            ## productos   = serializers.serialize('json', Producto.objects.__str__())
            productos = Producto.objects.all()
            lista_productos = ProductoSerializer(productos, many=True)
            marcas      = Marca.objects.all()
            lista_marcas = MarcaSerializer(marcas, many=True)
            ## productos   =   Producto.objects.__str__()
            contenido   = {
                'productos': lista_productos.data,
                'marcas': lista_marcas.data,
            }
            return JsonResponse(contenido, status=201)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
            
def crear_compra (request):
    contenido   = {}
    contenido['proveedores']    =   Proveedor.objects.all()
    return render(request, 'compras/crear.html', contenido)

def gestion_compras (request):
    contenido = {}

    if request.method == 'POST':
        if request.POST['accion'] == 'crear_compra':
            try:
                ## compra.fecha   =   request.POST['fecha']
                factura         =   request.POST['factura']
                proveedor_id    =   request.POST['proveedor']
                proveedor       =   Proveedor.objects.get(id=proveedor_id)
                compra          =   Compra(proveedor=proveedor, factura=factura)
                compra.save()
                ## contenido['compra']     =   compra
                return JsonResponse({'success': True, 'message': 'La compra fue creada correctamente.'}, status=201)
            except Exception as e:
                response_data   =   {
                    'success': False,
                    'message': 'Error al crear la compra: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'lista_filtrada':
            if request.POST['filtrar'] == 'null':
                productos = Producto.objects.all()
            else:
                id = request.POST['filtrar']
                productos = Producto.objects.exclude(id__in=json.loads(id)).defer('descripcion')
            lista_productos = ProductoSerializer(productos, many=True)
            contenido['productos'] = lista_productos.data
            contenido['success'] = True
            return JsonResponse(contenido, status=201)
        if request.POST['accion'] == 'datos_productos':
            productos = Producto.objects.select_related.defer('descripcion')
            contenido = {
                'productos':    productos,
                'success':      True,
            }
            return JsonResponse(contenido, status=201)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

def lista_proveedores (request):
    contenido = {}
    return render(request, 'proveedores/lista.html', contenido)

def gestion_proveedores (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'lista':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                proveedores = Proveedor.objects.filter(estado=estado)
                lista_proveedores = ProveedorSerializer(proveedores, many=True)
                contenido   = {
                    'proveedores': lista_proveedores.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear el proveedor: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'crear_proveedor':
            try:
                proveedor                   =   Proveedor()
                proveedor.nombre            =   request.POST['nombre']
                proveedor.identificacion    =   request.POST['identificacion']
                proveedor.descripcion       =   request.POST['descripcion']
                proveedor.direccion         =   request.POST['direccion']
                proveedor.ciudad            =   request.POST['ciudad']
                proveedor.telefono          =   request.POST['telefono']
                proveedor.celular           =   request.POST['celular']
                proveedor.correo            =   request.POST['correo']
                proveedor.save()
                return JsonResponse({'success': True, 'message': 'El proveedor fue creado correctamente.'}, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear el proveedor: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'info':
            proveedor = ProveedorSerializer(Proveedor.objects.get(id=request.POST['id']))
            contenido = {
                'proveedor': proveedor.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'editar_proveedor':
            proveedor                   =   Proveedor.objects.get(id=request.POST['id'])
            proveedor.nombre            =   request.POST['nombre']
            proveedor.identificacion    =   request.POST['identificacion']
            proveedor.descripcion       =   request.POST['descripcion']
            proveedor.direccion         =   request.POST['direccion']
            proveedor.ciudad            =   request.POST['ciudad']
            proveedor.telefono          =   request.POST['telefono']
            proveedor.celular           =   request.POST['celular']
            proveedor.correo            =   request.POST['correo']
            proveedor.save()
            contenido = {
                'success': True,
                'message': 'El proveedor fue actualizado correctamente.',
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'deshabilitar_proveedor':
            proveedor = Proveedor.objects.get(id=request.POST['id'])
            proveedor.estado = False
            proveedor.save()
            contenido = {
                'success': True,
                'message': 'El proveedor fue deshabilitado correctamente.',
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'habilitar_proveedor':
            proveedor = Proveedor.objects.get(id=request.POST['id'])
            proveedor.estado = True
            proveedor.save()
            contenido = {
                'success': True,
                'message': 'El proveedor fue habilitado correctamente.',
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'buscar':
            if request.POST['estado'].lower() == 'true':
                estado = True
            else:
                estado = False
            print(estado)
            """ proveedores = Proveedor.objects.filter(
                Q(estado=estado) |
                (Q(nombre__icontains=request.POST['buscar']) | 
                Q(identificacion__icontains=request.POST['buscar']) | 
                Q(descripcion__icontains=request.POST['buscar']) | 
                Q(telefono__icontains=request.POST['buscar']) |
                Q(celular__icontains=request.POST['buscar']))
            ) """
            proveedores = Proveedor.objects.filter(estado=estado).filter(
                Q(nombre__icontains=request.POST['buscar']) | 
                Q(identificacion__icontains=request.POST['buscar']) | 
                Q(descripcion__icontains=request.POST['buscar']) | 
                Q(telefono__icontains=request.POST['buscar']) | 
                Q(celular__icontains=request.POST['buscar'])
            )
            lista_proveedores = ProveedorSerializer(proveedores, many=True)
            contenido   = {
                'proveedores': lista_proveedores.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)