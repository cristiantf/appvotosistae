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
- ⚠️ **Falta registro de auditoría (Logs):** No hay trazabilidad de qué administrador creó, modificó o eliminó elecciones/listas/candidatos, ni cuándo se importaron padrones. Es crucial para la transparencia.
- ⚠️ **Seguridad del Voto:** El voto se guarda en texto plano relacionando `voter_id` con `candidate_list_id` en la tabla `Vote`. Para asegurar el secreto absoluto del voto según normativa, se debe implementar una capa de anonimización o hashing, de forma que se separe la identidad del votante de la preferencia emitida.

### Funcionalidades de Ley (Cumplimiento Normativo)
- ⚠️ **Voto Nulo y Voto en Blanco:** Actualmente, el sistema obliga a votar por una lista específica. Las elecciones requieren por ley la opción de voto nulo y blanco.
- ⚠️ **Fechas de Elección Automáticas:** Los periodos electorales se activan/desactivan manualmente. Deberían tener fechas/horas de inicio y fin programadas.
- ⚠️ **Requisitos de Candidatos:** No hay validación sistémica de si un candidato cumple los requisitos académicos (promedio, 50% de malla). Esto puede manejarse administrativamente, pero el sistema podría tener campos para registrar la validación documental.
- ⚠️ **Dignidades Predefinidas:** Las dignidades son texto libre. Deberían estar estandarizadas (Presidente, Vicepresidente, Vocales, etc.) e implementarse un control de paridad de género.

### Experiencia de Usuario (UI/UX)
- ⚠️ **Diseño y Estilos:** La interfaz utiliza Bootstrap básico. Se requiere una modernización visual significativa, uso de paletas de colores institucionales y mejor diseño responsivo (mobile-first), dado que la mayoría de los estudiantes votarán desde sus celulares.
- ⚠️ **Accesibilidad:** Faltan contrastes adecuados, etiquetas ARIA y soporte total para lectores de pantalla.

### Refactorización Técnica
- ⚠️ La lógica de carga de Excel (`src/utils.py`) procesa fila por fila, lo cual es ineficiente para padrones grandes. Debería optimizarse usando inserciones masivas (`bulk_insert`).
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

## 5. Próximos Pasos Inmediatos
1. Continuar con el **Plan de Desarrollo** abordando las fechas automáticas de elección.
2. Refinar la gestión de dignidades predefinidas.
