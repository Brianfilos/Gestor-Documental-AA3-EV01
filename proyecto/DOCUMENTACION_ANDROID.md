# Documentación Técnica - App Android Gestor Documental

## Tabla de Contenidos
1. [Arquitectura General](#arquitectura-general)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Capa de Datos](#capa-de-datos)
4. [Autenticación y Sesión](#autenticación-y-sesión)
5. [Pantallas y Flujo de Navegación](#pantallas-y-flujo-de-navegación)
6. [Modelos de Datos](#modelos-de-datos)
7. [Endpoints de la API](#endpoints-de-la-api)
8. [Cómo se Conecta Android con el Backend](#cómo-se-conecta-android-con-el-backend)
9. [Dependencias](#dependencias)
10. [Configuración del Entorno](#configuración-del-entorno)

---

## 1. Arquitectura General

La app sigue una arquitectura simplificada de 2 capas:

```
┌─────────────────────────────────────────────┐
│               CAPA UI                        │
│  Activities  │  Fragments  │  Adapters       │
│  (Kotlin + ViewBinding + Coroutines)         │
└────────────────────┬────────────────────────┘
                     │ llamadas directas
┌────────────────────▼────────────────────────┐
│             CAPA DE DATOS                    │
│  RetrofitClient  │  ApiService  │ SessionMgr │
│  (Retrofit2 + OkHttp + GSON)                 │
└────────────────────┬────────────────────────┘
                     │ HTTP REST
┌────────────────────▼────────────────────────┐
│           BACKEND DJANGO (API REST)          │
│         http://10.0.2.2:8000/api/            │
└─────────────────────────────────────────────┘
```

> No usa ViewModel ni Repository pattern. Las Activities y Fragments hacen las llamadas
> a la API directamente usando coroutines (`lifecycleScope.launch`).

---

## 2. Estructura de Archivos

```
android/
├── build.gradle                        ← versiones globales
├── settings.gradle                     ← repositorios y plugins
└── app/
    ├── build.gradle                    ← dependencias y configuración de la app
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/gestordocumental/
        │   ├── data/
        │   │   ├── ApiService.kt       ← modelos de datos + interfaz Retrofit
        │   │   ├── RetrofitClient.kt   ← instancia singleton de Retrofit
        │   │   └── SessionManager.kt  ← gestión de tokens JWT y sesión
        │   └── ui/
        │       ├── LoginActivity.kt
        │       ├── MainActivity.kt
        │       ├── dashboard/
        │       │   ├── DashboardFragment.kt
        │       │   └── DocumentoResumenAdapter.kt
        │       ├── documentos/
        │       │   ├── DocumentosFragment.kt
        │       │   ├── DocumentoDetalleActivity.kt
        │       │   ├── DocumentoFormActivity.kt
        │       │   ├── DocumentosAdapter.kt
        │       │   └── RevisionesAdapter.kt
        │       ├── historial/
        │       │   ├── HistorialFragment.kt
        │       │   └── HistorialAdapter.kt
        │       └── usuarios/
        │           └── UsuariosFragment.kt  ← incluye UsuariosAdapter inline
        └── res/
            ├── layout/                 ← 14 archivos XML de interfaz
            ├── menu/nav_menu.xml       ← menú del Navigation Drawer
            └── values/
                ├── strings.xml
                ├── colors.xml
                └── themes.xml
```

---

## 3. Capa de Datos

### 3.1 RetrofitClient.kt — Cliente HTTP Singleton

Crea y expone una única instancia de Retrofit para toda la app.

```
RetrofitClient
├── OkHttpClient
│   ├── HttpLoggingInterceptor (nivel BODY — loguea todo en consola)
│   ├── connectTimeout: 30 segundos
│   ├── readTimeout:    30 segundos
│   └── writeTimeout:   30 segundos
├── GsonConverterFactory (serialización JSON ↔ Kotlin)
└── BaseUrl: BuildConfig.API_BASE_URL  (definida en build.gradle)
```

**Uso desde cualquier parte de la app:**
```kotlin
val api = RetrofitClient.instance
val respuesta = api.getDocumentos(token = sessionManager.getToken())
```

---

### 3.2 ApiService.kt — Interfaz de la API

Define todas las llamadas HTTP como funciones `suspend` (compatibles con coroutines).

Cada función es una llamada a un endpoint del backend Django.

---

### 3.3 SessionManager.kt — Gestión de Sesión

Almacena la sesión del usuario en `SharedPreferences` bajo la clave `gestor_prefs`.

| Clave almacenada   | Contenido                        |
|--------------------|----------------------------------|
| `access_token`     | Token JWT de acceso              |
| `refresh_token`    | Token JWT de refresco            |
| `user_id`          | ID del usuario autenticado       |
| `user_name`        | Nombre del usuario               |
| `user_email`       | Correo electrónico               |
| `user_rol`         | Rol del usuario (admin/empleado) |

**Métodos principales:**

| Método             | Descripción                                 |
|--------------------|---------------------------------------------|
| `saveSession()`    | Guarda tokens y datos de usuario            |
| `getToken()`       | Retorna `"Bearer {access_token}"`           |
| `isLoggedIn()`     | `true` si hay token guardado                |
| `clearSession()`   | Borra todo (logout)                         |

---

## 4. Autenticación y Sesión

### Flujo de Login

```
Usuario escribe correo + contraseña
        │
        ▼
LoginActivity llama: POST /api/auth/login/
        │
        ├─ Éxito → SessionManager.saveSession(response)
        │          → navega a MainActivity
        │
        └─ Error  → muestra mensaje de error en pantalla
```

### Flujo de Sesión Persistente

Cuando la app abre `LoginActivity`, verifica:
```kotlin
if (sessionManager.isLoggedIn()) {
    startActivity(Intent(this, MainActivity::class.java))
    finish()  // no muestra el login si ya hay sesión
}
```

### Uso del Token en cada Request

Cada llamada autenticada envía el token en el header HTTP:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Se obtiene así:
```kotlin
val token = sessionManager.getToken()  // retorna "Bearer {token}"
api.getDocumentos(token = token)
```

### Logout

Al cerrar sesión desde el menú:
```kotlin
sessionManager.clearSession()
startActivity(Intent(this, LoginActivity::class.java))
finish()
```

---

## 5. Pantallas y Flujo de Navegación

### Mapa de Navegación

```
LoginActivity
    │
    └──► MainActivity (Navigation Drawer)
             │
             ├──► DashboardFragment        (pantalla inicial)
             │
             ├──► DocumentosFragment
             │        │
             │        ├──► DocumentoDetalleActivity  (ver documento)
             │        │        └── RevisionesAdapter
             │        │        └── HistorialAdapter (historial del doc)
             │        │
             │        └──► DocumentoFormActivity  (crear / editar)
             │                 └── Dropdown de clasificaciones
             │
             ├──► HistorialFragment         (historial global)
             │
             └──► UsuariosFragment          (lista de usuarios)
```

---

### Descripción de cada pantalla

#### LoginActivity
- Entrada principal de la app
- Campos: correo electrónico y contraseña
- Si ya hay sesión guardada, salta directo a `MainActivity`
- Llama: `POST /api/auth/login/`

---

#### MainActivity
- Contenedor principal con **Navigation Drawer** lateral
- Aloja los 4 fragments mediante el componente Navigation
- Gestiona el logout desde el menú
- Muestra el nombre y correo del usuario en el drawer

---

#### DashboardFragment
- Estadísticas generales del sistema
- Tarjetas con: total de documentos, documentos activos, total de usuarios
- Lista de documentos recientes
- Llama: `GET /api/documentos/` y `GET /api/usuarios/`

---

#### DocumentosFragment
- Lista paginada de todos los documentos
- Soporte **pull-to-refresh** para recargar
- Botón FAB (+) para crear nuevo documento
- Al tocar un documento abre `DocumentoDetalleActivity`
- Llama: `GET /api/documentos/`

---

#### DocumentoDetalleActivity
- Muestra toda la información de un documento
- Pestañas o secciones: datos, historial de cambios, revisiones/comentarios
- Botón para editar (abre `DocumentoFormActivity`)
- Botón para eliminar (con confirmación)
- Input para agregar nuevo comentario/revisión
- Llama: `GET /api/documentos/{id}/`, `GET /api/documentos/{id}/historial/`,
  `GET /api/documentos/{id}/revisiones/`, `POST /api/documentos/{id}/revisiones/`

---

#### DocumentoFormActivity
- Formulario para crear o editar un documento
- Campos: título, descripción, estado, clasificación (dropdown)
- Las clasificaciones se cargan al abrir la pantalla
- En modo edición, prellenado con los datos existentes
- Llama: `GET /api/clasificaciones/`, `POST /api/documentos/`, `PUT /api/documentos/{id}/`

---

#### HistorialFragment
- Historial global de todas las acciones del sistema
- Pull-to-refresh
- Muestra: acción, usuario, documento afectado, fecha
- Llama: `GET /api/historial/`

---

#### UsuariosFragment
- Lista de todos los usuarios del sistema (solo lectura)
- Muestra: nombre, correo, rol, estado
- Llama: `GET /api/usuarios/`

---

## 6. Modelos de Datos

Todos los modelos están definidos en `ApiService.kt` como `data class` de Kotlin.
GSON los convierte automáticamente desde/hacia JSON.

### Autenticación

```kotlin
data class LoginRequest(
    val correo: String,
    val password: String
)

data class LoginResponse(
    val access: String,       // token JWT de acceso
    val refresh: String,      // token JWT de refresco
    val usuario: UsuarioInfo
)

data class UsuarioInfo(
    val id: Int,
    val nombre: String,
    val correo: String,
    val rol: String
)
```

### Documentos

```kotlin
data class Documento(
    val idDocumento: Int,
    val titulo: String,
    val descripcion: String?,
    val fechaCarga: String,
    val estado: String,          // "activo", "inactivo", "archivado"
    val archivo: String?,
    val idUsuario: Int,
    val usuario_nombre: String,
    val idClasificacion: Int?,
    val clasificacion_nombre: String?
)
```

### Clasificaciones

```kotlin
data class Clasificacion(
    val idClasificacion: Int,
    val nombreClasificacion: String,
    val descripcion: String?
)
```

### Usuarios

```kotlin
data class Usuario(
    val idUsuario: Int,
    val nombre: String,
    val correo: String,
    val estado: String,
    val idRol: Int,
    val rol_nombre: String
)
```

### Historial

```kotlin
data class Historial(
    val idHistorial: Int,
    val idDocumento: Int,
    val documento_titulo: String,
    val idUsuario: Int,
    val usuario_nombre: String,
    val accion: String,          // "creación", "edición", "eliminación"
    val fechaAccion: String
)
```

### Revisiones

```kotlin
data class Revision(
    val idRevision: Int,
    val idDocumento: Int,
    val idUsuario: Int,
    val usuario_nombre: String,
    val fechaRevision: String,
    val comentario: String
)
```

### Respuesta Paginada

```kotlin
data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>
)
```

---

## 7. Endpoints de la API

| Método | Endpoint                              | Descripción                    | Auth |
|--------|---------------------------------------|--------------------------------|------|
| POST   | `/api/auth/login/`                    | Login, retorna tokens JWT      | No   |
| POST   | `/api/auth/refresh/`                  | Renovar access token           | No   |
| GET    | `/api/documentos/`                    | Listar documentos (paginado)   | Si   |
| GET    | `/api/documentos/{id}/`               | Ver un documento               | Si   |
| POST   | `/api/documentos/`                    | Crear documento                | Si   |
| PUT    | `/api/documentos/{id}/`               | Editar documento               | Si   |
| DELETE | `/api/documentos/{id}/`               | Eliminar documento             | Si   |
| GET    | `/api/documentos/{id}/historial/`     | Historial de cambios del doc   | Si   |
| GET    | `/api/documentos/{id}/revisiones/`    | Revisiones/comentarios del doc | Si   |
| POST   | `/api/documentos/{id}/revisiones/`    | Agregar revisión/comentario    | Si   |
| GET    | `/api/clasificaciones/`               | Listar clasificaciones         | Si   |
| GET    | `/api/usuarios/`                      | Listar usuarios                | Si   |
| GET    | `/api/usuarios/me/`                   | Usuario autenticado actual     | Si   |
| GET    | `/api/historial/`                     | Historial global del sistema   | Si   |

---

## 8. Cómo se Conecta Android con el Backend

### Diagrama completo de una llamada

```
Fragment/Activity
    │
    │  lifecycleScope.launch { ... }      ← coroutine (hilo secundario)
    │
    ├─ sessionManager.getToken()          ← lee "Bearer xxx" de SharedPreferences
    │
    ├─ RetrofitClient.instance            ← obtiene el singleton Retrofit
    │       └── ApiService (interfaz)
    │               └── función suspend  ← Kotlin suspend function
    │
    │                    HTTP Request
    │            ┌────────────────────────────────┐
    │            │  GET /api/documentos/           │
    │            │  Host: 10.0.2.2:8000            │
    │            │  Authorization: Bearer eyJ...   │
    │            └────────────────────────────────┘
    │                           │
    │                    Backend Django
    │                    JWT verifica token
    │                    Consulta MySQL
    │                    Retorna JSON
    │
    │            ┌────────────────────────────────┐
    │            │  HTTP 200 OK                    │
    │            │  Content-Type: application/json │
    │            │  { "count": 5, "results": [...]}│
    │            └────────────────────────────────┘
    │
    ├─ GSON deserializa JSON → PaginatedResponse<Documento>
    │
    └─ withContext(Dispatchers.Main) {    ← regresa al hilo principal
           adapter.submitList(docs)       ← actualiza la UI
       }
```

### Patrón de llamada en código

Todas las llamadas siguen esta estructura:

```kotlin
lifecycleScope.launch {
    try {
        val token = sessionManager.getToken()
        val response = RetrofitClient.instance.getDocumentos(token = token)
        // actualizar UI con los datos
        adapter.submitList(response.results)
    } catch (e: Exception) {
        // mostrar error al usuario
        Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
    }
}
```

### Dirección IP del backend

| Escenario                   | URL base                          |
|-----------------------------|-----------------------------------|
| Emulador Android (en la PC) | `http://10.0.2.2:8000/api/`       |
| Dispositivo físico (WiFi)   | `http://192.168.1.X:8000/api/`    |

> `10.0.2.2` es la IP especial que el emulador Android usa para referirse
> a `localhost` de la máquina host donde corre Android Studio.

La URL se configura en `app/build.gradle`:
```gradle
defaultConfig {
    buildConfigField "String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/\""
}
```

---

## 9. Dependencias

| Librería                      | Versión    | Para qué se usa                            |
|-------------------------------|------------|--------------------------------------------|
| `androidx.appcompat`          | 1.6.1      | Compatibilidad Material Design             |
| `material`                    | 1.11.0     | Componentes Material Design 3              |
| `androidx.navigation`         | 2.7.6      | Navegación entre fragments                 |
| `androidx.lifecycle`          | 2.7.0      | ViewModel y LiveData (importado, sin uso)  |
| `retrofit2`                   | 2.9.0      | Cliente HTTP para la API REST              |
| `converter-gson`              | 2.9.0      | Serialización JSON con GSON                |
| `okhttp3`                     | 4.12.0     | Capa HTTP de bajo nivel + logging          |
| `logging-interceptor`         | 4.12.0     | Logs de requests/responses HTTP            |
| `kotlinx-coroutines-android`  | 1.7.3      | Llamadas asíncronas con `suspend`          |
| `androidx.security:crypto`    | 1.1.0-alpha | SharedPreferences encriptado              |

---

## 10. Configuración del Entorno

### Requisitos

- **Android Studio** Hedgehog (2023.1) o superior
- **Java 17**
- **SDK Android API 26+** (Android 8.0 Oreo)
- Backend Django corriendo en `http://localhost:8000`

### Configuración de la SDK

```gradle
// app/build.gradle
android {
    compileSdk 34
    defaultConfig {
        minSdk 26        // Android 8.0 mínimo
        targetSdk 34     // Android 14
    }
}
```

### Paso a paso para ejecutar

1. Abrir Android Studio → **File → Open** → seleccionar carpeta `proyecto/android/`
2. Esperar sincronización de Gradle
3. Iniciar el backend Django: `python manage.py runserver`
4. Verificar la URL en `app/build.gradle` (ver sección 8)
5. Crear emulador API 26+ o conectar dispositivo físico
6. Presionar **Run ▶** (Shift+F10)

### Credenciales de prueba

```
Correo:     admin@gestordoc.com
Contraseña: Admin2024*
```
