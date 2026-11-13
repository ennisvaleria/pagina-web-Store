# Arquitectura del Sistema - Página Web Store

Este documento describe la arquitectura implementada en el proyecto, basada en el patrón **MVT (Model-View-Template)** de Django.

## Diagrama de Arquitectura

```mermaid
graph TD
    User((Usuario/Navegador)) -- "1. Petición HTTP (URL)" --> URLs[urls.py]
    URLs -- "2. Redirige a" --> Views[views.py]
    
    subgraph "Lógica de Servidor (Django)"
        Views -- "3. Consulta/Guarda datos" --> Models[models.py]
        Models -- "4. Acceso a datos" --> DB[(db.sqlite3)]
        DB -- "5. Retorna datos" --> Models
        Models -- "6. Datos procesados" --> Views
        Views -- "7. Renderiza datos" --> Templates[Templates HTML]
    end
    
    Templates -- "8. Respuesta HTML" --> User
```

## Descripción de los Componentes

1.  **Usuario/Navegador**: El cliente que interactúa con la interfaz web enviando solicitudes.
2.  **URLs (`urls.py`)**: Actúa como el despachador de peticiones. Mapea la dirección solicitada con la función de vista correspondiente.
3.  **Vistas (`views.py`)**: Contiene la lógica de negocio. Recibe la petición, interactúa con los modelos y determina qué plantilla mostrar.
4.  **Modelos (`models.py`)**: Define la estructura de los datos y actúa como interfaz entre la lógica de Django y la base de datos.
5.  **Base de Datos (`db.sqlite3`)**: Almacén persistente de la información del sistema.
6.  **Plantillas (`Templates`)**: Archivos HTML que definen cómo se presenta la información al usuario final.

## Flujo de Datos
El flujo es cíclico: **Usuario** $\rightarrow$ **URL** $\rightarrow$ **Vista** $\rightarrow$ **Modelo** $\rightarrow$ **DB** $\rightarrow$ **Modelo** $\rightarrow$ **Vista** $\rightarrow$ **Template** $\rightarrow$ **Usuario**.

## Administrador del panel

El login y el registro usan el modelo `Cliente`; las contraseñas se guardan cifradas. Al ejecutar las migraciones, Django crea `admin@tienda.cl` si todavía no existe ningún administrador y si se configuró la variable de entorno `ADMIN_INITIAL_PASSWORD`. `ADMIN_INITIAL_EMAIL` permite cambiar el correo; su valor predeterminado es `admin@tienda.cl`.

Para desarrollo local, antes de migrar:

```bash
export ADMIN_INITIAL_PASSWORD='elige-una-clave-segura'
python manage.py migrate
```

La contraseña se lee del entorno y no está guardada en el repositorio. Si ya hay un administrador, el aprovisionamiento no lo modifica. Para crear uno manualmente, también está disponible `python manage.py crear_admin`, que solicita la contraseña de forma interactiva.

Para Docker Compose, crea un archivo `.env` junto al `docker-compose.yml` en el servidor:

```env
DEBUG=0
ALLOWED_HOSTS=tienda.ejemplo.cl,www.tienda.ejemplo.cl
CSRF_TRUSTED_ORIGINS=https://tienda.ejemplo.cl,https://www.tienda.ejemplo.cl
ADMIN_INITIAL_PASSWORD=elige-una-clave-segura
```

Reemplaza los dominios por los del servidor. El servicio ejecuta las migraciones antes de iniciar; no subas `.env` ni la contraseña al repositorio.

Nginx sirve los archivos estáticos y las imágenes subidas desde `staticfiles/` y `media/`; ambos directorios permanecen en el servidor mediante el volumen del proyecto.
