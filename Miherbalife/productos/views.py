from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import Categoria, Producto, MenuDia, Carrusel, InformacionBanner,ReferenciaAdmin,Pedido
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProductoForm, MenuDiaForm, CarruselForm, InformacionBannerForm,ReferenciaAdminForm
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
import urllib.parse


    


def index(request, categoria_slug=None):
    # Capturar lo que el usuario escribió en el buscador y quitarle espacios sobrantes
    query = request.GET.get('q', '').strip()
    
    # Obtener todas las categorías para llenar el menú desplegable dinámicamente
    categorias = Categoria.objects.all()
    categoria_actual = None
    
    # Empezamos con todos los productos
    productos = Producto.objects.all()

    # Si el usuario seleccionó una categoría, filtramos por ella primero
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    # Si el usuario escribió algo en el buscador, filtramos sobre el resultado actual
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Nombramos las consultas activas para el Carrusel y Banners
    carrusel_imagenes = Carrusel.objects.filter(activo=True)
    banners_informativos = InformacionBanner.objects.filter(activo=True)

    # Renderiza la plantilla principal 'index.html'
    return render(request, 'index.html', {
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'productos': productos,
        'carrusel_imagenes': carrusel_imagenes,
        'banners_informativos': banners_informativos,
    })


def agregar_al_carrito(request, producto_id, tipo='producto'):
    carrito = request.session.get('carrito', {})
    sabor_elegido = request.POST.get('sabor', '')

    # Clave única para diferenciar productos con distintos sabores
    if sabor_elegido:
        clave = f"{tipo}_{producto_id}_{sabor_elegido}"
    else:
        clave = f"{tipo}_{producto_id}"

    if clave in carrito:
        carrito[clave]['cantidad'] += 1
    else:
        if tipo == 'producto':
            item = get_object_or_404(Producto, id=producto_id)
            nombre = f"{item.nombre} ({sabor_elegido})" if sabor_elegido else item.nombre
            precio = float(item.precio)
            imagen = item.imagen.url if item.imagen else ''
        else:
            item = get_object_or_404(MenuDia, id=producto_id)
            nombre = item.nombre
            precio = float(item.precio)
            imagen = item.imagen.url if item.imagen else ''

        carrito[clave] = {
            'nombre': nombre,
            'precio': precio,
            'cantidad': 1,
            'imagen': imagen,
            'sabor': sabor_elegido,
            'tipo': tipo,
            'id': producto_id
        }

    request.session['carrito'] = carrito
    request.session.modified = True  # Asegura que Django guarde los cambios en la sesión

    # 1. Calculamos el total de artículos actuales en el carrito
    total_items = sum(item['cantidad'] for item in carrito.values())

    # 2. Si la petición viene por AJAX (desde el botón flotante/tarjeta), respondemos con JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cantidad_total': total_items})

    # 3. Si por alguna razón entra una petición normal, redirige a donde estaba
    return redirect(request.META.get('HTTP_REFERER', 'catalogo'))


def eliminar_del_carrito(request, clave):
    carrito = request.session.get('carrito', {})
    if clave in carrito:
        del carrito[clave]
        request.session['carrito'] = carrito
    return redirect('ver_carrito')


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total_general = 0
    
    for clave, item in carrito.items():
        item['subtotal'] = float(item['precio']) * int(item['cantidad'])
        total_general += item['subtotal']
    
    return render(request, 'carrito.html', {
        'carrito': carrito,
        'total_general': total_general
    })
    

def sumar_al_carrito(request, clave):
    carrito = request.session.get('carrito', {})
    if clave in carrito:
        carrito[clave]['cantidad'] += 1
        request.session['carrito'] = carrito
    return redirect('ver_carrito')


def restar_del_carrito(request, clave):
    carrito = request.session.get('carrito', {})
    if clave in carrito:
        carrito[clave]['cantidad'] -= 1
        # Si la cantidad llega a 0 o menos, se remueve del carrito
        if carrito[clave]['cantidad'] <= 0:
            del carrito[clave]
        request.session['carrito'] = carrito
    return redirect('ver_carrito')

def vaciar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    # Redirige de vuelta al carrito (que ahora estará vacío) o al catálogo
    return redirect('ver_carrito')


