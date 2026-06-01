# Gestor Documental - Instrucciones de Instalación

## Estructura del Proyecto
```
proyecto/
├── backend/    → Django (web + API REST)
└── android/    → Android Studio (app móvil)
```

---

## 1. BACKEND DJANGO

### Requisitos
- Python 3.10+
- MySQL 8.0+
- pip

### Pasos

#### a) Crear la base de datos MySQL
Ejecuta el archivo SQL del proyecto:
```sql
-- En MySQL Workbench o consola:
source "Sistema-Gestor-Documental.sql"
```

#### b) Configurar el entorno
```bash
cd proyecto/backend

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### c) Configurar la BD en .env
Edita `backend/.env`:
```
DB_NAME=sistema_gestor_documental
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_HOST=localhost
DB_PORT=3306
```

#### d) Migrar y crear datos iniciales
```bash
python manage.py migrate
python setup_inicial.py
```

#### e) Iniciar el servidor
```bash
python manage.py runserver
```

Accede en: **http://localhost:8000**
- Login: `admin@gestordoc.com`
- Contraseña: `Admin2024*`

---

## 2. APP ANDROID

### Requisitos
- Android Studio Hedgehog (2023.1) o superior
- Java 17
- SDK Android API 26+

### Pasos

#### a) Abrir el proyecto
1. Abre Android Studio
2. Selecciona **File → Open**
3. Navega a `proyecto/android/`
4. Espera que sincronice Gradle

#### b) Configurar la URL del servidor
Edita `app/build.gradle`:
```gradle
// Si el servidor corre en tu PC y el emulador Android:
buildConfigField "String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/\""

// Si usas dispositivo físico (reemplaza con tu IP local):
buildConfigField "String", "API_BASE_URL", "\"http://192.168.1.X:8000/api/\""
```

#### c) Ejecutar
- Crea un emulador o conecta un dispositivo físico
- Clic en **Run ▶**

---

## API REST - Endpoints disponibles

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/auth/login/` | Login (retorna JWT) |
| POST | `/api/auth/refresh/` | Renovar token |
| GET | `/api/documentos/` | Listar documentos |
| POST | `/api/documentos/` | Crear documento |
| GET | `/api/documentos/{id}/` | Ver documento |
| PUT | `/api/documentos/{id}/` | Editar documento |
| DELETE | `/api/documentos/{id}/` | Eliminar |
| GET | `/api/documentos/{id}/historial/` | Historial |
| GET | `/api/documentos/{id}/revisiones/` | Revisiones |
| POST | `/api/documentos/{id}/revisiones/` | Agregar revisión |
| GET | `/api/clasificaciones/` | Clasificaciones |
| GET | `/api/usuarios/` | Usuarios |
| GET | `/api/usuarios/me/` | Usuario actual |
| GET | `/api/historial/` | Historial global |

---

## Módulos de la aplicación

| Módulo | Web | Android |
|--------|-----|---------|
| Login / Autenticación | ✅ | ✅ |
| Dashboard con estadísticas | ✅ | ✅ |
| Gestión de documentos (CRUD) | ✅ | ✅ |
| Búsqueda y filtros | ✅ | ✅ |
| Clasificaciones | ✅ | - |
| Gestión de usuarios | ✅ | ✅ (solo lectura) |
| Historial de actividad | ✅ | ✅ |
| Revisiones de documentos | ✅ | ✅ |
| API REST para Android | ✅ | — |

---

## Tecnologías usadas

**Backend/Web:**
- Django 4.2
- Django REST Framework
- JWT (Simple JWT)
- Bootstrap 5 + Bootstrap Icons
- MySQL

**Android:**
- Kotlin
- Material Design 3
- Retrofit 2 (HTTP)
- Coroutines
- ViewBinding
