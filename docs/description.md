# Proceso de Refactorización del Backend

Este documento describe el proceso de refactorización llevado a cabo para implementar nuevas reglas de negocio y validaciones en el backend de la aplicación CourseFlow, basándose en las historias de usuario y especificaciones proporcionadas.

## 1. Preparación del Entorno

- Se cambió a la rama `mirel` para aislar los nuevos desarrollos y no afectar la rama principal.

## 2. Modificación de los Modelos de la Base de Datos (`app/models/`)

Se actualizaron los modelos de SQLAlchemy para reflejar los nuevos requisitos de datos.

### `user.py`
- Se añadió el campo `dni_nie` (`String(20)`), único y opcional, para almacenar el DNI o NIE del usuario.
- Se añadió el campo `birth_date` (`Date`), opcional, para la fecha de nacimiento del usuario.

### `application.py`
- Se añadió el campo `has_darde` (`Boolean`), opcional, para indicar si el solicitante es demandante de empleo.
- Se añadió el campo `previous_education` (`Text`), opcional, para que el usuario pueda detallar su formación previa.

## 3. Actualización de Esquemas y Validaciones (`app/schemas/`)

Se modificaron los esquemas de Pydantic para validar los datos de entrada en la API.

### `user_schema.py`
- Se incluyeron los campos `dni_nie` y `birth_date` en el esquema base `UserBase`.
- Se implementó un validador para `dni_nie` que comprueba el formato estándar de DNI/NIE español.
- Se añadió un validador para `birth_date` que asegura que el usuario sea mayor de 18 años.

### `application_schema.py`
- Se creó el archivo y se definieron los esquemas `ApplicationBase`, `ApplicationCreate` y `ApplicationRead`.
- Se incluyó el campo `has_darde` (booleano y obligatorio).
- Se añadió `previous_education` con una validación que limita la longitud máxima a 250 caracteres.

## 4. Implementación de la Lógica de Negocio en la API (`app/api/v1/`)

Se refactorizaron las rutas de la API para implementar las nuevas reglas de negocio y de seguridad.

### `routes_applications.py`
- **Inscripción Única:** Se verifica que un usuario no pueda inscribirse más de una vez en el mismo curso.
- **Control de Aforo:** Antes de crear una inscripción, se comprueba si el número de solicitudes aceptadas ha alcanzado la capacidad máxima del curso.
- **Validación de Fechas y Visibilidad:** Se impide la inscripción si la fecha actual es posterior a la fecha de inicio del curso o si el curso no está activo (`is_active = false`).
- **Seguridad por Roles:** Se restringió el endpoint de actualización de estado de solicitudes (`PATCH /{app_id}`) para que solo los usuarios con rol de `admin` puedan utilizarlo.

### `routes_courses.py`
- **Seguridad por Roles:** Se protegieron los endpoints de creación (`POST`), actualización (`PUT`) y eliminación (`DELETE`) de cursos para que solo los administradores puedan realizar estas operaciones.
- **Endpoint de Eliminación:** Se añadió un endpoint `DELETE /{course_id}` que no existía previamente.

## 5. Pasos Siguientes Recomendados

- **Crear una nueva migración de base de datos** con Alembic para aplicar los cambios realizados en los modelos a la estructura de la base de datos.
- **Ejecutar las pruebas** para verificar que las nuevas funcionalidades y restricciones operan correctamente.
- **Realizar un `commit`** con todos los cambios en la rama `mirel` y, cuando esté validado, integrarlo a la rama principal.
