import json
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth.hashers import check_password, make_password
from django.core.management import call_command, CommandError
from django.db.models.signals import post_migrate
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Categoria, Cliente, DetallePedido, Pedido, Producto


class PedidoFlowTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Ana",
            apellido="Pérez",
            direccion="Calle 123",
            correo="ana@example.com",
            password="hash",
        )
        categoria = Categoria.objects.create(nombre="Periféricos")
        self.producto = Producto.objects.create(
            categoria=categoria,
            nombre="Mouse",
            descripcion="Mouse gamer",
            precio=10000,
            imagen="productos/mouse.jpg",
            stock=5,
        )
        session = self.client.session
        session["usuario"] = self.cliente.correo
        session.save()

    def test_checkout_creates_order_and_decreases_stock(self):
        respuesta = self.client.post(
            reverse("checkout"),
            data=json.dumps({
                "items": [
                    {"id": self.producto.pk, "cantidad": 1},
                    {"id": self.producto.pk, "cantidad": 2},
                ],
            }),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 201)
        pedido = Pedido.objects.get()
        detalle = DetallePedido.objects.get(pedido=pedido)
        self.producto.refresh_from_db()
        self.assertEqual(pedido.cliente, self.cliente)
        self.assertEqual(pedido.total, 30000)
        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.precio_unitario, 10000)
        self.assertEqual(self.producto.stock, 2)

    def test_checkout_rejects_insufficient_stock_without_partial_order(self):
        respuesta = self.client.post(
            reverse("checkout"),
            data=json.dumps({"items": [{"id": self.producto.pk, "cantidad": 6}]}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(Pedido.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)

    def test_customer_sees_only_their_own_orders(self):
        otro_cliente = Cliente.objects.create(
            nombre="Luis",
            apellido="Díaz",
            direccion="Avenida 456",
            correo="luis@example.com",
            password="hash",
        )
        pedido_propio = Pedido.objects.create(cliente=self.cliente, total=10000)
        Pedido.objects.create(cliente=otro_cliente, total=10000)

        respuesta = self.client.get(reverse("mis_pedidos"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, f"Pedido #{pedido_propio.pk}")
        self.assertEqual(len(respuesta.context["pedidos"]), 1)

    def test_catalog_and_api_include_only_active_database_products(self):
        inactivo = Producto.objects.create(
            categoria=self.producto.categoria,
            nombre="Producto oculto",
            descripcion="No debe aparecer",
            precio=5000,
            imagen="productos/oculto.jpg",
            stock=1,
            activo=False,
        )

        respuesta = self.client.get(reverse("api_productos"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["total"], 1)
        self.assertEqual(respuesta.json()["productos"][0]["id"], self.producto.pk)
        self.assertNotEqual(respuesta.json()["productos"][0]["id"], inactivo.pk)
        self.assertContains(self.client.get(reverse("inicio")), "Mouse")

    def test_admin_can_change_order_state(self):
        pedido = Pedido.objects.create(cliente=self.cliente, total=10000)
        session = self.client.session
        session["rol"] = "admin"
        session.save()

        self.assertEqual(
            self.client.get(reverse("panel_pedido_detalle", args=[pedido.pk])).status_code,
            200,
        )
        respuesta = self.client.post(
            reverse("panel_pedido_detalle", args=[pedido.pk]),
            {"estado": "enviado"},
        )

        self.assertEqual(respuesta.status_code, 302)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, "enviado")

    def test_admin_pages_render_orders_and_only_customer_accounts(self):
        admin = Cliente.objects.create(
            nombre="Admin",
            apellido="TecStore",
            direccion="",
            correo="admin@example.com",
            password="hash",
            rol="admin",
        )
        session = self.client.session
        session["rol"] = "admin"
        session.save()

        pedidos = self.client.get(reverse("panel_pedidos"))
        clientes = self.client.get(reverse("panel_clientes"))

        self.assertEqual(pedidos.status_code, 200)
        self.assertEqual(clientes.status_code, 200)
        self.assertContains(clientes, self.cliente.correo)
        self.assertNotContains(clientes, admin.correo)


class CrearAdminCommandTests(TestCase):
    def setUp(self):
        Cliente.objects.filter(rol="admin").delete()

    @patch("config.management.commands.crear_admin.getpass", side_effect=["clave-segura-123", "clave-segura-123"])
    def test_creates_admin_with_hashed_password_when_none_exists(self, _getpass):
        call_command("crear_admin")

        admin = Cliente.objects.get(correo="admin@tienda.cl")
        self.assertEqual(admin.rol, "admin")
        self.assertTrue(check_password("clave-segura-123", admin.password))

    @patch("config.management.commands.crear_admin.getpass")
    def test_does_nothing_and_does_not_prompt_when_admin_exists(self, getpass_mock):
        Cliente.objects.create(
            nombre="Otro",
            apellido="Admin",
            direccion="-",
            correo="otro-admin@example.com",
            password="hash",
            rol="admin",
        )

        call_command("crear_admin")

        getpass_mock.assert_not_called()
        self.assertEqual(Cliente.objects.filter(rol="admin").count(), 1)

    def test_reports_conflicting_non_admin_email(self):
        Cliente.objects.create(
            nombre="Ana",
            apellido="Cliente",
            direccion="-",
            correo="admin@tienda.cl",
            password="hash",
        )

        with self.assertRaises(CommandError):
            call_command("crear_admin")


class AuthenticationTests(TestCase):
    def setUp(self):
        Cliente.objects.filter(rol="admin").delete()

    def test_registration_saves_customer_and_allows_database_login(self):
        registration = self.client.post(reverse("registro"), {
            "nombre": "Valeria",
            "apellido": "Pérez",
            "direccion": "Calle 123",
            "correo": "valeria@example.com",
            "password": "mi-clave-segura",
        })

        self.assertRedirects(registration, reverse("login"), fetch_redirect_response=False)
        cliente = Cliente.objects.get(correo="valeria@example.com")
        self.assertTrue(check_password("mi-clave-segura", cliente.password))

        login = self.client.post(reverse("login"), {
            "correo": "valeria@example.com",
            "password": "mi-clave-segura",
        })

        self.assertRedirects(login, reverse("inicio"), fetch_redirect_response=False)
        session = self.client.session
        self.assertEqual(session["usuario"], cliente.correo)
        self.assertEqual(session["rol"], "cliente")

    def test_admin_login_sets_role_and_redirects_to_panel(self):
        admin = Cliente.objects.create(
            nombre="Admin",
            apellido="Tienda",
            direccion="-",
            correo="admin@tienda.cl",
            password=make_password("mi-clave-segura"),
            rol="admin",
        )

        response = self.client.post(reverse("login"), {
            "correo": admin.correo,
            "password": "mi-clave-segura",
        })

        self.assertRedirects(response, reverse("panel"), fetch_redirect_response=False)
        session = self.client.session
        self.assertEqual(session["usuario"], admin.correo)
        self.assertEqual(session["rol"], "admin")

    def test_api_usuario_reads_customer_from_session_and_database(self):
        cliente = Cliente.objects.create(
            nombre="Ana",
            apellido="Pérez",
            direccion="Calle 123",
            correo="ana@example.com",
            password="hash",
        )
        session = self.client.session
        session["usuario"] = cliente.correo
        session.save()

        response = self.client.get(reverse("api_usuario"))

        datos = response.json()
        self.assertTrue(datos["autenticado"])
        self.assertEqual(datos["id"], cliente.id)
        self.assertEqual(datos["correo"], cliente.correo)
        self.assertEqual(datos["nombre"], cliente.nombre)
        self.assertEqual(datos["apellido"], cliente.apellido)
        self.assertEqual(datos["direccion"], cliente.direccion)
        self.assertEqual(datos["rol"], cliente.rol)
        self.assertNotIn("password", datos)

    @override_settings(
        ADMIN_INITIAL_EMAIL="admin@tienda.cl",
        ADMIN_INITIAL_PASSWORD="docker-initial-secret",
    )
    def test_post_migrate_provisions_admin_once(self):
        app_config = apps.get_app_config("config")
        signal_args = {
            "app_config": app_config,
            "verbosity": 0,
            "interactive": False,
            "using": "default",
        }

        post_migrate.send(sender=app_config, **signal_args)
        post_migrate.send(sender=app_config, **signal_args)

        admin = Cliente.objects.get(correo="admin@tienda.cl")
        self.assertEqual(admin.rol, "admin")
        self.assertTrue(check_password("docker-initial-secret", admin.password))
        self.assertEqual(Cliente.objects.filter(rol="admin").count(), 1)
