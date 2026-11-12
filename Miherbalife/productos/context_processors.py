from .models import Categoria, Producto

def menu_global(request):
    return {
        'categorias': Categoria.objects.all(),
        'productos_menu': Producto.objects.all()
    }

def cantidad_carrito_context(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return {'cantidad_carrito': total_items}
