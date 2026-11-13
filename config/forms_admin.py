from django import forms
 
from .models import Categoria, Producto
 
 
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        labels = {'nombre': 'Nombre de la categoría'}
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre
 
 
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'imagen', 'stock', 'activo']
        labels = {
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'imagen': 'Imagen',
            'activo': 'Visible en la tienda',
        }
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre
 
    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio