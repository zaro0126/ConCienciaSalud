from django import forms
from .models import Producto, MenuDia, Carrusel, InformacionBanner, ReferenciaAdmin


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'descripcion', 'imagen', 'sabores']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'sabores': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class MenuDiaForm(forms.ModelForm):
    class Meta:
        model = MenuDia
        fields = ['nombre', 'precio', 'descripcion', 'imagen', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CarruselForm(forms.ModelForm):
    class Meta:
        model = Carrusel
        fields = ['titulo', 'imagen', 'activo', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class InformacionBannerForm(forms.ModelForm):
    class Meta:
        model = InformacionBanner
        fields = ['titulo', 'imagen', 'enlace', 'activo', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'enlace': forms.URLInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class ReferenciaAdminForm(forms.ModelForm):
    class Meta:
        model = ReferenciaAdmin
        fields = ['titulo', 'archivo', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }