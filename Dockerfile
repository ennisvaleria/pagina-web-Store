# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Evitar que Python genere archivos .pyc y asegurar que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para Django/Psycopg2 si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
# Nota: Asumimos que crearás un requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . /app/

# Exponer el puerto que usa Django (por defecto 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn (recomendado para producción)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
