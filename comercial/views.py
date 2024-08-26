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

from .models import Producto, Kardex, Marca, Compra, Item_Compra, Proveedor, Cliente, Venta, Item_Venta

# Create your views here.


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

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
    class Meta:
        model = Compra
        fields = '__all__'

class Item_CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item_Compra
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
                compras = Compra.objects.filter(estado=estado)
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
            """ try: """
            compra = Compra()
            compra.factura      =   request.POST['factura']
            compra.proveedor    =   Proveedor.objects.get(id=request.POST['proveedor'])
            compra.fecha        =   datetime.now()
            compra.total        =   request.POST['total']
            compra.save()
            items = json.loads(request.POST['items'])
            for item in items:
                item_compra             =   Item_Compra()
                item_compra.compra      =   compra
                item_compra.producto    =   Producto.objects.get(id=item['id'])
                item_compra.cantidad    =   item['cantidad']
                item_compra.costo      =   item['costo']
                item_compra.save()
            
            return JsonResponse({'success': True, 'message': 'La compra fue creada correctamente.'}, status=201)
            """ except Exception as e:
                response_data   =   {
                    'success': False,
                    'message': 'Error al crear la compra: {}'.format(str(e))
                }
                return JsonResponse(response_data, status=500) """
        elif request.POST['accion'] == 'info_compra':
            compra = Compra.objects.get(id=request.POST['id'])
            compra_serializer = CompraSerializer(compra)
            items = Item_Compra.objects.filter(compra=compra)
            items_serializer = Item_CompraSerializer(items, many=True)
            contenido = {
                'compra': compra_serializer.data,
                'items':  items_serializer.data,
                'success': True,
            }
            return JsonResponse(contenido, status=201)
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
        if request.POST['accion'] == 'crear_compra': 
            venta = Venta()
            venta.factura   =   request.POST['factura']
            venta.cliente   =   request.POST['cliente']
            venta.fecha     =   datetime.now()
            venta.total     =   request.POST['total']
            venta.save()
            for item in json.loads(request.POST['productos']):
                item_venta             =   Item_Venta()
                item_venta.venta        =   venta
                item_venta.producto     =   Producto.objects.get(id=item['id'])
                item_venta.cantidad     =   item['cantidad']
                item_venta.precio       =   item['precio']
                item_venta.save()
            contenido = {
                'success': True,
                'message': 'La venta fue creada correctamente.',
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