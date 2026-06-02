# CourseFlow Backend

CourseFlow – Plataforma de Gestión de Cursos y Convocatorias

## 1. Introducción

El presente proyecto consiste en el desarrollo de una aplicación web fullstack orientada a la gestión
de cursos y solicitudes de participación en entornos formativos y sociales, como SomosF5. La herramienta
busca centralizar la información de cursos, facilitar la gestión de participantes y simplificar el proceso
de inscripción.

## 2. Objetivo del proyecto

Desarrollar un MVP que permita:

- Gestionar cursos de forma centralizada
- Permitir solicitudes de inscripción por parte de usuarios
- Facilitar la gestión de participantes por parte del administrador

## 3. Alcance (MVP)

- Autenticación y roles (usuario, administrador)
- CRUD de cursos
- Envío y gestión de solicitudes de inscripción
- Panel de administración con listados y acciones sobre solicitudes

## 4. Funcionamiento básico

1. El usuario visualiza cursos disponibles
2. El usuario solicita participación
3. El administrador revisa solicitudes
4. El administrador acepta o rechaza usuarios

## 5. Documentación relevante

Archivos y rutas clave:

- `src/app/models/application.py` — modelo `Application` (tabla `applications`)
- `src/app/schemas/application_schema.py` — esquemas Pydantic para solicitudes
- `src/app/api/v1/routes_applications.py` — endpoints relacionados con solicitudes
- `src/app/utils/excel.py` — utilidad que genera el XLSX en memoria (si está presente)

## 6. Exportación a Excel (cambio incorporado)

Se añadió una funcionalidad para exportar el listado de solicitudes desde el backend.

Endpoint:

`GET /api/v1/applications/export/excel`

Devuelve un archivo `.xlsx` con las columnas principales de las solicitudes. El archivo se entrega con cabecera
`Content-Disposition` y nombre sugerido `solicitudes_YYYY-MM-DD.xlsx`.

Nota: este README ha sido restaurado desde la documentación del proyecto y se agregó únicamente la nota de
exportación para reflejar el cambio mínimo que se incorporó.

## 7. Cómo ejecutar (resumen rápido)

1. Crear o activar el entorno virtual (ej.: `python -m venv .venv` y `source .venv/bin/activate`).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Configurar variables de entorno si aplica (examinar `src/app/core/config.py`).
4. Ejecutar la aplicación: `uvicorn src.app.main:app --reload --port 8001`.

Para más detalles ver la carpeta `docs/` y `project/`.
