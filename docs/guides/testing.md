# Instrucciones para testing (Backend - CourseFlow)

## Principios
*   **Cobertura mínima:**:El proyecto debe superar el 70% de cobertura en rutas y modelos para garantizar estabilidad.

*   **Aislamiento con Rollback:**: Cada test debe ejecutarse de forma aislada, utilizando transacciones con rollback o recreando la base de datos para no compartir estado entre ejecuciones.

*   **Nomenclatura clara**: Usa el prefijo `test_` para identificar los archivos de prueba (ej: `test_auth.py`).

## Tests Unitarios y de Integración

### Tests Unitarios
La estructura de pruebas de CourseFlow sigue las mejores prácticas de Pytest para backend en Python. Los tests se organizan en la carpeta `tests/` y se ejecutan de forma aislada utilizando transacciones que se revierten tras cada prueba.

Siguiendo la arquitectura de carpetas detectada, los tests se centralizan para facilitar la ejecución en el contenedor de Docker.
```
sCourseFlow_Backend/
├── app/
│   ├── models/          # Modelos de SQLAlchemy
│   ├── routes/          # Blueprints de la API
│   └── decorators.py    # Lógica de @require_role
├── tests/               # Carpeta central de pruebas
│   ├── conftest.py      # Fixtures globales (app, db, client, auth_headers)
│   ├── test_auth.py     # Registro, Login y JWT
│   ├── test_roles.py     # Jerarquía: User, Admin, Superadmin
│   ├── test_courses.py  # CRUD de cursos (Admin)
│   └── test_apps.py     # Solicitudes de inscripción
└── pytest.ini           # Configuración de pytest
```

### Contextos de Prueba Obligatorios
Todos los demás tests se organizan dentro de la carpeta `/tests/` en la raíz del proyecto.

```
proyecto/
├── src/                # Código fuente
├── tests/              # Carpeta dedicada a tests globales
│   ├── integration/    # Tests de integración
│   ├── e2e/            # Flujos de usuario (ej: navegación, CRUD)
│   └── fixtures/       # Datos JSON de prueba para simular la API
└── ...
```

## Contextos de Prueba Obligatorios

Para cumplir con los criterios de rendimiento del proyecto pedagógico, la suite de pruebas debe cubrir:

* 1. **Seguridad y Jerarquía (BE-02/BE-05):** Validar que un USER reciba un 403 Forbidden al intentar acceder a rutas de ADMIN o SUPERADMIN.

* 2.   **Autenticación (BE-01):** erificar el flujo de registro (evitando duplicados), login con generación de JWT y cierre de sesión con lista negra.

* 3.  **Lógica de Negocio (BE-03):** Validar que la creación de cursos tenga fechas coherentes (end_date > start_date) y que el borrado sea lógico.

* 4. **Integridad de Datos (BE-04):** Asegurar que un usuario no pueda solicitar el mismo curso dos veces (Constraint Unique) y que pueda cancelar su propia solicitud.


## Comandos para Ejecutar Tests

Para asegurar que el código funciona sin bugs antes de la entrega del 2 de junio:

```
# Ejecutar toda la suite de pruebas desde el contenedor
docker compose exec backend pytest

# Ejecutar con reporte de cobertura (Meta: >=70%)
docker compose exec backend pytest --cov=app --cov-report=term-missing

# Ejecutar un archivo específico
docker compose exec backend pytest tests/test_roles.py
```
