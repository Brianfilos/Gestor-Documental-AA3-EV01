"""
Configuración del AMBIENTE DE PRUEBAS del Sistema Gestor Documental.

Reutiliza toda la configuración de producción/desarrollo (settings.py) y
únicamente reemplaza el motor de base de datos por SQLite en memoria, de modo
que las pruebas automatizadas se puedan ejecutar sin depender del servidor
MySQL local y sin alterar los datos reales del sistema.

Uso:
    python manage.py test --settings=gestor_documental.settings_test -v 2
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Hash de contraseñas rápido: acelera la creación de usuarios de prueba.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Los archivos cargados durante las pruebas no se escriben en media/ real.
MEDIA_ROOT = BASE_DIR / 'test_media'  # noqa: F405

DEBUG = False
