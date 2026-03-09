# Registro de Archivos y Directorios Obsoletos

Este directorio contiene archivos y carpetas que han sido apartados del proyecto principal por considerarse innecesarios, duplicados o remanentes de versiones anteriores.

Se han movido aquí en lugar de eliminarse permanentemente como medida de precaución.

## Detalle de Contenido

### `instance/`
*   **Origen**: Raíz del proyecto (`/instance`).
*   **Contenido**: Bases de datos locales de SQLite (`app.db`, `voting.db`).
*   **Motivo**: El proyecto está configurado para usar una base de datos MySQL remota a través de la variable de entorno `DATABASE_URL`. Estos archivos locales no se utilizan y podrían causar confusión.

### `src/voto/`
*   **Origen**: `/src/voto`.
*   **Contenido**: Un blueprint completo (rutas, plantillas).
*   **Motivo**: Parece ser una versión duplicada o antigua del blueprint `src/voting/`. Su funcionalidad es redundante y no estaba siendo utilizado activamente en la aplicación.

### `src/index.html`
*   **Origen**: `/src/index.html`.
*   **Motivo**: Archivo de plantilla HTML ubicado fuera del directorio estándar `src/templates`. No estaba siendo renderizado por ninguna ruta.

### `src/templates/admin/` (movidos a `obsoletos/src/templates/admin/`)
*   **Origen**: `/src/templates/admin/`.
*   **Archivos Movidos**:
    *   `manage_elections.html`: Se confirmó que el endpoint que lo usaba era incorrecto. La funcionalidad real está en `list_election_periods.html`.
    *   `manage_list_details.html`: Contenido duplicado con `manage_list.html`.
    *   `manage_period_details.html`: Contenido duplicado con `manage_election_period.html`.
    *   `create_admin.html`: La creación de administradores se realiza mediante un script de línea de comandos (`create_admin_user.py`), no a través de una plantilla web.
    *   `index.html`: Plantilla genérica sin uso en el contexto del blueprint de administración.

### `src/templates/main/` (movidos a `obsoletos/src/templates/main/`)
*   **Origen**: `/src/templates/main/`.
*   **Archivos Movidos**:
    *   `login.html`: La funcionalidad de login y sus plantillas correspondientes son gestionadas por el blueprint `auth` (`src/auth/templates/login.html`), por lo que este archivo era un duplicado no utilizado.

---
*Este registro fue generado el 2024-07-30.*
