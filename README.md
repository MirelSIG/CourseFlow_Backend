README – Backend CourseFlow (FastAPI + PostgreSQL + Alembic + Docker)
1. Introducción
Este backend implementa la API del proyecto CourseFlow, una plataforma para gestionar cursos, solicitudes de inscripción y listas de espera.
Está construido con:
• FastAPI (framework principal)
• SQLAlchemy (ORM)
• PostgreSQL (base de datos)
• Alembic (migraciones)
• Docker + docker‑compose (entorno reproducible)
• JWT (autenticación)
• Arquitectura modular y escalable
La estructura está adaptada a las necesidades del bootcamp y a la organización real del equipo.
---
2. Estructura del proyecto
Esta es la estructura actual del repositorio backend:

```text
CourseFlow_Backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── alembic/
│   │   └── env_1.py
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── routes_auth.py
│   │       ├── routes_users.py
│   │       ├── routes_courses.py
│   │       ├── routes_applications.py
│   │       └── routes_waiting_list.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── application.py
│   │   └── waiting_list.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── course_schema.py
│   │   ├── auth_schema.py
│   │   └── application_schema.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── courses.py
│   │   └── applications.py
│   └── utils/
│       ├── __init__.py
│       └── decorators.py
├── tests/
│   └── test_health.py
├── docs/
├── project/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .env.example
```

3. Explicación de cada carpeta
`app/main.py`
Punto de entrada de FastAPI.
Aquí se inicializa la app, CORS y se incluyen las rutas.
---
`app/api/`
Contiene toda la lógica de la API.
`api/deps.py`
Dependencias comunes, como la sesión de DB (get_db()).
`api/v1/`
Rutas organizadas por módulo:

| Archivo | Función |
|---------|----------|
| routes_auth.py | Login, JWT |
| routes_users.py | Registro y gestión de usuarios |
| routes_courses.py | CRUD de cursos |
| routes_applications.py | Solicitudes de inscripción |
| routes_waiting_list.py | Lista de espera |

`app/models/`
Modelos SQLAlchemy que representan las tablas:
• user.py
• course.py
• application.py
• waiting_list.py
El archivo models/__init__.py importa todos los modelos para que Alembic pueda detectarlos.
---
`app/schemas/`
Schemas Pydantic usados para:
• Validar datos de entrada
• Formatear respuestas
• Documentar la API
Tus nombres personalizados:

| Archivo | Contenido |
|---------|----------|
| user_schema.py | UserCreate, UserRead |
| auth_schema.py | LoginRequest, TokenResponse |
| course_schema.py | CourseCreate, CourseRead |
| application_schema.py | ApplicationCreate, ApplicationRead |
| waiting_list_schema.py | WaitingListCreate, WaitingListRead |

`app/core/`
Configuración central del backend.
`core/config.py`
Carga variables de entorno y configuración general.
`core/security.py`
Funciones de seguridad:
• Hash de contraseñas
• Verificación
• Generación de JWT
---
`app/db/`
Conexión a la base de datos.
`session.py`
Crea el engine y la sesión SQLAlchemy.
`base.py`
Define la clase Base para todos los modelos.
---
`app/alembic/env_1.py`
Este archivo es la configuración de Alembic.
• Lo creó Alembic automáticamente
• Tú lo editaste para conectar migraciones con tus modelos
• Es el “cerebro” que permite generar migraciones
---
`app/routes/`
Carpeta creada por tu compañero.
Actualmente no se usa, porque las rutas reales están en api/v1/.
Puedes:
• Eliminarla
• O usarla para rutas internas no versionadas
---
`app/utils/`
Funciones auxiliares.
decorators.py está vacío por ahora.
---
`tests/`
Pruebas automáticas con pytest.
test_health.py verifica que la API responde.
---
4. Base de datos y migraciones (Alembic)
¿Qué es Alembic?
Sistema de migraciones para SQLAlchemy.
¿Dónde está configurado?
En:
app/alembic/env_1.py
¿Cómo generar una migración?**
alembic revision -m "init"
Esto crea un nuevo archivo de migración en app/alembic/versions/.
¿Cómo aplicar migraciones?**
alembic upgrade head
Esto actualiza la base de datos al último estado definido por las migraciones.

