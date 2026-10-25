/*
 * Versión web de la app móvil del Gestor Documental.
 * Mismas pantallas que la app Android: Login, Dashboard, Documentos (lista,
 * detalle con revisiones e historial, formulario), Historial y Usuarios.
 * Consume la API REST del proyecto (apps/api) con token JWT.
 */
(function () {
  'use strict';

  // La API vive en el mismo dominio. Para pruebas locales se puede indicar otra
  // con ?api=http://127.0.0.1:8000/api/
  var API = new URLSearchParams(location.search).get('api') || '/api/';
  var app = document.getElementById('app');

  var ESTADOS = { activo: 'Activo', inactivo: 'Inactivo', revision: 'En revisión', archivado: 'Archivado' };

  var ICONOS = {
    menu: 'M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z',
    atras: 'M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20z',
    doc: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zm-1 7V3.5L18.5 9z',
    dash: 'M3 13h8V3H3zm0 8h8v-6H3zm10 0h8V11h-8zm0-18v6h8V3z',
    hist: 'M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6a7 7 0 1 1 2.05 4.95l-1.42 1.42A9 9 0 1 0 13 3zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8z',
    users: 'M16 11a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm-8 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13zm8 0c-.29 0-.62.02-.97.05A4.22 4.22 0 0 1 17 16.5V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z',
    salir: 'M10.09 15.59 11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67zM19 3H5a2 2 0 0 0-2 2v4h2V5h14v14H5v-4H3v4a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z',
    mas: 'M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z',
    buscar: 'M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16a6.47 6.47 0 0 0 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z'
  };

  function svg(nombre) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + ICONOS[nombre] + '"/></svg>';
  }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function fecha(v) {
    if (!v) return '';
    var d = new Date(v.length === 10 ? v + 'T00:00:00' : v);
    if (isNaN(d)) return v;
    var f = d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' });
    return v.length === 10 ? f : f + ' ' + d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
  }

  // ---------- Sesión (equivalente a SessionManager.kt) ----------
  var memoria = {};
  var sesion = {
    get: function (k) { try { return localStorage.getItem('gd_' + k); } catch (e) { return memoria[k] || null; } },
    set: function (k, v) { try { localStorage.setItem('gd_' + k, v); } catch (e) { memoria[k] = v; } },
    limpiar: function () {
      ['token', 'refresh', 'usuario'].forEach(function (k) {
        try { localStorage.removeItem('gd_' + k); } catch (e) { delete memoria[k]; }
      });
    },
    usuario: function () { try { return JSON.parse(sesion.get('usuario')) || {}; } catch (e) { return {}; } }
  };

  // ---------- Cliente de la API (equivalente a ApiService.kt) ----------
  function api(ruta, opciones) {
    opciones = opciones || {};
    var cabeceras = { 'Accept': 'application/json' };
    if (opciones.body) cabeceras['Content-Type'] = 'application/json';
    var token = sesion.get('token');
    if (token && !opciones.publico) cabeceras['Authorization'] = 'Bearer ' + token;
    return fetch(API + ruta, {
      method: opciones.method || 'GET',
      headers: cabeceras,
      body: opciones.body ? JSON.stringify(opciones.body) : undefined
    }).then(function (r) {
      if (r.status === 401 && !opciones.publico) {
        sesion.limpiar();
        location.hash = '#/login';
        throw new Error('La sesión expiró. Inicia sesión de nuevo.');
      }
      if (r.status === 204) return null;
      return r.json().catch(function () { return null; }).then(function (datos) {
        if (!r.ok) {
          var msg = (datos && (datos.detail || Object.keys(datos).map(function (k) {
            return k + ': ' + [].concat(datos[k]).join(' ');
          }).join(' · '))) || ('Error ' + r.status);
          throw new Error(msg);
        }
        return datos;
      });
    });
  }

  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toast.t);
    toast.t = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }

  function cargando() { return '<div class="loading"><div class="spinner"></div>Cargando…</div>'; }
  function errorConexion(e) { return '<div class="empty">' + esc(e.message || 'Error de conexión con el servidor') + '</div>'; }

  // ---------- Estructura con barra superior y menú lateral (MainActivity) ----------
  function marco(titulo, seccion, cuerpo, opciones) {
    opciones = opciones || {};
    var u = sesion.usuario();
    var boton = opciones.atras
      ? '<button class="icon-btn" data-atras aria-label="Volver">' + svg('atras') + '</button>'
      : '<button class="icon-btn" data-menu aria-label="Abrir menú">' + svg('menu') + '</button>';
    var item = function (ruta, clave, icono, texto) {
      return '<a href="#/' + ruta + '" class="' + (seccion === clave ? 'active' : '') + '">' + svg(icono) + texto + '</a>';
    };
    app.innerHTML =
      '<header class="toolbar">' + boton + '<h1>' + esc(titulo) + '</h1></header>' +
      '<div class="scrim" data-cerrar></div>' +
      '<aside class="drawer" aria-label="Menú">' +
        '<div class="drawer-head"><div class="avatar">' + svg('doc') + '</div>' +
          '<div class="n">' + esc(u.nombre || 'Usuario') + '</div>' +
          '<div class="c">' + esc(u.correo || '') + '</div>' +
          '<div class="r">' + esc(u.rol || 'Sin rol') + '</div></div>' +
        '<nav>' + item('dashboard', 'dashboard', 'dash', 'Dashboard') + item('documentos', 'documentos', 'doc', 'Documentos') +
          item('historial', 'historial', 'hist', 'Historial') + item('usuarios', 'usuarios', 'users', 'Usuarios') +
          '<hr><a href="#/salir">' + svg('salir') + 'Cerrar Sesión</a></nav>' +
      '</aside>' +
      '<main class="content" id="contenido">' + (cuerpo || cargando()) + '</main>' +
      (opciones.fab ? '<button class="fab" data-fab>' + svg('mas') + 'Nuevo</button>' : '');
    var menu = app.querySelector('[data-menu]');
    if (menu) menu.onclick = function () { document.body.classList.add('menu-open'); };
    var atras = app.querySelector('[data-atras]');
    if (atras) atras.onclick = function () { history.length > 1 ? history.back() : (location.hash = opciones.atras); };
    app.querySelector('[data-cerrar]').onclick = cerrarMenu;
    app.querySelectorAll('.drawer a').forEach(function (a) { a.addEventListener('click', cerrarMenu); });
    var fab = app.querySelector('[data-fab]');
    if (fab) fab.onclick = opciones.fab;
    return document.getElementById('contenido');
  }

  function cerrarMenu() { document.body.classList.remove('menu-open'); }

  function chipEstado(estado) {
    return '<span class="chip ' + esc(estado) + '">' + esc(ESTADOS[estado] || estado) + '</span>';
  }

  // ---------- Pantallas ----------
  function pantallaLogin() {
    app.innerHTML =
      '<section class="login">' +
        '<div class="login-brand"><div class="login-logo">' + svg('doc') + '</div>' +
          '<h1>GestorDoc</h1><p>Sistema Gestor Documental</p></div>' +
        '<form class="card" id="form-login" novalidate>' +
          '<h2>Bienvenido</h2><p class="sub">Ingresa tus credenciales para continuar</p>' +
          '<div class="error-box" id="error" hidden></div>' +
          '<div class="field"><label for="correo">Correo electrónico</label>' +
            '<input id="correo" type="email" autocomplete="username" placeholder="correo@ejemplo.com" required></div>' +
          '<div class="field"><label for="password">Contraseña</label>' +
            '<input id="password" type="password" autocomplete="current-password" placeholder="Contraseña" required></div>' +
          '<button class="btn btn-primary" id="btn-login" type="submit">Iniciar Sesión</button>' +
          '<p class="demo-hint">Usuario de demostración: <code>admin@gestordoc.com</code> · <code>Admin2024*</code></p>' +
        '</form>' +
      '</section>';
    var form = document.getElementById('form-login');
    form.onsubmit = function (ev) {
      ev.preventDefault();
      var correo = document.getElementById('correo').value.trim();
      var password = document.getElementById('password').value;
      var error = document.getElementById('error');
      var boton = document.getElementById('btn-login');
      if (!correo || !password) {
        error.textContent = 'Por favor completa todos los campos';
        error.hidden = false;
        return;
      }
      boton.disabled = true;
      boton.textContent = 'Ingresando…';
      api('auth/login/', { method: 'POST', body: { correo: correo, password: password }, publico: true })
        .then(function (r) {
          sesion.set('token', r.access);
          sesion.set('refresh', r.refresh);
          sesion.set('usuario', JSON.stringify(r.usuario));
          location.hash = '#/dashboard';
        })
        .catch(function (e) {
          error.textContent = /credentials|active account/i.test(e.message)
            ? 'Correo o contraseña incorrectos' : e.message;
          error.hidden = false;
          boton.disabled = false;
          boton.textContent = 'Iniciar Sesión';
        });
    };
  }

  function pantallaDashboard() {
    var c = marco('Dashboard', 'dashboard');
    Promise.all([api('documentos/'), api('usuarios/')]).then(function (r) {
      var docs = r[0], usuarios = r[1];
      var activos = docs.results.filter(function (d) { return d.estado === 'activo'; }).length;
      c.innerHTML =
        '<div class="saludo">Bienvenido, ' + esc(sesion.usuario().nombre || '') + '</div>' +
        '<div class="stats">' +
          '<div class="card stat"><div class="t">Documentos</div><div class="v">' + docs.count + '</div><div class="s">Total registrados</div></div>' +
          '<div class="card stat"><div class="t">Activos</div><div class="v green">' + activos + '</div><div class="s">Documentos activos</div></div>' +
          '<div class="card stat stat-wide"><div><div class="t">Usuarios</div><div class="s">Usuarios del sistema</div></div><div class="v">' + usuarios.count + '</div></div>' +
        '</div>' +
        '<div class="section-title">Documentos recientes</div>' +
        '<div class="card">' + (docs.results.slice(0, 5).map(function (d) {
          return '<div class="mini" data-doc="' + d.idDocumento + '"><div><div class="tt">' + esc(d.titulo) + '</div>' +
            '<div class="hist-user">' + esc(d.clasificacion_nombre) + ' · ' + fecha(d.fechaCarga) + '</div></div>' + chipEstado(d.estado) + '</div>';
        }).join('') || '<div class="empty">No hay elementos para mostrar</div>') + '</div>';
      c.querySelectorAll('[data-doc]').forEach(function (el) {
        el.onclick = function () { location.hash = '#/documentos/' + el.dataset.doc; };
      });
    }).catch(function (e) { c.innerHTML = errorConexion(e); });
  }

  var filtro = { q: '', estado: '' };

  function pantallaDocumentos() {
    var c = marco('Documentos', 'documentos', null, { fab: function () { location.hash = '#/documentos/nuevo'; } });
    c.innerHTML =
      '<form class="search" id="buscar"><input id="q" type="search" placeholder="Buscar por título o descripción" value="' + esc(filtro.q) + '">' +
        '<button class="btn btn-sm btn-outline" style="height:44px" aria-label="Buscar">' + svg('buscar') + '</button></form>' +
      '<div class="chips-filter">' + [['', 'Todos']].concat(Object.keys(ESTADOS).map(function (k) { return [k, ESTADOS[k]]; }))
        .map(function (e) { return '<button data-estado="' + e[0] + '" class="' + (filtro.estado === e[0] ? 'on' : '') + '">' + e[1] + '</button>'; }).join('') +
      '</div><div id="lista">' + cargando() + '</div>';
    document.getElementById('buscar').onsubmit = function (ev) {
      ev.preventDefault();
      filtro.q = document.getElementById('q').value.trim();
      cargarLista();
    };
    c.querySelectorAll('[data-estado]').forEach(function (b) {
      b.onclick = function () {
        filtro.estado = b.dataset.estado;
        c.querySelectorAll('[data-estado]').forEach(function (x) { x.classList.toggle('on', x === b); });
        cargarLista();
      };
    });
    cargarLista();
  }

  function cargarLista() {
    var lista = document.getElementById('lista');
    lista.innerHTML = cargando();
    var qs = [];
    if (filtro.q) qs.push('q=' + encodeURIComponent(filtro.q));
    if (filtro.estado) qs.push('estado=' + filtro.estado);
    api('documentos/' + (qs.length ? '?' + qs.join('&') : '')).then(function (r) {
      lista.innerHTML = r.results.map(function (d) {
        return '<article class="card"><h3 class="doc-title">' + esc(d.titulo) + '</h3>' +
          '<p class="doc-desc">' + esc(d.descripcion || '') + '</p>' +
          '<div class="chips">' + chipEstado(d.estado) + '<span class="chip clasif">' + esc(d.clasificacion_nombre) + '</span></div>' +
          '<div class="meta"><span>' + fecha(d.fechaCarga) + '</span><span>' + esc(d.usuario_nombre) + '</span></div>' +
          '<div class="actions"><button class="btn btn-sm btn-outline" data-ver="' + d.idDocumento + '">Ver</button>' +
          '<button class="btn btn-sm btn-text" data-editar="' + d.idDocumento + '">Editar</button></div></article>';
      }).join('') || '<div class="empty">No hay documentos para mostrar</div>';
      if (r.count > r.results.length) {
        lista.insertAdjacentHTML('beforeend', '<div class="empty" style="padding:12px">Mostrando ' + r.results.length + ' de ' + r.count + ' documentos</div>');
      }
      lista.querySelectorAll('[data-ver]').forEach(function (b) { b.onclick = function () { location.hash = '#/documentos/' + b.dataset.ver; }; });
      lista.querySelectorAll('[data-editar]').forEach(function (b) { b.onclick = function () { location.hash = '#/documentos/' + b.dataset.editar + '/editar'; }; });
    }).catch(function (e) { lista.innerHTML = errorConexion(e); });
  }

  function pantallaDetalle(id) {
    var c = marco('Detalle de Documento', 'documentos', null, { atras: '#/documentos' });
    Promise.all([api('documentos/' + id + '/'), api('documentos/' + id + '/revisiones/'), api('documentos/' + id + '/historial/')])
      .then(function (r) {
        var d = r[0], revisiones = r[1], historial = r[2];
        c.innerHTML =
          '<div class="card"><h3 class="doc-title" style="font-size:18px">' + esc(d.titulo) + '</h3>' +
            '<p class="doc-desc" style="-webkit-line-clamp:unset">' + esc(d.descripcion || 'Sin descripción') + '</p>' +
            '<div class="detail-grid">' +
              '<div><div class="k">Estado</div><div class="v">' + chipEstado(d.estado) + '</div></div>' +
              '<div><div class="k">Clasificación</div><div class="v">' + esc(d.clasificacion_nombre) + '</div></div>' +
              '<div><div class="k">Fecha</div><div class="v">' + fecha(d.fechaCarga) + '</div></div>' +
              '<div><div class="k">Cargado por</div><div class="v">' + esc(d.usuario_nombre) + '</div></div>' +
            '</div>' +
            '<div class="actions"><button class="btn btn-sm btn-outline" data-editar>Editar</button></div></div>' +
          '<div class="section-title">Agregar revisión</div>' +
          '<form class="card" id="form-rev"><div class="field" style="margin-bottom:10px"><textarea id="comentario" placeholder="Escribe el comentario de la revisión"></textarea></div>' +
            '<button class="btn btn-primary" type="submit">Agregar revisión</button></form>' +
          '<div class="section-title">Revisiones (' + revisiones.length + ')</div>' +
          (revisiones.map(function (rv) {
            return '<div class="card"><div class="row"><span class="hist-accion">' + esc(rv.usuario_nombre) + '</span><span class="hist-fecha">' + fecha(rv.fechaRevision) + '</span></div>' +
              '<div class="hist-doc">' + esc(rv.comentario || '') + '</div></div>';
          }).join('') || '<div class="card empty" style="padding:16px">Sin revisiones</div>') +
          '<div class="section-title">Historial</div>' +
          '<div class="card">' + (historial.map(function (h) {
            return '<div class="mini"><div><div class="tt">' + esc(h.accion) + '</div><div class="hist-user">' + esc(h.usuario_nombre) + '</div></div>' +
              '<span class="hist-fecha">' + fecha(h.fechaAccion) + '</span></div>';
          }).join('') || '<div class="empty">Sin movimientos</div>') + '</div>';
        c.querySelector('[data-editar]').onclick = function () { location.hash = '#/documentos/' + id + '/editar'; };
        document.getElementById('form-rev').onsubmit = function (ev) {
          ev.preventDefault();
          var texto = document.getElementById('comentario').value.trim();
          if (!texto) { toast('Escribe un comentario'); return; }
          api('documentos/' + id + '/revisiones/', { method: 'POST', body: { comentario: texto } })
            .then(function () { toast('Revisión agregada'); pantallaDetalle(id); })
            .catch(function (e) { toast(e.message); });
        };
      }).catch(function (e) { c.innerHTML = errorConexion(e); });
  }

  function pantallaFormulario(id) {
    var c = marco(id ? 'Editar Documento' : 'Nuevo Documento', 'documentos', null, { atras: '#/documentos' });
    Promise.all([api('clasificaciones/'), id ? api('documentos/' + id + '/') : Promise.resolve(null)])
      .then(function (r) {
        var clasifs = r[0].results, d = r[1] || { titulo: '', descripcion: '', estado: 'activo', idClasificacion: '' };
        c.innerHTML =
          '<form class="card" id="form-doc" novalidate>' +
            '<div class="field"><label for="titulo">Título *</label><input id="titulo" maxlength="200" value="' + esc(d.titulo) + '"></div>' +
            '<div class="field"><label for="descripcion">Descripción</label><textarea id="descripcion">' + esc(d.descripcion || '') + '</textarea></div>' +
            '<div class="field"><label for="clasificacion">Clasificación *</label><select id="clasificacion"><option value="">Selecciona una clasificación</option>' +
              clasifs.map(function (k) {
                return '<option value="' + k.idClasificacion + '"' + (k.idClasificacion === d.idClasificacion ? ' selected' : '') + '>' + esc(k.nombreClasificacion) + '</option>';
              }).join('') + '</select></div>' +
            '<div class="field"><label for="estado">Estado</label><select id="estado">' +
              Object.keys(ESTADOS).map(function (k) { return '<option value="' + k + '"' + (k === d.estado ? ' selected' : '') + '>' + ESTADOS[k] + '</option>'; }).join('') +
            '</select></div>' +
            '<div class="error-box" id="error" hidden></div>' +
            '<button class="btn btn-primary" type="submit">Guardar</button>' +
          '</form>';
        document.getElementById('form-doc').onsubmit = function (ev) {
          ev.preventDefault();
          var cuerpo = {
            titulo: document.getElementById('titulo').value.trim(),
            descripcion: document.getElementById('descripcion').value.trim(),
            idClasificacion: parseInt(document.getElementById('clasificacion').value, 10),
            estado: document.getElementById('estado').value
          };
          var error = document.getElementById('error');
          if (!cuerpo.titulo || !cuerpo.idClasificacion) {
            error.textContent = 'El título y la clasificación son obligatorios';
            error.hidden = false;
            return;
          }
          api(id ? 'documentos/' + id + '/' : 'documentos/', { method: id ? 'PATCH' : 'POST', body: cuerpo })
            .then(function (doc) {
              toast(id ? 'Documento actualizado correctamente' : 'Documento creado correctamente');
              location.replace('#/documentos/' + doc.idDocumento);
            })
            .catch(function (e) { error.textContent = e.message; error.hidden = false; });
        };
      }).catch(function (e) { c.innerHTML = errorConexion(e); });
  }

  function pantallaHistorial() {
    var c = marco('Historial', 'historial');
    api('historial/').then(function (r) {
      c.innerHTML = r.results.map(function (h) {
        return '<div class="card"><div class="row"><span class="hist-accion">' + esc(h.accion) + '</span><span class="hist-fecha">' + fecha(h.fechaAccion) + '</span></div>' +
          '<div class="hist-doc">' + esc(h.documento_titulo) + '</div><div class="hist-user">' + esc(h.usuario_nombre) + '</div></div>';
      }).join('') || '<div class="empty">No hay elementos para mostrar</div>';
    }).catch(function (e) { c.innerHTML = errorConexion(e); });
  }

  function pantallaUsuarios() {
    var c = marco('Usuarios', 'usuarios');
    api('usuarios/').then(function (r) {
      c.innerHTML = r.results.map(function (u) {
        var iniciales = (u.nombre || '?').split(' ').map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase();
        return '<div class="card user-row"><div class="user-av">' + esc(iniciales) + '</div>' +
          '<div class="user-info"><div class="n">' + esc(u.nombre) + '</div><div class="c">' + esc(u.correo) + '</div></div>' +
          '<div class="user-tags"><div class="rol">' + esc(u.rol_nombre || 'Sin rol') + '</div>' +
          '<div class="est ' + esc(u.estado) + '">' + esc(u.estado === 'activo' ? 'Activo' : 'Inactivo') + '</div></div></div>';
      }).join('') || '<div class="empty">No hay elementos para mostrar</div>';
    }).catch(function (e) { c.innerHTML = errorConexion(e); });
  }

  // ---------- Navegación ----------
  function enrutar() {
    cerrarMenu();
    window.scrollTo(0, 0);
    var partes = location.hash.replace(/^#\/?/, '').split('/');
    var logueado = !!sesion.get('token');
    if (partes[0] === 'salir') { sesion.limpiar(); location.replace('#/login'); return; }
    if (!logueado) { if (partes[0] !== 'login') location.replace('#/login'); pantallaLogin(); return; }
    switch (partes[0]) {
      case 'documentos':
        if (partes[1] === 'nuevo') return pantallaFormulario(null);
        if (partes[1] && partes[2] === 'editar') return pantallaFormulario(partes[1]);
        if (partes[1]) return pantallaDetalle(partes[1]);
        return pantallaDocumentos();
      case 'historial': return pantallaHistorial();
      case 'usuarios': return pantallaUsuarios();
      case 'dashboard': return pantallaDashboard();
      default: location.replace('#/dashboard');
    }
  }

  window.addEventListener('hashchange', enrutar);
  enrutar();
})();
