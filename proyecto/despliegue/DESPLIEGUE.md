# Despliegue en producción: gestor.filosdev.com

Guía para publicar en el VPS (UltaHost) la página principal, el Sistema Gestor
Documental (Django + API REST) y la versión web de la app móvil.

| Dirección | Qué se ve |
|---|---|
| `https://gestor.filosdev.com/` | Página principal (plantilla SaaS Application adaptada) |
| `https://gestor.filosdev.com/movil/` | Versión web de la app móvil (también va dentro de la página principal) |
| `https://gestor.filosdev.com/login/` | Aplicación web del Gestor Documental |
| `https://gestor.filosdev.com/api/` | API REST (JWT) que usan la app Android y la versión web |
| `https://gestor.filosdev.com/admin/` | Administración de Django |

Archivos de esta carpeta:

- `landing/`: página principal.
- `movil/`: versión web de la app móvil (HTML, CSS y JS, sin dependencias).
- `nginx/gestor.filosdev.com.conf`: sitio de Nginx.
- `systemd/gestor-documental.service`: servicio de Gunicorn.
- `env.produccion.ejemplo`: plantilla del archivo `.env`.

> El servidor ya tiene otras aplicaciones. Ningún paso modifica sus sitios de Nginx ni sus
> bases de datos: el gestor usa su propio sitio, su propio puerto interno (8001) y su propia
> base de datos.

## 0. Revisar el servidor antes de empezar

```bash
lsb_release -a                 # versión de Ubuntu
python3 --version              # se necesita 3.10 o superior
ss -tlnp | grep -E ':(80|443|3306|8001)\b'   # el 8001 debe estar libre
ls /etc/nginx/sites-enabled/   # sitios que ya existen (no se tocan)
```

Si el puerto 8001 está ocupado, cambia `8001` por otro libre en
`systemd/gestor-documental.service` y en `nginx/gestor.filosdev.com.conf`.

## 1. DNS

El registro `A` de `gestor.filosdev.com` debe apuntar a `151.243.101.226`:

```bash
dig +short gestor.filosdev.com
```

## 2. Paquetes del sistema

```bash
apt update
apt install -y git python3-venv python3-pip nginx certbot python3-certbot-nginx
```

Si el servidor no tiene MySQL y quieres usarlo: `apt install -y mysql-server`. Si
prefieres no usar MySQL, salta el paso 5 y usa `DB_ENGINE=sqlite` en el `.env`.

## 3. Descargar el código

```bash
git clone -b despliegue-produccion https://github.com/Brianfilos/Gestor-Documental-AA3-EV01.git /opt/gestor-documental
cd /opt/gestor-documental/proyecto/backend
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

## 4. Variables de entorno

```bash
cp ../despliegue/env.produccion.ejemplo .env
python3 -c "import secrets; print(secrets.token_urlsafe(50))"   # copia el resultado en SECRET_KEY
nano .env
```

Mientras no tengas el certificado HTTPS (paso 9), deja `COOKIES_SEGURAS=False`;
después cámbialo a `True`.

## 5. Base de datos MySQL propia del gestor

```bash
mysql -u root -p
```

```sql
CREATE DATABASE gestor_documental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gestor'@'localhost' IDENTIFIED BY 'la-misma-contraseña-del-.env';
GRANT ALL PRIVILEGES ON gestor_documental.* TO 'gestor'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

En el `.env` deja `DB_HOST=localhost` si creaste el usuario como `'gestor'@'localhost'`.

## 6. Tablas, archivos estáticos y datos de demostración

```bash
export DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
venv/bin/python seed_demo.py        # 4 usuarios, 6 clasificaciones y 12 documentos
venv/bin/python manage.py check --deploy
```

`seed_demo.py` crea el usuario `admin@gestordoc.com` con la contraseña `Admin2024*`
(es la que se muestra en la página para que la instructora pueda probar).

Permisos para el usuario del servicio:

```bash
mkdir -p media
chown -R www-data:www-data /opt/gestor-documental/proyecto/backend/media
# Solo si usas SQLite:
# chown www-data:www-data /opt/gestor-documental/proyecto/backend /opt/gestor-documental/proyecto/backend/produccion.sqlite3
```

## 7. Servicio de Gunicorn

```bash
cp ../despliegue/systemd/gestor-documental.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now gestor-documental
systemctl status gestor-documental --no-pager
curl -I http://127.0.0.1:8001/login/          # debe responder 200
```

## 8. Sitio de Nginx

```bash
cp ../despliegue/nginx/gestor.filosdev.com.conf /etc/nginx/sites-available/gestor.filosdev.com
ln -s /etc/nginx/sites-available/gestor.filosdev.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
curl -I http://gestor.filosdev.com/
```

## 9. Certificado HTTPS (Let's Encrypt)

```bash
certbot --nginx -d gestor.filosdev.com --redirect
sed -i 's/^COOKIES_SEGURAS=.*/COOKIES_SEGURAS=True/' /opt/gestor-documental/proyecto/backend/.env
systemctl restart gestor-documental
```

## 10. Verificación

```bash
curl -I https://gestor.filosdev.com/
curl -I https://gestor.filosdev.com/movil/
curl -I https://gestor.filosdev.com/login/
curl -s -X POST https://gestor.filosdev.com/api/auth/login/ \
     -H 'Content-Type: application/json' \
     -d '{"correo":"admin@gestordoc.com","password":"Admin2024*"}' | head -c 120; echo
```

## Actualizar después de un cambio en GitHub

```bash
cd /opt/gestor-documental && git pull
cd proyecto/backend
export DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
systemctl restart gestor-documental
```

## App Android contra el servidor publicado

Para compilar el APK contra producción, cambia en `proyecto/android/app/build.gradle` el
valor de `API_BASE_URL` a `https://gestor.filosdev.com/api/`.