### Modelo Relacional de Datos

El sistema utiliza un esquema relacional donde los **Usuarios** se inscriben en **Cursos** a través de **Solicitudes** (Applications). Además, existe una **Lista de Espera** para gestionar el cupo de los cursos cuando la capacidad se agota.

#### Diagrama Entidad-Relación (ERD)

```mermaid
erDiagram
    USERS ||--o{ APPLICATIONS : "realiza"
    USERS ||--o{ WAITING_LIST : "está en"
    COURSES ||--o{ APPLICATIONS : "recibe"
    COURSES ||--o{ WAITING_LIST : "tiene"

    USERS {
        int id PK
        string name
        string email
        string password
        enum role "user, admin, superadmin"
        datetime created_at
        datetime updated_at
    }
    COURSES {
        int id PK
        string name
        text description
        date start_date
        date end_date
        int capacity
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    APPLICATIONS {
        int id PK
        int user_id FK
        int course_id FK
        enum status "pending, accepted, rejected, cancelled"
        datetime created_at
        datetime updated_at
    }
    WAITING_LIST {
        int id PK
        int user_id FK
        int course_id FK
        int position
        datetime created_at
    }
```

#### Descripción de las Relaciones

*   **Usuarios <-> Solicitudes (1:N):** Un usuario puede tener múltiples solicitudes (una por curso), pero cada solicitud pertenece a un único usuario.
*   **Cursos <-> Solicitudes (1:N):** Un curso puede recibir múltiples solicitudes de inscripción, pero cada solicitud está vinculada a un único curso.
*   **Relación Muchos a Muchos (M:N):** Los usuarios y los cursos están relacionados indirectamente a través de la tabla `applications`, que actúa como tabla de unión con metadatos adicionales (el estado de la inscripción).
*   **Lista de Espera:** Vincula usuarios con cursos cuando el cupo está lleno, manteniendo un orden secuencial mediante el campo `position`.
5. Docker y docker-compose
Levantar todo el backend:
```bash
sudo docker compose up --build -d
```
Esto construye la imagen, levanta PostgreSQL, ejecuta las migraciones automáticamente (vía entrypoint) y levanta el contenedor con FastAPI.

