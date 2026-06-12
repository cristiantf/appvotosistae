# Plan de Trabajo (Próximos Pasos)

Este documento detalla el plan de implementación para las próximas dos fases críticas del Sistema de Votación: el cumplimiento normativo avanzado para candidatos y la preparación de la infraestructura para el paso a Producción.

---

## Fase 1: Validaciones Documentales y Requisitos Académicos

**Objetivo:** Adaptar el registro de candidatos para que cumpla con los reglamentos institucionales (Ej. Ley Orgánica de Educación Superior - LOES, o estatutos internos), garantizando que solo estudiantes elegibles puedan postularse.

### Tareas:
1. **Análisis de Requisitos Institucionales:**
   - [ ] Definir con las autoridades qué requisitos son obligatorios (Ej. promedio mínimo, no tener sanciones disciplinarias, semestre/año cursando).
2. **Ampliación del Modelo `Candidate`:**
   - [ ] Añadir campos booleanos o de texto en la base de datos para subir evidencias (Ej. `academic_record_pdf`, `disciplinary_clearance`).
   - [ ] Crear un campo de estado de validación (`pending`, `approved`, `rejected`).
3. **Módulo de Revisión para Administradores:**
   - [ ] En el panel de "Gestionar Candidatos", añadir una vista detallada para que el Tribunal Electoral valide manualmente los documentos y apruebe o rechace la postulación.
4. **Notificaciones y Flujo:**
   - [ ] Implementar un sistema de alertas para que los candidatos o administradores de listas sepan si a un candidato le falta algún documento.

---

## Fase 2: Escalabilidad y Despliegue en Producción

**Objetivo:** Abandonar el servidor de desarrollo nativo de Flask (Werkzeug) que no está diseñado para soportar múltiples conexiones simultáneas, y migrar a una arquitectura WSGI profesional robusta.

### Tareas:
1. **Selección de Servidor WSGI:**
   - Dado que el servidor se ejecuta en un entorno Windows, la herramienta estándar `Gunicorn` (exclusiva de UNIX/Linux) no es compatible de forma nativa. 
   - [ ] Se implementará **Waitress**, un servidor WSGI de grado de producción diseñado para funcionar perfectamente en Windows con excelente concurrencia.
2. **Configuración de Waitress:**
   - [ ] Instalar la librería: `pip install waitress`
   - [ ] Crear un script de inicio seguro `run_waitress.py` que importe la aplicación Flask y la monte en un puerto seguro (Ej. puerto 80/443 o 8080 detrás de un proxy).
3. **Proxy Inverso (Nginx o IIS):**
   - [ ] (Opcional pero recomendado) Documentar la instalación de Nginx o Internet Information Services (IIS) como proxy inverso para manejar los certificados SSL/TLS (HTTPS real, no `adhoc`) y despachar tráfico estático (imágenes/css) de manera eficiente.
4. **Pruebas de Carga (Stress Testing):**
   - [ ] Utilizar herramientas como `locust` o `Apache JMeter` para simular 100-500 votantes concurrentes autenticándose y usando el Face ID al mismo tiempo, garantizando que el servidor Windows y Waitress no se asfixien durante el día de las elecciones.

---
*Nota: Este plan de trabajo puede expandirse o iterar dependiendo del feedback normativo de las autoridades estudiantiles.*
