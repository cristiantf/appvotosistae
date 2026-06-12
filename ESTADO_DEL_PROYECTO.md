# Estado del Proyecto: Sistema de Votación (appvotosistae)

Este documento detalla el estado actual del proyecto de desarrollo del sistema de votación electrónica, incluyendo las funcionalidades ya implementadas, los problemas identificados y las áreas de mejora.

## 1. Visión General
El proyecto es una aplicación web desarrollada con **Python y Flask** para la gestión de elecciones estudiantiles. Utiliza una base de datos relacional (configurada para MySQL en producción y SQLite en desarrollo) administrada mediante SQLAlchemy.

## 2. Funcionalidades Implementadas

### Autenticación y Usuarios
- ✅ Login y Logout funcional.
- ✅ Registro de usuarios validando contra un padrón pre-cargado.
- ✅ Roles diferenciados: Administrador y Votante.

### Panel de Administración
- ✅ Dashboard básico para administradores.
- ✅ Gestión (CRUD) de Periodos Electorales.
- ✅ Activación y desactivación de elecciones.
- ✅ Carga masiva de padrones electorales desde archivos Excel/CSV (`pandas`, `openpyxl`).
- ✅ Gestión (CRUD) de Listas de candidatos (con soporte para subida de imágenes).
- ✅ Gestión (CRUD) de Candidatos individuales y asignación a listas.
- ✅ Edición manual de datos de votantes.

### Proceso de Votación (Usuario Final)
- ✅ Vista de elecciones activas.
- ✅ Visualización de listas participantes en la elección.
- ✅ Lógica para emitir un voto asegurando que sea un **voto único por elector y elección**.
- ✅ Restricción de acceso para no permitir votar en elecciones inactivas o si ya votó.

### Resultados y Análisis
- ✅ Visualización pública de resultados de elecciones finalizadas.
- ✅ Dashboard de resultados en el panel de administrador con gráficos de barras (utilizando `Chart.js`).

### Infraestructura y Desarrollo
- ✅ Estructura modular con Blueprints de Flask (`admin`, `auth`, `main`, `voting`).
- ✅ Pruebas automatizadas configuradas con `pytest`.
- ✅ Variables de entorno gestionadas con `python-dotenv`.
- ✅ Migraciones de base de datos con `Flask-Migrate`.
- ✅ Comandos CLI personalizados (`clean-orphans`).

## 3. Análisis y Áreas de Mejora Identificadas

A partir de la revisión del código y la investigación sobre la normativa de educación superior en Ecuador (LOES, CES), se han identificado las siguientes áreas críticas de mejora para llevar el proyecto a un nivel profesional y conforme a ley:

### Seguridad y Auditoría
- ✅ **Registro de auditoría (Logs):** Se implementó trazabilidad completa. Todas las acciones administrativas (creación/eliminación de usuarios, periodos, candidatos y cargas masivas) son registradas.
- ⚠️ **Seguridad del Voto:** (Corregido en el Sprint 1, voto totalmente anónimo).

### Funcionalidades de Ley (Cumplimiento Normativo)
- ✅ **Voto Nulo y Voto en Blanco:** Opciones por defecto incorporadas.
- ✅ **Fechas de Elección Automáticas:** Periodos con validación temporal estricta y temporizadores en tiempo real en la UI.
- ⚠️ **Requisitos de Candidatos:** Validaciones manuales.
- ✅ **Dignidades Predefinidas:** Se implementó modelo `Dignity` y asignación dinámica.

### Experiencia de Usuario (UI/UX)
- ✅ **Diseño y Estilos:** Rediseño completo "Premium" (CSS Vainilla + Tailwind inspired), interactivo y responsive.
- ✅ **Accesibilidad:** Contrastes e iconografía estandarizada.

### Refactorización Técnica
- ✅ La lógica de carga de Excel (`src/utils.py`) fue reconstruida usando **Bulk Inserts (SQLAlchemy)** y pre-procesamiento con pandas, logrando insertar miles de registros en menos de 15 segundos.
- ⚠️ `config.py` tiene la `SECRET_KEY` quemada en el código como fallback.
- ⚠️ La base de datos de producción está expuesta en `.env` en el repositorio local. Debe rotarse y asegurarse.

## 4. Historial de Sprints

### Sprint 1: Anonimato, Cumplimiento Legal y Rediseño Base (Completado)
- **Base de Datos:** Migración a MySQL local. Separación de votos e identidades creando la tabla `VoterParticipation` y haciendo anónima la tabla `Vote`.
- **Funcionalidad:** Opciones automáticas de Voto en Blanco y Nulo. Carga masiva de padrones electorales (Bulk Query) optimizada.
- **UI/UX:** Rediseño completo con "CSS Vainilla Premium". Tarjetas interactivas, efecto glassmorphism en el login, y papeleta electoral moderna.

### Sprint 2: Panel Superadmin y Correcciones Específicas (Completado)
- **Roles Avanzados:** Se introdujo el campo `is_superadmin` en el modelo de usuario.
- **Seguridad:** Creación del decorador `@superadmin_required`. El panel de gestión de usuarios está ahora restringido y solo los superadmins pueden visualizar usuarios o cambiar los permisos de administrador de otros.
- **Impersonación (Login As):** El superadmin puede iniciar sesión directamente en la cuenta de cualquier otro usuario para soporte técnico y pruebas.
- **Correcciones Windows:** Se modificó la función de subida de imágenes (`save_picture`) para usar barras diagonales simples (`/`) en lugar del `os.path.join` de Windows, asegurando que las imágenes de candidatos y listas carguen correctamente en el navegador.

