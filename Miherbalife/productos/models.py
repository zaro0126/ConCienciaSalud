import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from django.shortcuts import redirect
import urllib.parse

class MenuDia(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la preparación")
    descripcion = models.TextField(verbose_name="Descripción o ingredientes")
    precio = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio ($)")
    imagen = models.ImageField(upload_to='menu_dia/', verbose_name="Fotografía del plato/bebida")
    disponible = models.BooleanField(default=True, verbose_name="¿Disponible hoy?")
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Menú del Día"
        verbose_name_plural = "Menú del Día"
        ordering = ['-creado_el']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Texto corto para la URL (ej: polvos-y-batidos)")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sabor(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Sabor")
    disponible = models.BooleanField(default=True, verbose_name="¿Disponible?")

    class Meta:
        verbose_name = "Sabor"
        verbose_name_plural = "Sabores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    imagen = models.ImageField(upload_to='productos/')
    
    # Campo de Sabores integrado en la clase única de Producto
    sabores = models.ManyToManyField(Sabor, blank=True, verbose_name="Sabores disponibles")

    def save(self, *args, **kwargs):
        # Conversión automática a WEBP
        if self.imagen and hasattr(self.imagen, 'file'):
            try:
                img = Image.open(self.imagen)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                buffer.seek(0)

                nombre_base = os.path.splitext(self.imagen.name)[0]
                nuevo_nombre = f"{nombre_base}.webp"

                self.imagen.save(nuevo_nombre, ContentFile(buffer.read()), save=False)
            except Exception:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class InformacionBanner(models.Model):
    titulo = models.CharField(max_length=150, blank=True, null=True) # Opcional
    imagen = models.ImageField(upload_to='banners_informativos/')
    enlace = models.URLField(blank=True, null=True) # Por si quieres que la imagen sea un botón o link
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0) # Para ordenar cuáles van primero

    def save(self, *args, **kwargs):
        # Conversión automática a WEBP también para los banners
        if self.imagen and hasattr(self.imagen, 'file'):
            try:
                img = Image.open(self.imagen)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                buffer.seek(0)

                nombre_base = os.path.splitext(self.imagen.name)[0]
                nuevo_nombre = f"{nombre_base}.webp"

                self.imagen.save(nuevo_nombre, ContentFile(buffer.read()), save=False)
            except Exception:
                pass

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Banner Informativo"
        verbose_name_plural = "Banners Informativos"
        ordering = ['orden']

    def __str__(self):
        return self.titulo or f"Banner informativo #{self.id}"

class Carrusel(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Título o Descripción")
    imagen = models.ImageField(upload_to='carrusel/', verbose_name="Imagen del Carrusel")
    activo = models.BooleanField(default=True, verbose_name="¿Mostrar en la página?")
    orden = models.IntegerField(default=0, verbose_name="Orden de aparición")

    def save(self, *args, **kwargs):
        if self.imagen and hasattr(self.imagen, 'file'):
            try:
                img = Image.open(self.imagen)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                buffer.seek(0)
                nombre_base = os.path.splitext(self.imagen.name)[0]
                nuevo_nombre = f"{nombre_base}.webp"
                self.imagen.save(nuevo_nombre, ContentFile(buffer.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Imagen de Carrusel"
        verbose_name_plural = "Imágenes de Carrusel"
        ordering = ['orden']

    def __str__(self):
        return self.titulo or f"Carrusel #{self.id}"

class ReferenciaAdmin(models.Model):
    titulo = models.CharField(max_length=150, verbose_name="Título o Nombre del Documento")
    archivo = models.FileField(upload_to='referencias_admin/', verbose_name="Archivo o Imagen de Referencia")
    subido_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    orden = models.IntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Referencia de Administración"
        verbose_name_plural = "Referencias de Administración"
        ordering = ['orden']

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    TIPO_PEDIDO_CHOICES = [
        ('catalogo', 'Catálogo Cerrado'),
        ('menu_dia', 'Menú del Día'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_PEDIDO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Datos del cliente que pide
    nombre_cliente = models.CharField(max_length=100)
    telefono_cliente = models.CharField(max_length=20)
    
    # Control de fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Para saber si el admin ya lo vio (clave para la notificación)
    leido = models.BooleanField(default=False)

    def __str__(self):
        # Corregido: unimos la cadena en una sola línea o usando paréntesis
        return f"Pedido #{self.id} - {self.get_tipo_display()} ({self.nombre_cliente})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=150) # Nombre del producto o platillo del menú
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto} (Pedido #{self.pedido.id})"


def crear_pedido_y_enviar_whatsapp(request):
    if request.method == 'POST':
        # 1. Capturas los datos del cliente desde el formulario
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        tipo_pedido = request.POST.get('tipo') # 'catalogo' o 'menu_dia'
        
        # 2. GUARDAS EL PEDIDO EN LA BASE DE DATOS
        nuevo_pedido = Pedido.objects.create(
            tipo=tipo_pedido,
            nombre_cliente=nombre,
            telefono_cliente=telefono,
            leido=False # Aparecerá como pendiente en tu dashboard
        )
        
        # Opcional: Si manejas carrito, aquí guardas también los productos en DetallePedido
        # DetallePedido.objects.create(pedido=nuevo_pedido, nombre_producto="...", cantidad=1, precio_unitario=...)

        # 3. Armas el mensaje y el enlace para WhatsApp
        mensaje = f"Hola, soy {nombre}. Deseo realizar un pedido #{nuevo_pedido.id}."
        
        url_whatsapp = f"https://wa.me/526647670709?text={urllib.parse.quote(mensaje)}"
        
        # 4. Rediriges al usuario a WhatsApp
        return redirect(url_whatsapp)
