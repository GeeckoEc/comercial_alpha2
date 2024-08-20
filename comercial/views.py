import time
import json
from datetime import datetime, date
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


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


def index (request):
    return render(request, 'index.html')

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

def gestion_productos (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'lista':
            if request.POST['estado'].lower() == 'true':
                estado = True
            else:
                estado = False
            productos = Producto.objects.filter(estado=estado).defer('descripcion')
            lista_productos = ProductoSerializer(productos, many=True)
            marcas      = Marca.objects.all()
            lista_marcas = MarcaSerializer(marcas, many=True)
            contenido   = {
                'productos': lista_productos.data,
                'marcas': lista_marcas.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'lista_filtrada':
            if request.POST['filtrar'] == 'null':
                productos = Producto.objects.filter(estado=True)
            else:
                id = request.POST['filtrar']
                productos = Producto.objects.exclude(id__in=json.loads(id)).defer('descripcion')
            lista_productos = ProductoSerializer(productos, many=True)
            contenido = {
                'productos': lista_productos.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'crear_producto':
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
        elif request.POST['accion'] == 'editar_producto':
            producto = Producto.objects.get(id=request.POST['id'])
            producto.codigo = request.POST['codigo']
            producto.marca = Marca.objects.get(id=request.POST['marca'])
            producto.nombre = request.POST['nombre']
            producto.presentacion = request.POST['presentacion']
            producto.descripcion = request.POST['descripcion']
            producto.precio = request.POST['precio']
            producto.save()
            response_data = {
                'success': True,
                'message': 'El producto fue editado correctamente.',
            }
            return JsonResponse(response_data, status=201)
        elif request.POST['accion'] == 'deshabilitar_producto':
            producto = Producto.objects.get(id=request.POST['id'])
            producto.estado = False
            producto.save()
            response_data = {
                'success': True,
                'message': 'El producto fue deshabilitado correctamente.',
            }
            return JsonResponse(response_data, status=201)
        elif request.POST['accion'] == 'habilitar_producto':
            producto = Producto.objects.get(id=request.POST['id'])
            producto.estado = True
            producto.save()
            response_data = {
                'success': True,
                'message': 'El producto fue habilitado correctamente.',
            }
            return JsonResponse(response_data, status=201)
        elif request.POST['accion'] == 'info_producto':
            producto = Producto.objects.get(id=request.POST['id'])
            producto_serializer = ProductoSerializer(producto)
            marcas = Marca.objects.all()
            marcas_serializer = MarcaSerializer(marcas, many=True)
            contenido = {
                'producto': producto_serializer.data,
                'marcas': marcas_serializer.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'buscar':
            if request.POST['estado'].lower() == 'true':
                estado = True
            else:
                estado = False
            productos = Producto.objects.filter(estado=estado).filter(
                Q(codigo__icontains=request.POST['buscar']) |
                Q(nombre__icontains=request.POST['buscar']) |
                Q(presentacion__icontains=request.POST['buscar'])
            )
            lista_productos = ProductoSerializer(productos, many=True)
            marcas      = Marca.objects.all()
            lista_marcas = MarcaSerializer(marcas, many=True)
            contenido = {
                'productos': lista_productos.data,
                'marcas': lista_marcas.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'buscar_sin_seleccionar':
            if request.POST['filtrar'] == 'null':
                productos = Producto.objects.filter(estado=True)
            else:
                id = request.POST['filtrar']
                productos = Producto.objects.filter(estado=True).filter(
                    Q(codigo__icontains=request.POST['buscar']) |
                    Q(nombre__icontains=request.POST['buscar']) |
                    Q(presentacion__icontains=request.POST['buscar'])
                ).exclude(id__in=json.loads(id)).defer('descripcion')
            lista_productos = ProductoSerializer(productos, many=True)
            contenido = {
                'productos': lista_productos.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
            
def crear_compra (request):
    contenido   = {}
    contenido['proveedores']    =   Proveedor.objects.filter(estado=True)
    return render(request, 'compras/crear.html', contenido)

def gestion_compras (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'crear_compra':
            try:
                compra = Compra()
                compra.factura      =   request.POST['factura']
                compra.proveedor    =   request.POST['proveedor']
                compra.fecha        =   datetime.now()
                compra.total        =   request.POST['total']
                compra.save()
                for item in json.loads(request.POST['productos']):
                    item_compra             =   Item_Compra()
                    item_compra.compra      =   compra
                    item_compra.producto    =   Producto.objects.get(id=item['id'])
                    item_compra.cantidad    =   item['cantidad']
                    item_compra.costo      =   item['precio']
                    item_compra.save()
                
                return JsonResponse({'success': True, 'message': 'La compra fue creada correctamente.'}, status=201)
            except Exception as e:
                response_data   =   {
                    'success': False,
                    'message': 'Error al crear la compra: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

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

def lista_marcas (request):
    contenido = {}
    return render(request, 'marcas/lista.html', contenido)

def gestion_marcas (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'lista':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                marcas = Marca.objects.filter(estado=estado)
                lista_marcas = MarcaSerializer(marcas, many=True)
                contenido   = {
                    'marcas': lista_marcas.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al mostrar la marcas: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)