"""
Configuración de DEMOSTRACIÓN del Sistema Gestor Documental.

Se usa únicamente para grabar un video de ejecución (evidencia GA9-220501096-
AA3-EV01). Reutiliza toda la configuración de producción/desarrollo
(settings.py) y reemplaza la base de datos por un archivo SQLite propio,
separado de la base MySQL real, de modo que la grabación nunca lee ni escribe
datos reales del proyecto.

Uso:
    python manage.py migrate --settings=gestor_documental.settings_demo
    python seed_demo.py
    python manage.py runserver 127.0.0.1:8010 --settings=gestor_documental.settings_demo --noreload
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'demo_db.sqlite3',  # noqa: F405
    }
}

MEDIA_ROOT = BASE_DIR / 'demo_media'  # noqa: F405
DEBUG = True
ALLOWED_HOSTS = ['*']
