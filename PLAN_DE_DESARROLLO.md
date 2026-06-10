# Plan de Desarrollo: Mejoras al Sistema de Votación ISTAE

Este plan de desarrollo aborda las necesidades detectadas en el análisis del proyecto y la investigación normativa, con el objetivo de convertir el prototipo actual en un sistema de votación robusto, legalmente vinculante, seguro y con una excelente experiencia de usuario.

## User Review Required

> [!WARNING]
> **Separación de la identidad y el voto:** Actualmente, la tabla `Vote` guarda quién votó y por quién votó. Para cumplir con el principio de **voto secreto** (LOES), propongo separar esto en dos tablas: `VoterParticipation` (registra que el usuario votó para evitar voto doble) y una tabla `Vote` o `Ballot` (registra el voto emitido pero SIN asociarlo al `voter_id`, siendo completamente anónimo). 
> **¿Estás de acuerdo en implementar este cambio estructural en la base de datos?**

## Open Questions

> [!IMPORTANT]
> 1. **Framework de Diseño:** El proyecto usa Bootstrap 4. Para lograr una estética premium (Rich Aesthetics) y cumplir con las directivas del sistema, propongo migrar a **Tailwind CSS** (versión 3.x) integrado con Vite, o utilizar un sistema moderno basado en utilidades de CSS Vainilla pero fuertemente estructurado. ¿Confirmas el uso de TailwindCSS o prefieres que construya un sistema de diseño Vainilla CSS desde cero con variables CSS?
> 2. **Roles Adicionales:** ¿Necesitamos crear un rol de "Tribunal Electoral" (auditor de solo lectura) además del rol "Administrador" actual?

## Proposed Changes

Las mejoras se implementarán en fases (Sprints). Este plan cubre el **Sprint 1: Cumplimiento Legal y Modernización Visual**.

### 1. Modelos de Base de Datos y Cumplimiento Normativo

Se requiere ajustar la estructura de datos para soportar características legales.

#### [MODIFY] `src/models.py`
- Añadir opciones predeterminadas de **Voto en Blanco** y **Voto Nulo** en la lógica de resultados o en la tabla `CandidateList` como opciones reservadas del sistema.
- **Refactorización de Voto Secreto:**
  - Crear modelo `VoterParticipation` (`id`, `voter_id`, `election_period_id`, `timestamp`).
  - Modificar modelo `Vote` para eliminar el `voter_id` y mantener solo `election_period_id`, `candidate_list_id` y `timestamp`.
- Añadir campos `start_date` y `end_date` al modelo `ElectionPeriod` para controlar la apertura y cierre automático de las urnas virtuales.

### 2. Capa de Seguridad y Auditoría

#### [NEW] `src/models.py` (Añadir a archivo existente)
- Crear modelo `AuditLog` para registrar acciones administrativas (quién creó, quién modificó, quién eliminó) para garantizar transparencia.

#### [MODIFY] `src/admin/routes.py`
- Inyectar lógica de auditoría (`AuditLog`) en las funciones de creación/edición/borrado de listas, candidatos y padrones.

### 3. Rediseño de la Interfaz de Usuario (UI/UX Premium)

Reconstrucción completa de las plantillas utilizando principios de diseño moderno (Glassmorphism, Dark/Light Mode, tipografías premium como 'Inter', micro-animaciones).

#### [MODIFY] `src/templates/base.html`
- Reemplazar Bootstrap 4 por un sistema de diseño moderno (Tailwind o Vainilla Premium).
- Incluir paleta de colores institucional, navegación mejorada y diseño 100% responsivo.

#### [MODIFY] `src/templates/voting/show_lists.html`
- Crear una interfaz tipo "Papeleta Electoral Interactiva".
- Añadir las opciones claras e inconfundibles para Voto Nulo y Voto en Blanco.
- Incluir modales de confirmación de voto (micro-interacciones) para evitar votos accidentales.

#### [MODIFY] `src/templates/auth/login.html` & `register.html`
- Rediseño enfocado en la conversión, con un layout de doble columna (imagen/ilustración y formulario).

#### [NEW] `src/static/css/index.css`
- Definición de tokens de diseño, tipografías y variables de color en CSS para un control total de la estética.

### 4. Lógica de Negocio y Optimizaciones

#### [MODIFY] `src/voting/routes.py`
- Adaptar la lógica de emisión de voto (`cast_vote`) a la nueva estructura de base de datos anónima (`VoterParticipation` + `Vote`).
- Incluir manejo lógico para registrar el voto en blanco o nulo.

#### [MODIFY] `src/utils.py`
- Optimizar la función `load_voters_from_excel` utilizando inserciones masivas de SQLAlchemy (bulk inserts o execute_values) en lugar de bucles fila por fila, previniendo cuellos de botella con padrones grandes (ej. +5000 estudiantes).

## Verification Plan

### Automated Tests
- Ejecutar la suite de `pytest` existente y adaptarla a los nuevos esquemas de base de datos.
- Añadir nuevas pruebas en `tests/test_voting.py` para asegurar que el registro de `VoterParticipation` ocurre y el `Vote` se guarda de forma anónima correctamente.
- Validar el control de acceso en base a las fechas de `ElectionPeriod`.

### Manual Verification
- Cargar un archivo de prueba con 1000 registros para probar la eficiencia del bulk insert.
- Validar mediante el navegador la responsividad del diseño en formato móvil.
- Ejecutar un proceso electoral de inicio a fin con múltiples cuentas y validar que los resultados de Nulos y Blancos se reflejen correctamente en el dashboard.
