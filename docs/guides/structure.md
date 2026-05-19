# Estructura del Proyecto - Backend (CourseFlow)

Este documento detalla la arquitectura de directorios del backend de **CourseFlow**, diseñada específicamente para cumplir con los requerimientos de modularización, código limpio en inglés y el stack tecnológico (Python + PostgreSQL + Docker) solicitado para el proyecto pedagógico.

## Jerarquía de Directorios (Source Code)

Basado en el estado actual del repositorio, esta es la estructura de arquitectura backend:

```text
CourseFlow_Backend/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── alembic/
│       │   └── env_1.py
│       ├── api/
│       │   ├── deps.py
│       │   └── v1/
│       │       ├── routes_auth.py
│       │       ├── routes_users.py
│       │       ├── routes_courses.py
│       │       ├── routes_applications.py
│       │       └── routes_waiting_list.py
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── db/
│       │   ├── base.py
│       │   └── session.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── course.py
│       │   ├── application.py
│       │   └── waiting_list.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user_schema.py
│       │   ├── course_schema.py
│       │   ├── auth_schema.py
│       │   └── application_schema.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── courses.py
│       │   └── applications.py
│       └── utils/
│           ├── __init__.py
│           └── decorators.py
├── tests/
│   ├── conftest.py
│   ├── test_admin.py
│   ├── test_auth.py
│   ├── test_auth_middleware.py
│   ├── test_courses.py
│   ├── test_health.py
│   ├── test_users.py
│   └── test_applications.py
├── docs/
│   ├── assets/
│   │   ├── entity_relationship_diagram.png
│   │   ├── autenticacion.svg
│   │   ├── diagrama_general.svg
│   │   ├── solicitudes.svg
│   │   └── adminCursos.svg
│   ├── guides/
│   │   ├── deployment.md
│   │   ├── structure.md
│   │   ├── testing.md
│   │   └── workflow.md
│   ├── lineamientos/
│   │   ├── 5 - Proyecto Pedagogico_2026.pdf
│   │   └── Plataforma de Gestión de Cursos y Convocatorias-1.pdf
│   ├── stories/
│   │   ├── HU B+DVOPS/
│   │   └── HU BE/
│   ├── Proyecto_Pegagogico.md
│   ├── courseFlow.md
│   └── description.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .env.example
```