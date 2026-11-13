import logging

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver


logger = logging.getLogger(__name__)


@receiver(post_migrate, dispatch_uid="config.provision_initial_admin")
def provision_initial_admin(sender, **kwargs):
    if sender.label != "config":
        return

    from .models import Cliente

    if Cliente.objects.filter(rol="admin").exists():
        return

    password = settings.ADMIN_INITIAL_PASSWORD
    if not password:
        logger.warning(
            "No se creó el administrador inicial: define ADMIN_INITIAL_PASSWORD "
            "antes de ejecutar migrate."
        )
        return

    email = settings.ADMIN_INITIAL_EMAIL
    if Cliente.objects.filter(correo__iexact=email).exists():
        raise ImproperlyConfigured(
            f"{email} ya está registrado y no tiene rol admin; "
            "resuelve el conflicto antes de aprovisionar el administrador."
        )

    try:
        with transaction.atomic():
            if Cliente.objects.filter(rol="admin").exists():
                return
            Cliente.objects.create(
                nombre="Admin",
                apellido="Tienda",
                direccion="-",
                correo=email,
                password=make_password(password),
                rol="admin",
            )
    except IntegrityError:
        if not Cliente.objects.filter(rol="admin").exists():
            raise
