#from django.contrib import admin

# Register your models here.
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Proveedor, Adquiscion, Producto, Item_Adquiscion, Kardex, Cliente, Venta, Item_Venta


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'identificacion',
        'descripcion',
        'direccion',
        'ciudad',
        'telefono',
        'celular',
        'correo',
    )


@admin.register(Adquiscion)
class AdquiscionAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'factura', 'fecha', 'total')
    list_filter = ('proveedor', 'fecha')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'precio', 'cantidad')


@admin.register(Item_Adquiscion)
class Item_AdquiscionAdmin(admin.ModelAdmin):
    list_display = ('id', 'adquiscion', 'producto', 'cantidad', 'precio')
    list_filter = ('adquiscion', 'producto')


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'fecha', 'cantidad', 'precio')
    list_filter = ('producto', 'fecha')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'factura', 'total')
    list_filter = ('cliente', 'fecha')


@admin.register(Item_Venta)
class Item_VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio')
    list_filter = ('venta', 'producto')