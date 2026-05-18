# Estructura del Proyecto - Backend (CourseFlow)

Este documento detalla la arquitectura de directorios del backend de **CourseFlow**, diseñada específicamente para cumplir con los requerimientos de modularización, código limpio en inglés y el stack tecnológico (Python + PostgreSQL + Docker) solicitado para el proyecto pedagógico.

## Jerarquía de Directorios (Source Code)

Basado en la estructura de la aplicación, el código se organiza dentro del paquete principal `app/`:

```text
CourseFlow_Backend/
├──docs/
├── project/                    # Directorio raíz del código fuente (Source)
│   ├──instructions/           # Instrucciones de desarrollo
│      ├── deployment.md            # Manual de despliegue
│      ├── structure.md             # Estructura del proyecto
│      ├── testing.md             # Manual de pruebas
│      ├── workflow.md            # Manual de flujo
│   ├── stories/                 # Historias de usuario
│   ├── models/                 # Definición de la persistencia (BBDD)
│   │   ├── __init__.py         # Exportación de modelos
│   │   ├── application.py      # Tabla de inscripciones a cursos
│   │   ├── course.py           # Tabla de convocatorias y formación
│   │   └── user.py             # Tabla de usuarios y roles (Admin/User)
│   ├── routes/                 # Endpoints de la API REST (Controllers)
│   │   ├── __init__.py         # Registro de Blueprints/Routers
│   │   ├── applications.py     # Lógica de envío y gestión de solicitudes
│   │   ├── auth.py             # Lógica de registro y Login con JWT
│   │   └── courses.py          # Lógica del CRUD de cursos para alumnos/admins
│   ├── schemas/                # Validación y Serialización (DTOs)
│   │   ├── __init__.py
│   │   ├── application_schema.py
│   │   ├── course_schema.py
│   │   └── user_schema.py
│   ├── utils/                  # Herramientas transversales
│   │   └── decorators.py       # Decoradores de seguridad y validación de roles
│   ├── __init__.py             # Inicialización de la App y conexión BBDD
│   └── config.py               # Configuración de entornos y variables secretas
├── tests/                      # Suite de pruebas automatizadas (Pytest)
├── .env                        # Configuración sensible de entorno (No en Git)
├── .gitignore                  # Exclusión de archivos (pycache, .env, etc.)
├── deployment.md               # Manual de despliegue en producción
├── docker-compose.yml          # Orquestación de contenedores (API + PostgreSQL)
├── Dockerfile                  # Receta de construcción de la imagen de la API
├── requirements.txt            # Dependencias del backend
└── structure.md                # Este archivo: Guía de arquitectura