def negocio(request):
    return render(request, 'negocio.html')

def menuDia(request): 
     # Consultamos solo los elementos del menú del día marcados como disponibles
   menu_local = MenuDia.objects.filter(disponible=True)
   categorias = Categoria.objects.all() 
    
   return render(request, 'menu-dia.html', {
        'menu_local': menu_local,
        'categorias': categorias,     
    })


def es_administrador(user):
    return user.is_staff # O una validación personalizada

@login_required(login_url='/admin/login/') # O tu propia vista de login
@user_passes_test(es_administrador)
def panel_productos(request):
    # Tu lógica aquí
    pass

@login_required
def gestionar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'gestion/productos.html', {'productos': productos})

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestionar_productos')
    else:
        form = ProductoForm()
    return render(request, 'gestion/producto_form.html', {'form': form})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('gestionar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'gestion/producto_form.html', {'form': form, 'editando': True})

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('gestionar_productos')
    return render(request, 'gestion/producto_confirm_delete.html', {'producto': producto})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    


# ------------------------------------------------------ MENÚ DEL DÍA --------------------------------------------------------------------------
@login_required
def gestionar_menu(request):
    elementos = MenuDia.objects.all()
    return render(request, 'gestion/menu_lista.html', {'elementos': elementos})

@login_required
def agregar_menu(request):
    form = MenuDiaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('gestionar_menu')
    return render(request, 'gestion/producto_form.html', {'form': form})

@login_required
def editar_menu(request, pk):
    item = get_object_or_404(MenuDia, pk=pk)
    form = MenuDiaForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('gestionar_menu')
    return render(request, 'gestion/producto_form.html', {'form': form, 'editando': True})

@login_required
def eliminar_menu(request, pk):
    item = get_object_or_404(MenuDia, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_menu')
    return render(request, 'gestion/producto_confirm_delete.html', {'producto': item})


# ---------------------------------------------------------------- CARRUSEL --------------------------------------------------------------------
@login_required
def gestionar_carrusel(request):
    elementos = Carrusel.objects.all()
    return render(request, 'gestion/carrusel_lista.html', {'elementos': elementos})

@login_required
def agregar_carrusel(request):
    form = CarruselForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('gestionar_carrusel')
    return render(request, 'gestion/producto_form.html', {'form': form})

@login_required
def editar_carrusel(request, pk):
    item = get_object_or_404(Carrusel, pk=pk)
    form = CarruselForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('gestionar_carrusel')
    return render(request, 'gestion/producto_form.html', {'form': form, 'editando': True})

@login_required
def eliminar_carrusel(request, pk):
    item = get_object_or_404(Carrusel, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_carrusel')
    return render(request, 'gestion/producto_confirm_delete.html', {'producto': item})


# ---------------------------------------------------------- BANNERS INFORMATIVOS ------------------------------------------------------------
@login_required
def gestionar_banners(request):
    elementos = InformacionBanner.objects.all()
    return render(request, 'gestion/banners_lista.html', {'elementos': elementos})

@login_required
def agregar_banner(request):
    form = InformacionBannerForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('gestionar_banners')
    return render(request, 'gestion/producto_form.html', {'form': form})

@login_required
def editar_banner(request, pk):
    item = get_object_or_404(InformacionBanner, pk=pk)
    form = InformacionBannerForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('gestionar_banners')
    return render(request, 'gestion/producto_form.html', {'form': form, 'editando': True})

@login_required
def eliminar_banner(request, pk):
    item = get_object_or_404(InformacionBanner, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_banners')
    return render(request, 'gestion/producto_confirm_delete.html', {'producto': item})

@login_required
def dashboard_admin(request):
    total_productos = Producto.objects.count()
    total_menu = MenuDia.objects.count()
    total_carrusel = Carrusel.objects.count()
    total_banners = InformacionBanner.objects.count()

    context = {
        'total_productos': total_productos,
        'total_menu': total_menu,
        'total_carrusel': total_carrusel,
        'total_banners': total_banners,
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def gestionar_referencias(request):
    elementos = ReferenciaAdmin.objects.all()
    return render(request, 'gestion/referencias_lista.html', {'elementos': elementos})

@login_required
def agregar_referencia(request):
    form = ReferenciaAdminForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('gestionar_referencias')
    return render(request, 'gestion/producto_form.html', {'form': form, 'editando': False})

@login_required
def eliminar_referencia(request, pk):
    item = get_object_or_404(ReferenciaAdmin, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_referencias')
    return render(request, 'gestion/eliminar_confirmar.html', {'item': item, 'url_volver': 'gestionar_referencias'})

@login_required
def editar_referencia(request, pk):
    item = get_object_or_404(ReferenciaAdmin, pk=pk)
    form = ReferenciaAdminForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('gestionar_referencias')
    
    context = {
        'form': form, 
        'editando': True,
        'url_volver': 'gestionar_referencias'
    }
    return render(request, 'gestion/producto_form.html', context)


def cliente_preferente(request):
    return render(request, 'clientepreferente.html')

def es_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_admin)
def marcar_pedido_leido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    pedido.leido = True
    pedido.save()
    return redirect('dashboard_pedidos')

@user_passes_test(lambda u: u.is_staff)
def dashboard_pedidos(request):
    # Traemos todos los pedidos ordenados del más reciente al más antiguo
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    
    # Contamos cuántos están sin leer
    pedidos_nuevos_count = Pedido.objects.filter(leido=False).count()
    
    return render(request, 'gestion/dashboard_pedidos.html', {
        'pedidos': pedidos,
        'pedidos_nuevos_count': pedidos_nuevos_count,
    })


def procesar_pedido(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        tipo_pedido = request.POST.get('tipo', 'catalogo')
        
        # 1. Validamos que existan datos y el carrito no esté vacío
        carrito = request.session.get('carrito', {})
        if not carrito:
            return redirect('ver_carrito')

        # 2. Guardamos el pedido formalmente en la base de datos
        nuevo_pedido = Pedido.objects.create(
            tipo=tipo_pedido,
            nombre_cliente=nombre,
            telefono_cliente=telefono,
            leido=False
        )
        
        # 3. Armamos el mensaje de WhatsApp detallado con los productos del carrito
        mensaje = f"Hola, soy {nombre}. Deseo confirmar mi pedido #{nuevo_pedido.id}:\n\n"
        total = 0
        for clave, item in carrito.items():
            subtotal = float(item['precio']) * int(item['cantidad'])
            total += subtotal
            sabor_txt = f" ({item['sabor']})" if item.get('sabor') else ""
            mensaje += f"- {item['cantidad']}x {item['nombre']}{sabor_txt} (${subtotal})\n"
        
        mensaje += f"\n*Total a pagar: ${total} MXN*"

        # 4. Vaciamos el carrito de la sesión para que quede limpio
        if 'carrito' in request.session:
            del request.session['carrito']
            request.session.modified = True

        # 5. Generamos la URL de WhatsApp y redirigimos al usuario
        telefono_destino = "526647670709" # Tu número
        url_whatsapp = f"https://api.whatsapp.com/send?phone={telefono_destino}&text={urllib.parse.quote(mensaje)}"
        
        return redirect(url_whatsapp)
        
    return redirect('ver_carrito')

@user_passes_test(lambda u: u.is_staff)
def marcar_pedido_leido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.leido = True
    pedido.save()
    return redirect('dashboard_pedidos')

@user_passes_test(lambda u: u.is_staff)
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect('dashboard_pedidos')

@user_passes_test(es_admin)
def dashboard_admin(request):
    # 1. Calculamos los pedidos nuevos (pendientes)
    pedidos_nuevos_count = Pedido.objects.filter(leido=False).count()
    
    context = {
        'pedidos_nuevos_count': pedidos_nuevos_count,  # Alimenta la tarjeta en el menú principal
        'total_productos': Producto.objects.count(),
        'total_menu': MenuDia.objects.count(),
        'total_carrusel': Carrusel.objects.count(),
        'total_banners': InformacionBanner.objects.count(),
    }
    
    # Asegúrate de que este nombre coincida exactamente con tu archivo HTML en templates/gestion/
    return render(request, 'gestion/dashboard.html', context)