### Sprint 3: Gestión Dinámica de Dignidades y Papeleta Electoral (Completado)
- **Modelos:** Se creó el modelo `Dignity` y se modificó `Candidate` para referenciarlo mediante `dignity_id`.
- **Panel de Administración:** Se implementó una interfaz en la gestión de cada Periodo Electoral para crear y eliminar dignidades específicas de ese periodo.
- **Formularios Dinámicos:** Al crear o editar un candidato, el campo de dignidad es ahora un desplegable (`SelectField`) que se carga automáticamente con las dignidades configuradas para ese periodo, evitando errores de tipeo.
- **Visualización Pública:** La papeleta electoral (`show_lists.html`) fue actualizada para mostrar de forma compacta (mini-avatares, nombre y dignidad) a todos los candidatos que conforman cada lista.

### Sprint 4: Gestión de Usuarios y Paginación (Completado)
- **Gestión Avanzada:** Se implementó CRUD completo de usuarios desde el panel de Super Admin, incluyendo filtros y barra de búsqueda.
- **Paginación:** Las listas extensas (como el listado de usuarios) ahora usan paginación del lado del servidor.
- **Seguridad UI:** Integración de SweetAlert2 para validaciones de acciones destructivas (eliminación de usuarios, periodos y listas).

### Sprint 5: Automatización de Elecciones y Mejoras de UI (Completado)
- **Fechas Automáticas:** El modelo `ElectionPeriod` adquirió lógica inteligente para calcular su estado (`pending`, `active`, `finished`) según la hora exacta del servidor en contraste con las propiedades `start_date` y `end_date`.
- **Botón de Pánico:** El estado manual se conservó como un control de emergencia (`manual_inactive`) que permite detener el proceso electoral forzosamente.
- **Temporizador Dinámico:** Implementación de relojes de cuenta regresiva automáticos (JavaScript) en la página principal para las elecciones futuras y activas.
- **Traducción y Modernización Premium:** Migración del panel de administración (Dashboard y Lista de Periodos) a un diseño basado en tarjetas (Cards Premium), modernización visual de botones, alertas sin duplicados, y traducción completa al español (barras de navegación y controles).

### Sprint 6: Actas Oficiales en PDF y Consolidación UI (Completado)
- **Resultados Interactivos:** Rediseño del dashboard de resultados con una mejor paleta de colores para `Chart.js`, tooltips ampliados y tablas de conteo de votos con insignias y cálculo del total de sufragios.
- **Actas en PDF (Backend):** Implementación de la librería `fpdf2` para generar el "Acta Oficial de Escrutinio". La lógica calcula automáticamente el porcentaje de participación, estructura el documento de manera inmutable y añade un pie de firma para las autoridades y fecha de emisión exacta, permitiendo descargas seguras desde el navegador.
- **Estandarización Premium:** Refactorización visual de las pantallas de "Gestionar Candidatos", "Editar Candidato" y listas de administración, integrando Select2 mejorado, botones con etiquetas textuales y modales inteligentes con SweetAlert2 para edición y confirmación de destrucción de datos.

### Sprint 7: Seguridad Avanzada y Rendimiento (Completado)
- **Audit Logs:** Trazabilidad inmutable de todas las acciones que realizan los administradores. Visualización paginada exclusiva para Super Admins.
- **Motor de Respaldos (DLP):** Archivero visual integrado de archivos ZIP (Data Loss Prevention) y respaldos forzosos al eliminar periodos.
- **Carga Masiva Ultra-rápida:** Migración de importación de Excel a operaciones `Bulk Insert` en base de datos.
- **Automatización Background:** Respaldos automáticos programados con APScheduler.

### Sprint 8: Autenticación Biométrica (Face ID) y Control Global (Completado)
- **Face ID Zero-Trust:** Implementación de reconocimiento facial con `face-api.js` (TensorFlow) en el navegador del usuario para extracción de vectores matemáticos (128d), asegurando que ninguna foto se transmita o guarde en el servidor.
- **Validación Euclidiana:** Motor matemático en Python (`numpy`) que intercepta la intención de voto y pide la comprobación facial en vivo (Liveness Detection). Si la Distancia Euclidiana es menor a 0.62, sella la identidad y procesa el sufragio en milisegundos.
- **Fallback Criptográfico:** Si el estudiante no cuenta con cámara, el sistema degrada de manera segura pidiéndole confirmar su contraseña actual antes de emitir el voto (doble factor lógico).
- **Ajustes de Sistema Global:** Implementación de la vista y modelo `SystemSettings` para permitir a los Super Administradores abrir, cerrar o programar rangos de fechas automáticos para el registro libre de nuevos estudiantes.
- **Padrón Inteligente:** Nuevo buscador difuso en la gestión de padrones. Permite a los administradores agregar estudiantes registrados manualmente buscando por cédula, alias o nombre real. Incluye generación automática de perfil `Voter` si este era inexistente para cuentas manuales.
- **Modelos Refinados:** Se agregaron campos `name` y `lastname` nativos a la tabla `User` unificando la lectura de nombres entre módulos administrativos y de voto.


## 5. Próximos Pasos Inmediatos
1. Validaciones documentales y requisitos académicos de candidatos en caso de ser necesario por el reglamento institucional.
2. Escalabilidad: Implementar un servidor WSGI (Gunicorn/Waitress) para despliegue en producción.
