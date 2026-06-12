# Product Backlog - Sistema de Votación

Este documento contiene una lista priorizada de funcionalidades, mejoras y correcciones para el proyecto, conocidas como Historias de Usuario.

---

## Funcionalidades Pendientes

### Epic: Mejoras en la Experiencia de Usuario y Funcionalidad

- **Historia de Usuario (Prioridad: Alta):** Como **administrador**, quiero poder **subir una imagen para cada lista de candidatos** para que los votantes puedan identificarlas fácilmente.

- **Historia de Usuario (Prioridad: Alta):** Como **administrador**, quiero poder **subir una foto para cada candidato** para que los votantes puedan ver por quién están votando.

- **Historia de Usuario (Prioridad: Alta):** Como **votante**, quiero **ver las imágenes de las listas y las fotos de los candidatos** al momento de votar para poder tomar una decisión más informada.

- **Historia de Usuario (Prioridad: Baja):** Como **administrador**, quiero recibir **feedback en tiempo real** sobre el progreso de la carga de votantes, especialmente con archivos grandes.

### Epic: Calidad del Código y Robustez

- **Historia de Usuario (Prioridad: Media):** Como **desarrollador**, quiero **refactorizar la función `load_voters`** en `src/admin/routes.py` para que sea más legible, mantenible y menos propensa a errores.

### Epic: Seguridad y Rendimiento

- **Historia de Usuario (Completada):** Como **administrador**, quiero tener un **registro de auditoría** de las acciones importantes (ej. creación de elecciones, carga de votantes) para poder rastrear cambios y responsabilidades.

- **Historia de Usuario (Completada):** Como **administrador**, quiero que la **carga masiva de votantes por Excel** sea instantánea usando operaciones en bloque (Bulk Inserts) para evitar caídas del servidor con padrones de miles de estudiantes.

- **Historia de Usuario (Completada):** Como **superadministrador**, quiero tener un sistema de **prevención de pérdida de datos (DLP)** que genere respaldos ZIP automáticamente al cerrar elecciones o antes de eliminar un periodo, y un **gestor visual** para restaurarlos.

---

## Funcionalidades Completadas

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero que la **aplicación sea estable y se pueda ejecutar sin errores de dependencias críticas** para poder continuar con el desarrollo y realizar demostraciones.
    - *Nota Técnica: Se eliminó la dependencia `bootstrap-flask` que causaba un error de instalación irrecuperable en el entorno de desarrollo. Se refactorizaron las plantillas de `login` y `register` para renderizar los formularios con HTML y clases de Bootstrap directamente, eliminando la necesidad de la macro `quick_form`.*

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero tener una **suite de tests automatizados** para asegurar que las nuevas funcionalidades no rompan el código existente y para garantizar la fiabilidad de la aplicación.

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero **evitar la filtración de información sensible** en los mensajes de error para proteger la aplicación contra posibles ataques.

- **Historia de Usuario (Completada):** Como **administrador**, quiero ver los **resultados de la votación en un dashboard interactivo con gráficos premium** y poder **descargar un Acta de Escrutinio en PDF** para tener un respaldo físico y formal de la elección.

- **Historia de Usuario (Completada):** Como **administrador**, quiero poder **editar y eliminar** períodos electorales, listas y candidatos a través de una interfaz de usuario moderna (estilo Premium) con modales de confirmación para evitar borrados accidentales.

- **Historia de Usuario (Completada):** Como **votante**, quiero poder **ver los candidatos de cada lista** (con sus fotos, nombres y dignidades estandarizadas) antes de emitir mi voto, en una papeleta moderna y fácil de usar en dispositivos móviles.
