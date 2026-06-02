# Estructura del Proyecto - Backend (CourseFlow)

Este documento detalla la arquitectura de directorios del backend de **CourseFlow**, diseñada específicamente para cumplir con los requerimientos de modularización, código limpio en inglés y el stack tecnológico (Python + PostgreSQL + Docker) solicitado para el proyecto pedagógico.

## Jerarquía de Directorios (Source Code)

Basado en el estado actual del repositorio, esta es la estructura de arquitectura backend:

```text
CourseFlow_Backend/
├── src/                          # Código fuente del proyecto
│   └── app/                      # Aplicación principal FastAPI
│       ├── __init__.py
│       ├── main.py               # Punto de entrada de FastAPI
│       ├── config.py             # Configuración heredada
│       ├── alembic/              # Directorio de configuración de Alembic
│       │   └── env_1.py          # Script de entorno de migraciones
│       ├── api/                  # Controladores y endpoints de la API
│       │   ├── deps.py           # Dependencias comunes (ej. get_db)
│       │   └── v1/               # Versión 1 de la API REST
│       │       ├── routes_auth.py       # Rutas de login y logout con JWT
│       │       ├── routes_users.py      # Rutas de registro y perfil de usuarios
│       │       ├── routes_courses.py    # Rutas de CRUD de cursos
│       │       ├── routes_applications.py # Rutas de solicitudes de inscripción
│       │       └── routes_waiting_list.py # Rutas de la lista de espera
│       ├── core/                 # Configuración de seguridad y entorno
│       │   ├── config.py         # Carga de variables de entorno (.env)
│       │   └── security.py       # Utilidades de seguridad (hashing y JWT)
│       ├── db/                   # Inicialización de la base de datos
│       │   ├── base.py           # Base declarativa de SQLAlchemy
│       │   └── session.py        # Configuración del engine y sessionmaker
│       ├── models/               # Modelos SQLAlchemy (Base de Datos)
│       │   ├── __init__.py
│       │   ├── user.py           # Entidad y relaciones de usuarios
│       │   ├── course.py         # Entidad y relaciones de cursos
│       │   ├── application.py    # Entidad de solicitudes de cursos
│       │   └── waiting_list.py   # Entidad de lista de espera
│       ├── schemas/              # Esquemas de validación Pydantic
│       │   ├── __init__.py
│       │   ├── user_schema.py    # Validación de datos de usuarios
│       │   ├── course_schema.py  # Validación de datos de cursos
│       │   ├── auth_schema.py    # Validación de credenciales y tokens
│       │   └── application_schema.py # Validación de solicitudes de cursos
│       ├── routes/               # Rutas heredadas (sin uso actual)
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── courses.py
│       │   └── applications.py
│       └── utils/                # Utilidades y funciones auxiliares
│           ├── __init__.py
│           └── decorators.py     # Decoradores personalizados
├── tests/                        # Suite de pruebas unitarias e integración
│   ├── conftest.py               # Fixtures globales de pytest
│   ├── test_admin.py             # Pruebas de rutas de administración
│   ├── test_auth.py              # Pruebas del flujo de autenticación
│   ├── test_auth_middleware.py   # Pruebas de roles y middleware
│   ├── test_courses.py           # Pruebas del CRUD de cursos
│   ├── test_health.py            # Prueba de salud/disponibilidad del servidor
│   ├── test_users.py             # Pruebas de perfiles de usuario
│   └── test_applications.py      # Pruebas de solicitudes de inscripción
├── docs/                         # Documentación organizada del proyecto
│   ├── assets/                   # Diagramas generales y de secuencia (SVG/PNG)
│   ├── guides/                   # Guías de despliegue, estructura y testing
│   ├── lineamientos/             # PDFs de lineamientos del bootcamp
│   └── stories/                  # Historias de usuario del backlog
├── Dockerfile                    # Receta de la imagen Docker de la API
├── docker-compose.yml            # Orquestación de servicios (FastAPI + Postgres)
├── requirements.txt              # Dependencias del backend
├── README.md                     # Documentación principal del repositorio
└── .env.example                  # Plantilla para variables de entorno
```