## BRIEFING DE PROYECTO FULLSTACK
CourseFlow – Plataforma de Gestión de Cursos y Convocatorias
1. Introducción
El presente proyecto consiste en el desarrollo de una aplicación web fullstack orientada a la gestión
de cursos y solicitudes de participación en entornos formativos y sociales, como SomosF5.
La herramienta busca centralizar la información de cursos, facilitar la gestión de participantes y
simplificar el proceso de inscripción, sustituyendo herramientas manuales como hojas de cálculo.
El desarrollo se realizará en un sprint de dos semanas bajo metodología ágil (Scrum), con un equipo
de cinco personas.
2. Contexto y problemática
Actualmente, la gestión de cursos en organizaciones formativas suele realizarse de forma manual, lo
que genera:
● Dificultad en el seguimiento de participantes
● Procesos de inscripción poco estructurados
● Falta de control centralizado de la información
● Problemas en la gestión de bajas y cancelaciones
Se requiere una solución simple, funcional y adaptable a la realidad operativa.
3. Objetivo del proyecto
Desarrollar un MVP funcional que permita:
● Gestionar cursos de forma centralizada
● Permitir solicitudes de inscripción por parte de usuarios
● Facilitar la gestión de participantes por parte del administrador
● Proporcionar una visión clara del estado de los cursos
4. Alcance del proyecto (MVP obligatorio)
4.1 Autenticación y usuarios
● Registro de usuarios
● Inicio de sesión
● Roles: usuario y administrador
4.2 Gestión de cursos
● Creación de cursos
● Edición de cursos
● Visualización de cursos
Cada curso incluye:
● Nombre
● Descripción
● Fechas
● Capacidad (informativa)
● Estado de visibilidad (activo/inactivo)
4.3 Solicitud de inscripción
● El usuario puede solicitar participar en un curso
● La solicitud no implica acceso automático
● El usuario queda registrado como candidato
4.4 Gestión de solicitudes (admin)
● Visualización de solicitudes por curso
● Aceptación o rechazo de usuarios
● Eliminación de solicitudes
4.5 Panel de administración
● Listado de cursos
● Listado de solicitudes
● Gestión básica de participantes
4.6 Vista de usuario
● Listado de cursos disponibles
● Envío de solicitud de inscripción
● Consulta del estado de su solicitud
5. Modelo simplificado de funcionamiento
El sistema se basa en un flujo simple:
1. El usuario visualiza cursos disponibles
2. El usuario solicita participación
3. El administrador revisa solicitudes
4. El administrador acepta o rechaza usuarios
5. El usuario es informado de su estado
6. Funcionalidades opcionales (no obligatorias)
Estas funcionalidades se consideran mejoras si el tiempo lo permite:
# 6.1 Estados avanzados de candidatura
● Pendiente
● Aceptado
● Lista de espera
● Rechazado
● Cancelado
● No presentado
6.2 Sobre-reserva de participantes
● Capacidad objetivo con margen adicional de participantes aceptados
● Gestión flexible de plazas
6.3 Automatización de visibilidad de cursos
● Publicación automática según fechas
● Ocultación automática al inicio del curso
6.4 Promoción automática de candidatos
● Gestión automática de lista de espera en caso de cancelaciones
7. Requisitos técnicos
Frontend
● Vue.js (o React / Angular)
● HTML5 y CSS3
● Consumo de API REST
Backend
● Python
● Framework recomendado: FastAPI
● API REST
Base de datos
● PostgreSQL (principal)
● Alternativas: MySQL o MongoDB
DevOps
● Docker
● Git
● Metodología Scrum
● Herramientas colaborativas (Jira, Figma)
8. Arquitectura del sistema
La aplicación sigue una arquitectura cliente-servidor:
● Frontend: interfaz de usuario
● Backend: lógica de negocio
● API REST: comunicación entre sistemas
● Base de datos: almacenamiento persistente
9. Modelo de datos (simplificado)
users
● id
● name
● email
● password
● role
courses
● id
● name
● description
● start_date
● end_date
● capacity
● is_active
applications
● id
● user_id
● course_id
● status
● created_at
10. Organización del equipo
Equipo de cinco personas:
● 1 UX/UI + apoyo frontend
● 2 frontend developers
● 1 backend developer
● 1 backend + base de datos + despliegue
Trabajo en equipo con Git y revisiones de código.
11. Planificación del sprint (2 semanas)
Fase 1: Definición (Días 1–2)
● Alcance del proyecto
● Diseño en Figma
● Modelo de datos
● Definición de API
Fase 2: Backend base (Días 3–5)
● Autenticación
● CRUD de cursos
● Base de datos
Fase 3: Frontend base (Días 6–8)
● Vistas principales
● Login
● Listado de cursos
● Conexión con API
Fase 4: Funcionalidad principal (Días 9–11)
● Solicitudes de inscripción
● Panel de administración
● Gestión de usuarios por curso
Fase 5: Testing y ajustes (Días 12–13)
● Corrección de errores
● Integración completa
Fase 6: Entrega (Día 14)
● Deploy
● Demo final
12. User Stories
● Como usuario, quiero registrarme para acceder a la plataforma
● Como usuario, quiero ver cursos disponibles
● Como usuario, quiero solicitar participación en un curso
● Como administrador, quiero crear cursos
● Como administrador, quiero gestionar solicitudes de usuarios
13. Criterios de éxito
El proyecto será considerado exitoso si:
● Permite autenticación de usuarios
● Permite creación y gestión de cursos
● Permite solicitudes de inscripción
● Permite gestión de solicitudes por parte del administrador
● Está desplegado y funcional
● El flujo principal funciona sin errores
14. Conclusión
CourseFlow es una solución MVP orientada a la gestión de cursos y participantes en entornos
formativos. El diseño prioriza simplicidad, funcionalidad y adaptabilidad a un contexto real,
permitiendo una implementación completa en un sprint de dos semanas.
Las funcionalidades avanzadas quedan como extensiones opcionales para futuras iteraciones del
producto.