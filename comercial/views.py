import time
import json
from datetime import datetime, date
from django.core import serializers as  dj_serializers

from rest_framework import serializers
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Sum, Subquery, OuterRef, Case, When, Exists
from django.db.models.functions import Coalesce
# from django_ajax.decorators import ajax

from .models import Producto, Kardex, Marca, Compra, Item_Compra, Proveedor, Cliente, Venta, Item_Venta
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

from django.db import IntegrityError

class ProductoSerializer(serializers.ModelSerializer):
    kardex_costo = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, default=0)
    kardex_precio = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True,  default=0)
    kardex_stock = serializers.IntegerField(allow_null=True, default=0)
    marca_nombre = serializers.CharField(source='marca.nombre')

    class Meta:
        model = Producto
        fields = '__all__'
        """ exclude = ['descripcion'] """
        extra_fields = ['kardex_costo', 'kardex_precio', 'kardex_stock']

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class  CompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre')
    proveedor_identificacion = serializers.CharField(source='proveedor.identificacion')

    class Meta:
        model = Compra
        fields = '__all__'

class Item_CompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre')
    producto_marca = serializers.CharField(source='producto.marca.nombre')

    class Meta:
        model = Item_Compra
        fields = '__all__'

class KardexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kardex
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
            estado = bool(request.POST.get('estado', False))
            kardex_subquery = Kardex.objects.filter(producto=OuterRef('pk')).order_by('-fecha')
            kardex = Exists(kardex_subquery)
            kardex_costo = kardex_subquery.values('costo')[:1]
            kardex_precio = kardex_subquery.values('precio')[:1]
            kardex_stock = kardex_subquery.values('stock')[:1]
            productos = Producto.objects.filter(estado=estado).select_related('marca').annotate(
                kardex_costo=Subquery(kardex_costo) if kardex else Coalesce(0),
                kardex_precio=Subquery(kardex_precio) if  kardex else Coalesce(0),
                kardex_stock=Subquery(kardex_stock)  if kardex else Coalesce(0),

            ).defer('descripcion')
            marcas      = Marca.objects.all()
            lista_marcas = MarcaSerializer(marcas, many=True)
            contenido   = {
                'productos': ProductoSerializer(productos,  many=True).data,
                'marcas': lista_marcas.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'lista_filtrada':
            if request.POST['filtrar'] == 'null':
                productos = Producto.objects.filter(estado=True).select_related('marca').annotate(
                    kardex_stock=Subquery(
                        Kardex.objects.filter(producto=OuterRef('pk'))
                        .order_by('-fecha').values('stock')[:1]
                    )
                )
            else:
                id = request.POST['filtrar']
                productos = Producto.objects.exclude(id__in=json.loads(id)).defer('descripcion').select_related('marca').annotate(
                    kardex_stock=Subquery(
                        Kardex.objects.filter(producto=OuterRef('pk'))
                        .order_by('-fecha').values('stock')[:1]
                    )
                )
            contenido = {
                'productos': ProductoSerializer(productos, many=True).data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'productos_seleccionados':
            try:
                lista = json.loads(request.POST['seleccionados'])
                ids = [item['id'] for item in lista]
                productos = Producto.objects.filter(id__in=ids).prefetch_related('marca')
                contenido = {
                    'productos': ProductoSerializer(productos, many=True).data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al encontrar los productos: {}'.format(str(e))
                }
                return  JsonResponse(response_data, status=500)
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
                kardex                  =   Kardex()
                kardex.producto         =   Producto.objects.get(id=producto.id)
                kardex.transaccion      =   'Creación de Producto'
                kardex.precio           =   producto.precio
                kardex.save()
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
            try:
                producto                =   Producto.objects.get(id=request.POST['id'])
                producto.codigo         =   request.POST['codigo']
                producto.marca          =   Marca.objects.get(id=request.POST['marca'])
                producto.nombre         =   request.POST['nombre']
                producto.presentacion   =   request.POST['presentacion']
                producto.descripcion    =   request.POST['descripcion']
                producto.precio         =   request.POST['precio']
                producto.save()
                kardex                  =   producto.kardex.latest('fecha')
                kardex.transaccion      =   'Edición de Producto'
                kardex.precio           =   producto.precio
                kardex.save()
                response_data = {
                    'success': True,
                    'message': 'El producto fue editado correctamente.',
                }
                return JsonResponse(response_data, status=201)
            except Exception  as e:
                response_data = {
                    'success': False,
                    'message': 'Error al editar el producto: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
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
            try:
                producto            =   Producto.objects.get(id=request.POST['id'])
                kardex              =   producto.kardex.latest('fecha')
                marca               =   producto.marca
                contenido           =   {
                    'producto': ProductoSerializer(producto).data,
                    'marca':   MarcaSerializer(marca).data,
                    'kardex':   KardexSerializer(kardex).data,
                    'success':  True
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al obtener la información del producto: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'informacion_producto':
            try:
                producto            =   Producto.objects.get(id=request.POST['id'])
                kardex              =   producto.kardex.latest('fecha')
                marca               =   producto.marca
                movimientos         =   Kardex.objects.filter(producto=producto)
                contenido           =   {
                    'producto': ProductoSerializer(producto).data,
                    'marca':   MarcaSerializer(marca).data,
                    'kardex':   KardexSerializer(kardex).data,
                    'movimientos': KardexSerializer(movimientos, many=True).data,

                    'success':  True
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al obtener la información del producto: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'buscar':
            if request.POST['estado'].lower() == 'true':
                estado = True
            else:
                estado = False
            productos = Producto.objects.filter(estado=estado).filter(
                Q(codigo__icontains=request.POST['buscar']) |
                Q(nombre__icontains=request.POST['buscar']) |
                Q(presentacion__icontains=request.POST['buscar']) |
                Q(marca__nombre__icontains=request.POST['buscar'])
            ).prefetch_related('marca')
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

def lista_compras (request):
    return render(request, 'compras/lista.html')

def gestion_compras (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'lista_compras':
            try:
                if  request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                compras = Compra.objects.filter(estado=estado).prefetch_related('proveedor')
                lista_compras = CompraSerializer(compras, many=True)
                contenido   = {
                    'compras': lista_compras.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al listar las compras: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'crear_compra':
            try:
                compra = Compra()
                compra.factura      =   request.POST['factura']
                compra.proveedor    =   Proveedor.objects.get(id=request.POST['proveedor'])
                compra.fecha        =   datetime.now()
                compra.total        =   request.POST['total']
                compra.save()
                items = json.loads(request.POST['items'])
                for item in items:
                    producto    =   Producto.objects.get(id=item['id'])
                    kardex      =   producto.kardex.latest('fecha')
                    nuevo_kardex    =   Kardex.objects.create(
                        producto        =   producto,
                        transaccion     =   'Compra',
                        costo           =   item['costo'],
                        precio          =   kardex.precio,
                        cantidad        =   item['cantidad'],
                        stock           =   int(kardex.stock) + int(item['cantidad'])
                    )
                    nuevo_item      =   Item_Compra.objects.create(
                        compra          =   compra,
                        producto        =   producto,
                        cantidad        =   item['cantidad'],
                        costo           =   item['costo']
                    )
                return JsonResponse({'success': True, 'message': 'La compra fue creada correctamente.'}, status=201)
            except Exception as e:
                response_data   =   {
                    'success': False,
                    'message': 'Error al crear la compra: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'info_compra':
            compra = Compra.objects.get(id=request.POST['id'])
            items = Item_Compra.objects.filter(compra=compra).prefetch_related('producto', 'producto__marca')
            contenido = {
                'compra': CompraSerializer(compra).data,
                'items':  Item_CompraSerializer(items, many=True).data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif  request.POST['accion'] == 'buscar':
            try:
                if  request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                compras = Compra.objects.filter(estado=estado).filter(
                    Q(factura__icontains=request.POST['buscar']) |
                    Q(proveedor__nombre__icontains=request.POST['buscar'])
                ).prefetch_related('proveedor')
                contenido = {
                    'compras': CompraSerializer(compras, many=True).data,
                    'success': True,
                }
                return  JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al buscar las compras: {}'.format(str(e))
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
        if request.POST['accion'] == 'lista_marcas':
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
        elif request.POST['accion'] == 'buscar_marcas':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                marcas = Marca.objects.filter(estado=estado).filter(
                    Q(nombre__icontains=request.POST['buscar']) |
                    Q(descripcion__icontains=request.POST['buscar'])
                )
                lista_marcas = MarcaSerializer(marcas, many=True)
                contenido   = {
                    'marcas': lista_marcas.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except  Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al buscar las marcas: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'info_marca':
            try:
                marca = Marca.objects.get(id=request.POST['id'])
                lista_marca = MarcaSerializer(marca)
                contenido   = {
                    'marca': lista_marca.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al mostrar la marca: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'crear_marca':
            try:
                marca = Marca()
                marca.nombre = request.POST['nombre']
                marca.descripcion = request.POST['descripcion']
                marca.save()
                contenido = {
                    'success': True,
                    'message': 'La marca fue creada correctamente.',
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear la marca: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'editar_marca':
            try:
                marca = Marca.objects.get(id=request.POST['id'])
                marca.nombre = request.POST['nombre']
                marca.descripcion = request.POST['descripcion']
                marca.save()
                contenido = {
                    'success': True,
                    'message': 'La marca fue editada correctamente.',
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al editar la marca: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'cambiar_estado':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                    operacion = 'habilitada'
                else:
                    estado = False
                    operacion = 'deshabilitada'
                marca = Marca.objects.get(id=request.POST['id'])
                marca.estado = estado
                marca.save()
                contenido   = {
                    'success': True,
                    'message': f'La marca ha sido {operacion} correctamente'
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al cambiar el estado de la marca: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

def crear_venta (request):
    contenido   = {}
    contenido['clientes']    =   Cliente.objects.filter(estado=True)
    return render(request, 'ventas/crear.html', contenido)

def gestion_ventas (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'crear_venta':
            try:
                venta = Venta()
                venta.factura   =   request.POST['factura']
                venta.cliente   =   Cliente.objects.get(identificacion=request.POST['cliente'])
                venta.fecha     =   datetime.now()
                venta.total     =   request.POST['total']
                venta.save()
                for item in json.loads(request.POST['items']):
                    producto    =   Producto.objects.get(id=item['id'])
                    kardex      =   producto.kardex.latest('fecha')
                    Kardex.objects.create(
                        producto    =   producto,
                        transaccion =   'Venta',
                        costo       =   kardex.costo,
                        precio      =   item['precio'],
                        cantidad    =   item['cantidad'],
                        stock       =   int(kardex.stock) - int(item['cantidad'])

                    )
                    Item_Venta.objects.create(
                        venta       =   venta,
                        producto    =   producto,
                        cantidad    =   item['cantidad'],
                        precio      =   item['precio']
                    )
                contenido = {
                    'success': True,
                    'message': 'La venta fue creada correctamente.',
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear la venta: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        if request.POST['accion'] == 'siguiente_factura':
            try:
                factura = Venta.objects.latest('fecha').factura
                next_factura = str(int(factura.lstrip('0')) + 1).zfill(12)
            except Venta.DoesNotExist:
                next_factura = '001001000000001'
            contenido = {
                'factura': next_factura,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

def lista_clientes (request):
    contenido = {}
    return render(request, 'clientes/lista.html', contenido)

def gestion_clientes (request):
    if request.method == 'POST':
        if request.POST['accion'] == 'lista_clientes':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                clientes = Cliente.objects.filter(estado=estado)
                lista_clientes = ClienteSerializer(clientes, many=True)
                contenido   = {
                    'clientes': lista_clientes.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al listar clientes: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'datos_cliente':
            cliente = Cliente.objects.get(identificacion=request.POST['identificacion'])
            cliente_serializer = ClienteSerializer(cliente)
            contenido = {
                'cliente': cliente_serializer.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
        elif request.POST['accion'] == 'info_cliente':
            try:
                cliente = Cliente.objects.get(id=request.POST['id'])
                lista_cliente = ClienteSerializer(cliente)
                contenido   = {
                    'cliente': lista_cliente.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al mostrar el cliente: {}'.format(str(e))
                }
        elif request.POST['accion'] == 'buscar':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                else:
                    estado = False
                clientes = Cliente.objects.filter(estado=estado).filter(
                    Q(nombre__icontains=request.POST['buscar']) |
                    Q(apellido__icontains=request.POST['buscar']) |
                    Q(identificacion__icontains=request.POST['buscar']) |
                    Q(direccion__icontains=request.POST['buscar']) |
                    Q(ciudad__icontains=request.POST['buscar']) |
                    Q(telefono__icontains=request.POST['buscar']) |
                    Q(celular__icontains=request.POST['buscar']) |
                    Q(correo__icontains=request.POST['buscar'])
                )
                lista_clientes = ClienteSerializer(clientes, many=True)
                contenido = {
                    'clientes': lista_clientes.data,
                    'success': True,
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al buscar clientes: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'crear_cliente':
            try:
                cliente = Cliente()
                cliente.nombre              =   request.POST['nombre']
                cliente.apellido            =   request.POST['apellido']
                cliente.tipo_identificacion =   request.POST['tipo_identificacion']
                cliente.identificacion      =   request.POST['identificacion']
                cliente.direccion           =   request.POST['direccion']
                cliente.ciudad              =   request.POST['ciudad']
                cliente.telefono            =   request.POST['telefono']
                cliente.celular             =   request.POST['celular']
                cliente.correo              =   request.POST['correo']
                cliente.save()
                contenido = {
                    'success': True,
                    'message': 'El cliente fue creado correctamente.',
                    'identificacion': ClienteSerializer(cliente).data['identificacion']
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al crear el cliente: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'editar_cliente':
            try:
                cliente = Cliente.objects.get(id=request.POST['id'])
                cliente.nombre              =   request.POST['nombre']
                cliente.apellido            =   request.POST['apellido']
                cliente.tipo_identificacion =   request.POST['tipo_identificacion']
                cliente.identificacion      =   request.POST['identificacion']
                cliente.direccion           =   request.POST['direccion']
                cliente.ciudad              =   request.POST['ciudad']
                cliente.telefono            =   request.POST['telefono']
                cliente.celular             =   request.POST['celular']
                cliente.correo              =   request.POST['correo']
                cliente.save()
                contenido = {
                    'success': True,
                    'message': 'El cliente fue editado correctamente.',
                }
                return JsonResponse(contenido, status=201)
            except Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al editar el cliente: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)
        elif request.POST['accion'] == 'cambiar_estado':
            try:
                if request.POST['estado'].lower() == 'true':
                    estado = True
                    operacion = 'habilitado'
                else:
                    estado = False
                    operacion = 'deshabilitado'
                cliente = Cliente.objects.get(id=request.POST['id'])
                cliente.estado = estado
                cliente.save()
                contenido   = {
                    'success': True,
                    'message': f'El cliente ha sido {operacion} correctamente'
                }
                return JsonResponse(contenido, status=201)
            except  Exception as e:
                response_data = {
                    'success': False,
                    'message': 'Error al cambiar el estado del cliente: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'usuarios/login.html')
    elif request.method == 'POST':
        username  =  request.POST['username']
        password =  request.POST['password']

        usuario = authenticate(username=username, password=password)

        if usuario is None:
            return render(request, 'usuarios/login.html', {'error': 'Usuario o contraseña incorrectos.'})

        login(request, usuario)
        return redirect('index')

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('login')

@login_required
def registrar_usuario(request):
    campos = {
        'usuario': '',
        'nombre': '',
        'apellido': '',
        'email': '',
        'rol': '',
        'password': '',
        'password2': ''
    }
    if request.method == 'GET':
        return render(request, 'usuarios/registrar.html', {
            "roles": Group.objects.all(),
            "campos": campos
         })
    elif request.method == 'POST':
        campos ={
                "usuario" : request.POST['usuario'],
                "nombre" : request.POST['nombre'],
                "apellido" : request.POST['apellido'],
                "email" : request.POST['email'],
                "rol" : request.POST['rol'],
                "password" : request.POST['password'],
                "password2" : request.POST['password2']
        }
        if '' in campos.values():
            return render(request, 'usuarios/registrar.html', {
                "roles": Group.objects.all(),
                "error": "Todos los campos son requeridos.",
                "campos": campos
            })

        if campos['password'] != campos['password2']:
            return render(request, 'usuarios/registrar.html', {
                "roles": Group.objects.all(),
                "error": "Las contraseñas no coinciden.",
                "campos": campos
            })
        else :

            try:
                usuario = User.objects.create_user(username=campos['usuario'], email=campos['email'], password=campos['password'])
                usuario.first_name = campos['nombre']
                usuario.last_name = campos['apellido']

                if campos['rol'] == 'Administrador':
                    usuario.is_superuser = True
                else:
                    grupo = Group.objects.get(name=campos['rol'])
                    grupo.user_set.add(usuario)

                usuario.save()
            except IntegrityError:
                return render(request, 'usuarios/registrar.html', {
                    "roles": Group.objects.all(),
                    "error": "El usuario ya existe.",
                    "campos": campos
                })

            return redirect('lista_usuarios')

@login_required
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})

@login_required
def editar_usuario(request, id):
    if request.method == 'GET':
        usuario = get_object_or_404(User, id=id)
        campos ={
            "usuario" : usuario.username,
            "nombre" : usuario.first_name,
            "apellido" : usuario.last_name,
            "email" : usuario.email,
            "rol" : 'Administrador' if usuario.is_superuser else usuario.groups.first().name,
            'password': '',
            'password2': ''
        }
        return render(request, 'usuarios/editar.html', {
            "campos": campos,
            "roles": Group.objects.all()
        })
    elif request.method == 'POST':
        usuario = get_object_or_404(User, id=id)
        campos ={
            "usuario" : request.POST['usuario'],
            "nombre" : request.POST['nombre'],
            "apellido" : request.POST['apellido'],
            "email" : request.POST['email'],
            "rol" : request.POST['rol'],
            'password': request.POST['password'],
            'password2': request.POST['password2']
        }

        if  campos['usuario'] == '' or campos['email'] == '' or campos['nombre'] == '' or campos['apellido'] == '':
            return render(request, 'usuarios/editar.html', {
                "roles": Group.objects.all(),
                "error": "Los campos usuario, email, nombre y apellido son requeridos.",
                "campos": campos
            })

        if campos['password'] != '' and campos['password2'] != '' and campos['password'] != campos['password2']:
            return render(request, 'usuarios/editar.html', {
                "roles": Group.objects.all(),
                "error": "Las contraseñas no coinciden.",
                "campos": usuario
            })

        try:
            usuario.first_name = campos['nombre']
            usuario.last_name = campos['apellido']
            usuario.email = campos['email']
            usuario.username = campos['usuario']

            if campos['password'] != '':
                usuario.set_password(campos['password'])

            usuario.groups.clear()


            if campos['rol'] == 'Administrador':
                usuario.is_superuser = True
            else:
                usuario.is_superuser = False
                grupo = Group.objects.get(name=campos['rol'])
                grupo.user_set.add(usuario)

            # actualizar el usuario
            usuario.save()
        except IntegrityError:
            return render(request, 'usuarios/editar.html', {
                "roles": Group.objects.all(),
                "error": "Error al editar el usuario.",
                "campos": usuario
            })

        return redirect('lista_usuarios')

@login_required
def deshabilitar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    usuario.is_active = False
    usuario.save()
    return redirect('lista_usuarios')

@login_required
def mostrar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    campos ={
            "usuario" : usuario.username,
            "nombre" : usuario.first_name,
            "apellido" : usuario.last_name,
            "email" : usuario.email,
            "rol" : 'Administrador' if usuario.is_superuser else usuario.groups.first().name,
            'password': '',
            'password2': ''
        }
    return render(request, 'usuarios/detalles.html', {
            "campos": campos,
            "roles": Group.objects.all()
        })
