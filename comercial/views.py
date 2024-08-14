from django.shortcuts import render, get_object_or_404
from .models import Producto, Kardex

# Create your views here.
def vista_productos (request, producto_id):
    producto    = get_object_or_404(Producto, id=producto_id)
    kardex      = producto.kardex.all()
    contenido   = {
        'producto': producto,
        'kardex': kardex,
    }   
    return render(request, 'vista_productos.html', contenido)

def lista_productos (request):
    productos   = Producto.objects.all()
    contenido   = {
        'productos': productos,
    }
    return render(request, 'lista_productos.html', contenido)