"""
URL configuration for comercial_alpha2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from comercial.views import index, info_producto, lista_productos, gestion_productos, crear_compra, gestion_compras, lista_proveedores, gestion_proveedores, lista_marcas, gestion_marcas, crear_venta, gestion_ventas, lista_clientes, gestion_clientes, lista_compras

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path('productos/info/<int:producto_id>', info_producto, name="info_producto"),
    path('productos/lista/', lista_productos, name="lista_productos"),
    path('productos/gestion/', gestion_productos, name="gestion_productos"),
    path('compras/crear/', crear_compra, name="crear_compra"),
    path('compras/lista', lista_compras, name="lista_compras"),
    path('gestion_compras/', gestion_compras, name="gestion_compras"),
    path('proveedores/lista', lista_proveedores, name="lista_proveedores"),
    path('proveedores/gestion', gestion_proveedores, name="gestion_proveedores"),
    path('marcas/lista', lista_marcas, name="lista_marcas"),
    path('marcas/gestion', gestion_marcas, name="gestion_marcas"),
    path('ventas/crear', crear_venta, name="crear_venta"),
    path('gestion_ventas', gestion_ventas, name="gestion_ventas"),
    path('clientes/lista', lista_clientes, name="lista_clientes"),
    path('clientes/gestion', gestion_clientes, name="gestion_clientes"),
]
