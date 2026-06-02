# workflow.md
## Principios

*   **Agilidad y Autonomía:** El equipo opera de forma autónoma bajo SCRUM, atendiendo ceremonias como Dailys, Sprint Planning y Sprint Retros.

*    **Calidad Garantizada:** Ninguna funcionalidad se considera terminada sin superar una cobertura mínima de tests (objetivo 70%) y validación de seguridad.

*    **Colaboración Humano-IA:** Se utiliza al agente de IA (Gemini) como experto técnico para la arquitectura, generación de tests y validación de lógica de negocio bajo parámetros SCRUM.

* **Seguridad por Diseño:** Todo endpoint debe ser evaluado bajo la jerarquía de roles antes de su implementación.

## Proceso para una Historia de Usuario (HU)

### Análisis

Leer la HU y sus **Criterios de Aceptación (CA)**. Identificar los **tests E2E** necesarios para validar el flujo completo en el backend.

*  **Acción del Agente:** Propone el plan de pruebas y los escenarios de seguridad (ej: probar acceso no autorizado).

* **Acción del Humano:** Valida el plan de pruebas propuesto.

### Descomposición
- Dividir la HU en **Tareas Técnicas** independientes (ej: BE-07-T1, BE-07-T2).

- **Acción del Humano:** Realiza y prioriza esta descomposición en el backlog.

### Ciclo por Tarea (Sprints Técnicos) 
El humano define el inicio y fin de cada tarea.

a. **Análisis Técnico:**: Entender el impacto en la API y el modelo de datos (SQLAlchemy).

b. **Diseño de Contratos:**: Definir el endpoint (verbo, ruta), el esquema JSON esperado y el nivel de rol requerido.

c. **Validación del Diseño:**: El humano valida el contrato de la API. No se escribe código sin esta aprobación.

d. **Implementación:**

     1. **Código:**: Escribir lógica en FastAPI siguiendo principios SOLID y nomenclatura en inglés.
     2. **Tests Unitarios:**: CCrear pruebas para modelos o helpers de seguridad co-localizados o en tests/.
     3. **Tests de Integración:**: Desarrollar los tests en la carpeta /tests/ utilizando las fixtures de conftest.py.
e. **Ejecución y Debugging:**: Ejecutar pytest dentro del contenedor Docker para asegurar que la tarea cumple con los requisitos sin romper módulos previos.
f. **Validación final de la tarea**: El humano revisa el código y los resultados de los tests para dar el visto bueno.

### Validación Final de la Historia de Usuario

* **Integración Total:** Ejecutar la suite completa de tests de la HU para verificar la persistencia en PostgreSQL y la correcta emisión de JWT.
* **Estado "Done":** La HU se marca como terminada solo cuando los tests pasan y el código está documentado en el README.

* **Sprint Review:** El equipo demuestra la funcionalidad al stakeholder (cliente) en un entorno funcional o mediante la demostración del código probado.
