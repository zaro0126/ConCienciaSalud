from django.shortcuts import render, get_object_or_404
from productos.models import Producto, Categoria



def index(request, categoria_slug=None):
    # 1. Obtenemos todas las categorías de la base de datos para el menú desplegable
    categorias = Categoria.objects.all()
    
    # 2. Empezamos trayendo todos los productos
    productos = Producto.objects.all()
    categoria_actual = None

    # 3. Si el usuario hizo clic en una categoría del menú, filtramos
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    # 4. Empaquetamos TODO y se lo enviamos a tu index.html global
    return render(request, 'index.html', {
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'productos': productos,
    })

