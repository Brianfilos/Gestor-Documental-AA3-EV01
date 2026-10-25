# Despliegue en producción: gestor.filosdev.com

Guía para publicar en el VPS (UltaHost, con HestiaCP) la página principal, el Sistema Gestor
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
- `hestia/gestordoc.tpl` y `hestia/gestordoc.stpl`: plantilla de proxy de Hestia (HTTP y HTTPS).
- `systemd/gestor-documental.service`: servicio de Gunicorn.
- `env.produccion.ejemplo`: plantilla del archivo `.env`.

## Cómo convive con las otras aplicaciones del servidor

Se usa el mismo esquema de `cierres.filosdev.com` (servicio `cancelaciones`):

| Elemento | Gestor Documental | Ya existente (no se toca) |
|---|---|---|
| Código | `/opt/gestor-documental` | `/opt/cancelaciones`, `/root/conciliaciones`, … |
| Usuario de sistema | `gestordoc` | `cancelaciones`, … |
| Gunicorn | `127.0.0.1:8020` | 8000, 8001 y 8010 |
| Dominio en Hestia | `gestor.filosdev.com`, plantilla `gestordoc` | filosdev.com, conciliaciones, cierres |
| Base de datos | `gestor_documental` en MariaDB, usuario `gestor` | las demás bases |

Ningún paso modifica otro dominio, servicio o base de datos. Todos los comandos se ejecutan
como `root`.

## 1. Comprobar que el puerto 8020 sigue libre

```bash
ss -tlnp | grep ':8020\b' || echo "8020 libre"
```

## 2. Código, usuario y entorno virtual

```bash
apt install -y git python3-venv
useradd --system --home-dir /opt/gestor-documental --shell /usr/sbin/nologin gestordoc
git clone -b despliegue-produccion https://github.com/Brianfilos/Gestor-Documental-AA3-EV01.git /opt/gestor-documental
cd /opt/gestor-documental/proyecto/backend
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

## 3. Base de datos propia en MariaDB

Escoge una contraseña y úsala en los dos lugares (aquí y en el `.env`):

```bash
mysql
```

```sql
CREATE DATABASE gestor_documental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gestor'@'localhost' IDENTIFIED BY 'CONTRASEÑA_DEL_GESTOR';
GRANT ALL PRIVILEGES ON gestor_documental.* TO 'gestor'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 4. Archivo .env

```bash
cp ../despliegue/env.produccion.ejemplo .env
python3 -c "import secrets; print(secrets.token_urlsafe(50))"   # copia el resultado en SECRET_KEY
nano .env                                                      # SECRET_KEY y DB_PASSWORD
chmod 600 .env
```

## 5. Tablas, archivos estáticos y datos de demostración

```bash
export DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
venv/bin/python seed_demo.py        # 4 usuarios, 6 clasificaciones y 12 documentos
venv/bin/python manage.py check --deploy
mkdir -p media
chown -R gestordoc:gestordoc /opt/gestor-documental
```

`seed_demo.py` crea el usuario `admin@gestordoc.com` con la contraseña `Admin2024*`, que es la
que muestra la página para que la instructora pueda probar.

## 6. Servicio de Gunicorn

```bash
cp ../despliegue/systemd/gestor-documental.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now gestor-documental
systemctl status gestor-documental --no-pager
curl -I http://127.0.0.1:8020/login/          # debe responder 200
```

## 7. Dominio en Hestia con su plantilla de proxy

```bash
cp ../despliegue/hestia/gestordoc.tpl ../despliegue/hestia/gestordoc.stpl /usr/local/hestia/data/templates/web/nginx/
chmod 644 /usr/local/hestia/data/templates/web/nginx/gestordoc.*

/usr/local/hestia/bin/v-add-web-domain admin gestor.filosdev.com 151.243.101.226
/usr/local/hestia/bin/v-delete-web-domain-alias admin gestor.filosdev.com www.gestor.filosdev.com
/usr/local/hestia/bin/v-change-web-domain-proxy-tpl admin gestor.filosdev.com gestordoc
nginx -t
curl -I http://gestor.filosdev.com/
```

Si `v-delete-web-domain-alias` dice que el alias no existe, continúa sin problema.

## 8. Certificado HTTPS (Let's Encrypt desde Hestia)

```bash
/usr/local/hestia/bin/v-add-letsencrypt-domain admin gestor.filosdev.com
/usr/local/hestia/bin/v-add-web-domain-ssl-force admin gestor.filosdev.com
/usr/local/hestia/bin/v-list-web-domain admin gestor.filosdev.com    # SSL: yes, PROXY: gestordoc
```

## 9. Verificación

```bash
curl -I https://gestor.filosdev.com/
curl -I https://gestor.filosdev.com/movil/
curl -I https://gestor.filosdev.com/login/
curl -I https://gestor.filosdev.com/static/admin/css/base.css
curl -s -X POST https://gestor.filosdev.com/api/auth/login/ \
     -H 'Content-Type: application/json' \
     -d '{"correo":"admin@gestordoc.com","password":"Admin2024*"}' | head -c 120; echo
```

## Si algo falla

```bash
journalctl -u gestor-documental -n 50 --no-pager                 # errores de Django/Gunicorn
tail -n 50 /var/log/nginx/domains/gestor.filosdev.com.error.log   # errores de Nginx
```

Para quitar el gestor sin afectar nada más:

```bash
/usr/local/hestia/bin/v-delete-web-domain admin gestor.filosdev.com
systemctl disable --now gestor-documental && rm /etc/systemd/system/gestor-documental.service
```

## Actualizar después de un cambio en GitHub

```bash
cd /opt/gestor-documental && sudo -u gestordoc git pull
cd proyecto/backend
export DJANGO_SETTINGS_MODULE=gestor_documental.settings_produccion
sudo -u gestordoc venv/bin/pip install -r requirements.txt
sudo -u gestordoc -E venv/bin/python manage.py migrate
sudo -u gestordoc -E venv/bin/python manage.py collectstatic --noinput
systemctl restart gestor-documental
```

Si cambian las plantillas de `hestia/`, cópialas de nuevo y ejecuta
`/usr/local/hestia/bin/v-rebuild-web-domain admin gestor.filosdev.com`.

## App Android contra el servidor publicado

Para compilar el APK contra producción, cambia en `proyecto/android/app/build.gradle` el valor
de `API_BASE_URL` a `https://gestor.filosdev.com/api/`.
