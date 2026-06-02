# CourseFlow Backend

Backend de CourseFlow para autenticación, cursos y gestión de solicitudes de inscripción.

## Funcionalidades

- Autenticación y roles de usuario.
- CRUD de cursos.
- Gestión de solicitudes de inscripción.
- Exportación de solicitudes a Excel desde el panel de administración.

## Exportación Excel

El backend expone el endpoint:

`GET /api/v1/applications/export/excel`

Genera un archivo `.xlsx` con el listado de solicitudes y se descarga con el nombre `solicitudes_YYYY-MM-DD.xlsx`.

## Estructura relevante

- `src/app/api/v1/routes_applications.py`
- `src/app/utils/excel.py`
- `src/app/models/application.py`
- `src/app/schemas/application_schema.py`

## Desarrollo

Recomendado ejecutar el backend con el entorno virtual del proyecto y la configuración local existente.
