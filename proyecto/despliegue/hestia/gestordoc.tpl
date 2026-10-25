#=========================================================================#
# Plantilla de proxy de Hestia para gestor.filosdev.com (HTTP)            #
# Basada en la plantilla "cancelaciones" del servidor.                    #
# Copiar a /usr/local/hestia/data/templates/web/nginx/gestordoc.tpl       #
#=========================================================================#
#
#   /            -> página principal (archivo estático)
#   /sitio/      -> recursos de la página principal
#   /movil/      -> versión web de la app móvil
#   /static/     -> archivos estáticos de Django (collectstatic)
#   /media/      -> documentos cargados por los usuarios
#   lo demás     -> Gunicorn del gestor en 127.0.0.1:8020

server {
        listen      %ip%:%proxy_port%;
        server_name %domain_idn% %alias_idn%;
        error_log   /var/log/%web_system%/domains/%domain%.error.log error;
        access_log  /var/log/%web_system%/domains/%domain%.log combined;

        include %home%/%user%/conf/web/%domain%/nginx.forcessl.conf*;

        client_max_body_size 20M;

        location ~ /\.(?!well-known\/|file) {
                deny all;
                return 404;
        }

        location = / {
                root /opt/gestor-documental/proyecto/despliegue/landing;
                try_files /index.html =404;
        }

        location ^~ /sitio/ {
                alias /opt/gestor-documental/proyecto/despliegue/landing/;
                expires 7d;
        }

        location = /movil {
                return 301 /movil/;
        }

        location ^~ /movil/ {
                alias /opt/gestor-documental/proyecto/despliegue/movil/;
                index index.html;
        }

        location ^~ /static/ {
                alias /opt/gestor-documental/proyecto/backend/staticfiles/;
                expires 7d;
        }

        location ^~ /media/ {
                alias /opt/gestor-documental/proyecto/backend/media/;
        }

        location / {
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_pass http://127.0.0.1:8020;
        }

        location /error/ {
                alias %home%/%user%/web/%domain%/document_errors/;
        }

        include %home%/%user%/conf/web/%domain%/nginx.conf_*;
}
