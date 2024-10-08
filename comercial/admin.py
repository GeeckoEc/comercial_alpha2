# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Proveedor, Compra, Marca, Producto, Item_Compra, Kardex, Cliente, Venta, Item_Venta  


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado',
        'nombre',
        'identificacion',
        'descripcion',
        'direccion',
        'ciudad',
        'telefono',
        'celular',
        'correo',
    )
    list_filter = ('estado',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'proveedor',
        'estado',
        'factura',
        'fecha',
        'subtotal',
        'iva',
        'total',
    )
    list_filter = ('proveedor', 'estado', 'fecha')


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'nombre', 'descripcion')
    list_filter = ('estado',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado',
        'codigo',
        'marca',
        'nombre',
        'presentacion',
        'descripcion',
        'precio',
    )
    list_filter = ('estado', 'marca')


@admin.register(Item_Compra)
class Item_CompraAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'compra',
        'producto',
        'estado',
        'cantidad',
        'costo',
    )
    list_filter = ('compra', 'producto', 'estado')


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'producto',
        'transaccion',
        'fecha',
        'cantidad',
        'costo',
        'precio',
        'stock',
    )
    list_filter = ('producto', 'fecha')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado',
        'nombre',
        'apellido',
        'tipo_identificacion',
        'identificacion',
        'direccion',
        'ciudad',
        'telefono',
        'celular',
        'correo',
    )
    list_filter = ('estado',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado',
        'cliente',
        'fecha',
        'factura',
        'subtotal',
        'iva',
        'total',
    )
    list_filter = ('estado', 'cliente', 'fecha')


@admin.register(Item_Venta)
class Item_VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'estado',
        'venta',
        'producto',
        'cantidad',
        'precio',
    )
    list_filter = ('estado', 'venta', 'producto')