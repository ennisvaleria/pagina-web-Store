from getpass import getpass

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from config.models import Cliente


class Command(BaseCommand):
    help = "Crea admin@tienda.cl si todavía no existe un administrador."

    def handle(self, *args, **options):
        if Cliente.objects.filter(rol="admin").exists():
            self.stdout.write("Ya existe un usuario administrador; no se realizaron cambios.")
            return

        if Cliente.objects.filter(correo__iexact="admin@tienda.cl").exists():
            raise CommandError(
                "admin@tienda.cl ya está registrado sin rol de administrador. "
                "Revisa esa cuenta antes de volver a ejecutar el comando."
            )

        password = getpass("Contraseña para admin@tienda.cl: ")
        confirmacion = getpass("Repite la contraseña: ")
        if not password or password != confirmacion:
            raise CommandError("Las contraseñas están vacías o no coinciden.")

        try:
            with transaction.atomic():
                if Cliente.objects.filter(rol="admin").exists():
                    self.stdout.write("Ya existe un usuario administrador; no se realizaron cambios.")
                    return

                Cliente.objects.create(
                    nombre="Admin",
                    apellido="Tienda",
                    direccion="-",
                    correo="admin@tienda.cl",
                    password=make_password(password),
                    rol="admin",
                )
        except IntegrityError as error:
            raise CommandError(
                "No se pudo crear admin@tienda.cl porque el correo ya está registrado."
            ) from error

        self.stdout.write(self.style.SUCCESS("Cuenta admin@tienda.cl creada correctamente."))
