Resumen: el papel de cada tecnología en CourseFlow

Antes de entrar al código, es útil entender el rol de cada pieza del ecosistema.

🟦 FastAPI — La capa HTTP

FastAPI:

- Recibe peticiones HTTP y expone endpoints REST.
- Valida datos con Pydantic.
- Gestiona dependencias con `Depends`.
- Genera documentación automática (Swagger / ReDoc).
- Maneja middlewares, CORS, cookies y encabezados.

En CourseFlow, FastAPI:

- Recibe rutas como `/api/v1/auth/login`.
- Valida el JSON de entrada.
- Llama a la lógica de negocio.
- Devuelve un JWT o un error.

Es la capa de presentación del backend.

🟦 PostgreSQL — Almacén de datos

PostgreSQL:

- Base de datos relacional para usuarios, cursos, solicitudes y listas de espera.
- Persistente, transaccional y adecuada para relaciones 1:N y N:M.

En CourseFlow guarda:

- Usuarios (incluyendo `password_hash`).
- Cursos (con capacidad).
- Solicitudes (con estado).
- Listas de espera (con posición).

Es la capa de persistencia.

🟦 SQLAlchemy — Acceso a datos

SQLAlchemy es el ORM que:

- Mapea clases Python a tablas SQL.
- Convierte objetos Python en filas de la base de datos.
- Permite construir consultas sin escribir SQL crudo.

En CourseFlow:

- `User`, `Course`, `Application` y `WaitingList` son modelos SQLAlchemy.
- `SessionLocal()` abre sesiones transaccionales.
- `db.add()`, `db.query()`, `db.commit()` gestionan las operaciones.

Es la capa de acceso a datos.

🟦 Alembic — Migraciones

Alembic:

- Gestiona migraciones y versiones del esquema de BD.
- Permite evolucionar el esquema sin pérdida de datos.

En CourseFlow:

- Cada cambio en modelos suele ir acompañado de una migración versionada.
- `alembic upgrade head` aplica las migraciones pendientes.

Es la capa de evolución del esquema.

🟦 Docker — Reproducibilidad

Docker:

- Empaqueta el backend en contenedores aislados.
- Asegura consistencia entre entornos.
- Orquesta servicios con `docker-compose`.

En CourseFlow suele haber contenedores para FastAPI y PostgreSQL (opcional: pgAdmin).

Es la capa de infraestructura.

🟦 Python — Lenguaje principal

Python:

- Lenguaje en el que se implementa la API, la lógica de negocio, scripts y tests.
- Dinámico, expresivo y con rápido ciclo de desarrollo.

En CourseFlow, la lógica, la API y los tests están en Python.

Es la capa de ejecución.

---

2. Punto de arranque: `main.py`

En un proyecto FastAPI, `main.py` inicia la aplicación. En CourseFlow, suele:

1. Crear la instancia de `FastAPI`:

```python
app = FastAPI(...)
```

2. Configurar CORS para permitir llamadas desde el frontend (Vue, React, etc.).

3. Incluir rutas versionadas, por ejemplo:

```python
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1/users")
app.include_router(courses_router, prefix="/api/v1/courses")
```

4. Configurar eventos de inicio (lifespan):

- Creación automática del superadmin.
- Inicialización de la base de datos.
- Carga de variables de entorno.

5. Exponer la documentación en `/docs` y `/redoc`.

6. Punto de entrada para `uvicorn`:

```bash
uvicorn app.main:app --reload
```

---

3. Qué revisar después de `main.py`

El orden recomendado para explorar el backend es:

A) Dependencias (`deps.py`)

- `get_db()` — abre una sesión SQLAlchemy.
- `get_current_user()` — valida el JWT.
- `require_role()` — control de roles.
- `verify_token_not_revoked()` — comprobación de blacklist.

B) Seguridad (`security.py`)

- `hash_password()` / `verify_password()`.
- `create_access_token()` / `decode_token()`.
- `generate_jti()`.

C) Modelos SQLAlchemy

- `user.py`, `course.py`, `application.py`, `waiting_list.py`.

D) Schemas Pydantic

- Validan la entrada, formatean la salida y documentan la API.

E) Rutas

- `routes_auth.py`, `routes_users.py`, `routes_courses.py`, `routes_applications.py`, `routes_waiting_list.py`.

F) Tests

- Validan autenticación, roles, CRUD, seguridad e integridad de la BD.

---

Si quieres, puedo:

- Añadir una tabla de contenidos.
- Acortar o resumir secciones para un README más breve.
- Añadir ejemplos de comandos frecuentes.

Di qué prefieres y continúo.