Servicios incluidos y puertos expuestos:
• **backend** → FastAPI (http://localhost:8000/docs)
• **db** → PostgreSQL (Puerto externo: 5432)
• **pgadmin** → Interfaz visual para base de datos (http://localhost:5051)
  - **Usuario:** `admin@admin.com`
  - **Contraseña:** `admin`

Poblar la base de datos (Seed):
Para insertar datos de prueba iniciales (administradores, usuarios, cursos y solicitudes), ejecuta:
```bash
sudo docker compose exec backend python scripts/seed.py
```

### 🛠️ Configuración de Conexión en pgAdmin (Paso a Paso)
Una vez que ingreses a PgAdmin a través de `http://localhost:5051` (o el enlace de IDX) usando las credenciales por defecto, sigue estos pasos para conectarte a la base de datos del proyecto:

1. Haz clic derecho en **Servers** -> **Register** -> **Server...**
2. En la pestaña **General**:
   - **Name:** Escribe `CourseFlow DB` (o el nombre que prefieras).
3. En la pestaña **Connection**:
   - **Host name/address:** Escribe `db` *(este es el nombre del servicio de la base de datos en docker-compose, que Docker resolverá internamente)*.
   - **Port:** `5432`
   - **Maintenance database:** `courseflow_db`
   - **Username:** `courseflow`
   - **Password:** `courseflow`
4. Haz clic en **Save** (Guardar).
¡Listo! Ya podrás explorar las tablas de usuarios, cursos y solicitudes creadas por las migraciones de Alembic e inspeccionar los datos iniciales.

  6. Autenticación (JWT)
El flujo:
1. Usuario se registra (POST /api/v1/users)
2. Usuario inicia sesión (POST /api/v1/auth/login)
3. El backend genera un JWT
4. El frontend lo guarda y lo envía en cada petición.

 7. Endpoints principales

| Módulo | Método | Endpoint |
|--------|--------|----------|
| Usuarios | POST | /api/v1/users |
| Usuarios | GET | /api/v1/users/{id} |
| Auth | POST | /api/v1/auth/login |
| Cursos | POST | /api/v1/courses |
| Cursos | GET | /api/v1/courses |
| Cursos | GET | /api/v1/courses/{id} |
| Solicitudes | POST | /api/v1/applications |
| Solicitudes | GET | /api/v1/applications |
| Solicitudes | GET | /api/v1/applications/{id} |
| Lista de espera | POST | /api/v1/waiting_list |
| Lista de espera | GET | /api/v1/waiting_list |
| Lista de espera | GET | /api/v1/waiting_list/{id} |
| Lista de espera | GET | /api/v1/waiting-list/{course_id} |

---
8. Testing
El proyecto cuenta con una suite completa de pruebas unitarias y de integración que validan el comportamiento lógico y la seguridad de las API.

### Comando para ejecutar las pruebas:
Para ejecutar la suite completa de pruebas unitarias y de integración de la forma más rápida y sencilla, ejecuta este comando en tu terminal:

```bash
venv/bin/pytest
```


### Tipos de pruebas ejecutadas:
La suite consta de 19 tests divididos en módulos lógicos específicos:

1. **Autenticación y Registro (`tests/test_auth.py`):**
   - **Registro de usuarios:** Valida la creación de usuarios con contraseñas encriptadas de forma segura.
   - **Login de usuarios:** Comprueba que las credenciales válidas devuelvan una cookie JWT segura (`HttpOnly`).
   - **Credenciales inválidas:** Verifica la denegación correcta de accesos no autorizados.

2. **Middleware y Roles (`tests/test_auth_middleware.py`):**
   - **Control de Roles:** Verifica la jerarquía estricta de permisos (`User` < `Admin` < `Superadmin`).
   - **Acceso Restringido:** Valida que los endpoints protegidos devuelvan error `401 Unauthorized` si no se presenta un token.
   - **Bloqueo de Roles:** Garantiza que los usuarios normales no puedan invocar operaciones administrativas (error `403 Forbidden`).

3. **Gestión de Cursos (`tests/test_courses.py`):**
   - **Creación, Lectura, Actualización y Borrado (CRUD):** Garantiza que las operaciones CRUD guarden los datos correctamente en la base de datos de pruebas (SQLite en memoria).
   - **Reglas de negocio (Fechas):** Asegura que no se puedan crear cursos donde la fecha de fin sea menor que la de inicio (`end_date > start_date`).
   - **Borrado Lógico:** Comprueba que la eliminación de un curso no lo borre físicamente, sino que marque `is_active = False` para no romper el historial de solicitudes históricas.
   - **Listas filtradas:** Valida que los administradores puedan ver cursos inactivos en las búsquedas, pero los estudiantes solo los cursos activos.

4. **Chequeo de Salud (`tests/test_health.py`):**
   - **Disponibilidad:** Valida que la ruta de documentación autogenerada (`/docs`) responda con `200 OK` demostrando que el servidor FastAPI está arriba y listo.

9. Flujo general del backend
1. FastAPI recibe la petición
2. La ruta correspondiente valida datos con schemas
3. Se abre una sesión de DB con deps.get_db()
4. Se ejecuta la lógica usando models SQLAlchemy
5. Se devuelve la respuesta formateada con schemas
6. Alembic mantiene la BD sincronizada
7. Docker garantiza que todo funcione igual en todos los equipos
---
10. Cómo extender el proyecto
Puedes añadir:
• Roles avanzados
• Estados de solicitud
• Promoción automática desde lista de espera
• Notificaciones por email
• Dashboard admin
La arquitectura ya está preparada para crecer.
---
11. Conclusión
Este README explica:
• Cómo está organizado el backend
• Qué hace cada archivo
• Cómo se conectan FastAPI, SQLAlchemy, Alembic y Docker
• Cómo levantar el proyecto
• Cómo ejecutar migraciones y tests