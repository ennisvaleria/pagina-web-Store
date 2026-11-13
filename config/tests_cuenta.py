from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse

from .models import Cliente

DATOS = {
    'nombre': 'Juan', 'apellido': 'Perez', 'direccion': 'Calle 1 #23',
    'correo': 'juan@correo.cl', 'password': 'clave123',
}


def crear_cliente(rol='cliente', correo='juan@correo.cl', password='clave123'):
    return Cliente.objects.create(
        nombre='Juan', apellido='Perez', direccion='Calle 1 #23',
        correo=correo, password=make_password(password), rol=rol,
    )


class RegistroTests(TestCase):
    def test_registro_guarda_cliente_con_hash_y_rol_cliente(self):
        r = self.client.post(reverse('registro'), DATOS)
        self.assertRedirects(r, reverse('login'))
        c = Cliente.objects.get(correo='juan@correo.cl')
        self.assertEqual(c.rol, 'cliente')
        self.assertNotEqual(c.password, 'clave123')
        self.assertTrue(check_password('clave123', c.password))

    def test_no_se_puede_elegir_rol_admin_desde_el_formulario(self):
        self.client.post(reverse('registro'), {**DATOS, 'rol': 'admin'})
        self.assertEqual(Cliente.objects.get().rol, 'cliente')

    def test_correo_duplicado_muestra_error(self):
        crear_cliente()
        r = self.client.post(reverse('registro'), {**DATOS, 'correo': 'JUAN@correo.cl'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'ya está registrado')
        self.assertEqual(Cliente.objects.count(), 1)

    def test_campos_vacios_muestran_errores_por_campo(self):
        r = self.client.post(reverse('registro'), {})
        self.assertContains(r, 'error-campo', count=5)
        self.assertEqual(Cliente.objects.count(), 0)


class LoginTests(TestCase):
    def test_login_cliente_va_a_principal_y_guarda_sesion(self):
        crear_cliente()
        r = self.client.post(reverse('login'), {'correo': 'juan@correo.cl', 'password': 'clave123'})
        self.assertRedirects(r, reverse('inicio'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['usuario'], 'juan@correo.cl')
        self.assertEqual(self.client.session['rol'], 'cliente')

    def test_login_admin_va_al_panel(self):
        crear_cliente(rol='admin', correo='admin@tienda.cl', password='admin123')
        r = self.client.post(reverse('login'), {'correo': 'admin@tienda.cl', 'password': 'admin123'})
        self.assertRedirects(r, reverse('panel'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['rol'], 'admin')

    def test_login_incorrecto_muestra_mensaje(self):
        crear_cliente()
        for datos in ({'correo': 'juan@correo.cl', 'password': 'equivocada'},
                      {'correo': 'nadie@correo.cl', 'password': 'clave123'}):
            r = self.client.post(reverse('login'), datos)
            self.assertContains(r, 'Correo o contraseña incorrectos.')
            self.assertNotIn('usuario', self.client.session)

    def test_logout_limpia_la_sesion(self):
        crear_cliente()
        self.client.post(reverse('login'), {'correo': 'juan@correo.cl', 'password': 'clave123'})
        self.client.get(reverse('logout'))
        self.assertNotIn('usuario', self.client.session)


class PanelYApiTests(TestCase):
    def test_panel_bloqueado_sin_sesion_y_para_clientes(self):
        self.assertRedirects(self.client.get(reverse('panel_productos')), reverse('login'),
                             fetch_redirect_response=False)
        crear_cliente()
        self.client.post(reverse('login'), {'correo': 'juan@correo.cl', 'password': 'clave123'})
        self.assertRedirects(self.client.get(reverse('panel_productos')), reverse('login'),
                             fetch_redirect_response=False)

    def test_panel_accesible_para_admin(self):
        crear_cliente(rol='admin', correo='admin@tienda.cl', password='admin123')
        self.client.post(reverse('login'), {'correo': 'admin@tienda.cl', 'password': 'admin123'})
        self.assertEqual(self.client.get(reverse('panel_productos')).status_code, 200)

    def test_api_usuario(self):
        self.assertEqual(self.client.get(reverse('api_usuario')).json(), {'autenticado': False})
        crear_cliente()
        self.client.post(reverse('login'), {'correo': 'juan@correo.cl', 'password': 'clave123'})
        j = self.client.get(reverse('api_usuario')).json()
        self.assertTrue(j['autenticado'])
        self.assertEqual((j['nombre'], j['correo'], j['rol']), ('Juan', 'juan@correo.cl', 'cliente'))
        self.assertNotIn('password', j)

    def test_principal_muestra_nombre_y_link_a_perfil(self):
        crear_cliente()
        self.client.post(reverse('login'), {'correo': 'juan@correo.cl', 'password': 'clave123'})
        r = self.client.get(reverse('inicio'))
        self.assertContains(r, 'Juan Perez')
        self.assertContains(r, reverse('perfil'))


class PerfilTests(TestCase):
    def entrar(self, **kw):
        c = crear_cliente(**kw)
        self.client.post(reverse('login'), {'correo': c.correo, 'password': 'clave123'})
        return c

    def test_perfil_exige_login(self):
        r = self.client.get(reverse('perfil'))
        self.assertRedirects(r, reverse('login'), fetch_redirect_response=False)

    def test_ver_perfil(self):
        self.entrar()
        r = self.client.get(reverse('perfil'))
        self.assertContains(r, 'Calle 1 #23')

    def test_editar_datos(self):
        c = self.entrar()
        r = self.client.post(reverse('perfil'), {
            'accion': 'datos', 'nombre': 'Pedro', 'apellido': 'Soto',
            'direccion': 'Otra calle 5', 'correo': 'nuevo@correo.cl'})
        self.assertRedirects(r, reverse('perfil'))
        c.refresh_from_db()
        self.assertEqual((c.nombre, c.correo), ('Pedro', 'nuevo@correo.cl'))
        self.assertEqual(self.client.get(reverse('api_usuario')).json()['correo'], 'nuevo@correo.cl')

    def test_editar_con_correo_de_otro_cliente_falla(self):
        crear_cliente(correo='otro@correo.cl')
        c = self.entrar()
        r = self.client.post(reverse('perfil'), {
            'accion': 'datos', 'nombre': 'Juan', 'apellido': 'Perez',
            'direccion': 'Calle 1 #23', 'correo': 'otro@correo.cl'})
        self.assertContains(r, 'ya está en uso')
        c.refresh_from_db()
        self.assertEqual(c.correo, 'juan@correo.cl')

    def test_cambiar_password(self):
        c = self.entrar()
        r = self.client.post(reverse('perfil'), {
            'accion': 'password', 'actual': 'clave123', 'nueva': 'nueva456', 'repetir': 'nueva456'})
        self.assertRedirects(r, reverse('perfil'))
        c.refresh_from_db()
        self.assertTrue(check_password('nueva456', c.password))

    def test_cambiar_password_con_actual_incorrecta(self):
        c = self.entrar()
        r = self.client.post(reverse('perfil'), {
            'accion': 'password', 'actual': 'mala', 'nueva': 'nueva456', 'repetir': 'nueva456'})
        self.assertContains(r, 'actual no es correcta')
        c.refresh_from_db()
        self.assertTrue(check_password('clave123', c.password))

    def test_eliminar_cuenta_requiere_post_y_password(self):
        c = self.entrar()
        # GET no elimina nada
        self.client.get(reverse('perfil'))
        self.assertTrue(Cliente.objects.filter(pk=c.pk).exists())
        # contraseña incorrecta
        r = self.client.post(reverse('perfil'), {'accion': 'eliminar', 'password': 'mala'})
        self.assertContains(r, 'no es correcta')
        self.assertTrue(Cliente.objects.filter(pk=c.pk).exists())
        # contraseña correcta
        r = self.client.post(reverse('perfil'), {'accion': 'eliminar', 'password': 'clave123'})
        self.assertRedirects(r, reverse('login'), fetch_redirect_response=False)
        self.assertFalse(Cliente.objects.filter(pk=c.pk).exists())
        self.assertNotIn('usuario', self.client.session)

    def test_admin_no_puede_eliminar_su_cuenta(self):
        c = self.entrar(rol='admin', correo='admin@tienda.cl')
        r = self.client.post(reverse('perfil'), {'accion': 'eliminar', 'password': 'clave123'})
        self.assertContains(r, 'no puede eliminar')
        self.assertTrue(Cliente.objects.filter(pk=c.pk).exists())

    def test_sesion_de_cuenta_eliminada_ya_no_entra(self):
        c = self.entrar()
        c.delete()
        r = self.client.get(reverse('perfil'))
        self.assertRedirects(r, reverse('login'), fetch_redirect_response=False)
