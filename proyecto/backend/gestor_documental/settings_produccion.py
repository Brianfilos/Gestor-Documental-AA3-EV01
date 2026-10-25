"""
Configuración de PRODUCCIÓN del Sistema Gestor Documental (gestor.filosdev.com).

Reutiliza settings.py y ajusta lo que cambia al publicar en Internet: DEBUG
apagado, dominio permitido, cookies seguras detrás de HTTPS y archivos
estáticos recolectados para que Nginx los entregue.

Todos los valores sensibles se leen del archivo .env del servidor (ver
proyecto/despliegue/env.produccion.ejemplo).

Uso:
    export DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn gestor_documental.wsgi:application --bind 127.0.0.1:8001
"""
from decouple import Csv, config

from .settings import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='gestor.filosdev.com', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://gestor.filosdev.com', cast=Csv())

# Base de datos: MySQL por defecto (DB_* en .env). Con DB_ENGINE=sqlite se usa un
# archivo SQLite local, útil si el servidor no tiene MySQL disponible.
if config('DB_ENGINE', default='mysql') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'produccion.sqlite3',  # noqa: F405
        }
    }

# Nginx termina HTTPS y reenvía la petición a Gunicorn por HTTP.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = config('COOKIES_SEGURAS', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('COOKIES_SEGURAS', default=True, cast=bool)

# La API se consume desde el mismo dominio (versión web de la app móvil) y desde
# la app Android, que no envía cabecera Origin; no hace falta abrir CORS a todos.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='https://gestor.filosdev.com', cast=Csv())

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405
MEDIA_ROOT = BASE_DIR / 'media'  # noqa: F405

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}

# La carpeta static/ del proyecto es opcional (Git no versiona carpetas vacías).
STATICFILES_DIRS = [d for d in STATICFILES_DIRS if d.exists()]  # noqa: F405
