# Instrucciones de despliegue

## Objetivo
Este documento detalla el procedimiento para poner en producción el backend y la base de datos de CourseFlow. El objetivo es garantizar un entorno estable, seguro y escalable mediante contenedores, cumpliendo con los estándares de profesionalidad requeridos.

## Orquestación con Docker
Para asegurar que el proyecto sea "totalmente integrado y flexible", utilizamos Docker y Docker Compose. Esto permite desplegar la lógica de negocio (Python/FastAPI) y la persistencia (PostgreSQL) de forma simultánea.

### Comando para Despliegue

Desde la raíz del directorio backend, ejecuta:


```bash
docker-compose up -d --build
```

- d: Ejecuta los servicios en segundo plano (detached mode).

- -build: Reconstruye las imágenes para asegurar que el código fuente más reciente esté incluido.

## Contenido del Entorno de Producción

La arquitectura desplegada se compone de:

- **Contenedor de API:** Ejecuta la lógica en Python (FastAPI/FastAPI) bajo un servidor de grado de producción como Gunicorn o Uvicorn.- **Contenedor de BBDD:** Una instancia de PostgreSQL que gestiona el modelo relacional de usuarios, cursos y solicitudes.
- **Volúmenes de Datos:** Para asegurar que la información de la base de datos no se pierda al reiniciar los contenedores.

# Consideración de Datos y Seguridad

El despliegue del backend debe seguir estas reglas críticas:

-**Variables de Entorno:** Nunca incluir el archivo .env en el repositorio. Las claves para JWT y credenciales de DB deben configurarse directamente en el servidor de despliegue.
- **Migraciones de DB:** Se debe acreditar el proceso de creación del modelo de base de datos en el documento de presentación.
- **API REST:** Todos los endpoints deben respetar el estándar REST para asegurar la interoperabilidad con el frontend.

## Regla de Despliegue y Git
-**Control de Versiones:** Solo se despliega desde la rama de producción (main). El trabajo diario se mantiene en las ramas de development o individuales.
-**Código Limpio:** El código desplegado debe estar libre de bugs, formateado, comentado en inglés y haber pasado los tests de Pytest.

## Verificación de Integridad:

Una vez levantados los servicios, se debe verificar:

- **Conectividad:** Que los endpoints de la API respondan correctamente (validar con Postman/Thunder Client).

- **Seguridad:** Verificar que el sistema de autenticación protege las rutas de administración.

- **Logs:** Revisar los registros de Docker para asegurar que no hay errores de conexión con PostgreSQL

```bash
docker logs courseflow-backend
```

-**Fecha de Entrega:** Los entregables finales (Código en GitHub y Presentación) deben estar listos para el 2 y 3 de junio de 2026. 