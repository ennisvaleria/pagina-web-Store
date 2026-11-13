from django import forms


class PerfilForm(forms.Form):
    """Datos que el cliente puede editar en 'Mi perfil'."""
    nombre = forms.CharField(min_length=3, max_length=50, label='Nombre')
    apellido = forms.CharField(min_length=3, max_length=50, label='Apellido')
    direccion = forms.CharField(min_length=3, max_length=100, label='Dirección')
    correo = forms.EmailField(max_length=50, label='Correo')


class CambiarPasswordForm(forms.Form):
    actual = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput)
    nueva = forms.CharField(min_length=6, label='Nueva contraseña', widget=forms.PasswordInput)
    repetir = forms.CharField(label='Repite la nueva contraseña', widget=forms.PasswordInput)

    def clean(self):
        datos = super().clean()
        if datos.get('nueva') and datos.get('repetir') and datos['nueva'] != datos['repetir']:
            self.add_error('repetir', 'Las contraseñas no coinciden.')
        return datos


class EliminarCuentaForm(forms.Form):
    password = forms.CharField(label='Tu contraseña', widget=forms.PasswordInput)
