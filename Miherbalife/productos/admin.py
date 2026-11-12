from django.contrib import admin
from .models import Producto
from .models import Producto, Categoria
from .models import Producto, Categoria, MenuDia, Sabor, InformacionBanner, Carrusel

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria')
    filter_horizontal = ('sabores',)
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')
    
@admin.register(MenuDia)
class MenuDiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'disponible', 'creado_el')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'disponible')
    
@admin.register(Sabor)
class SaborAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'disponible')
    list_editable = ('disponible',)

@admin.register(InformacionBanner)
class InformacionBannerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'orden')

    
@admin.register(Carrusel)
class CarruselAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'orden')
    list_editable = ('activo', 'orden')

