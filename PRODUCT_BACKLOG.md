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

### Epic: Seguridad

- **Historia de Usuario (Prioridad: Media):** Como **administrador**, quiero tener un **registro de auditoría** de las acciones importantes (ej. creación de elecciones, carga de votantes) para poder rastrear cambios y responsabilidades.

---

## Funcionalidades Completadas

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero que la **aplicación sea estable y se pueda ejecutar sin errores de dependencias críticas** para poder continuar con el desarrollo y realizar demostraciones.
    - *Nota Técnica: Se eliminó la dependencia `bootstrap-flask` que causaba un error de instalación irrecuperable en el entorno de desarrollo. Se refactorizaron las plantillas de `login` y `register` para renderizar los formularios con HTML y clases de Bootstrap directamente, eliminando la necesidad de la macro `quick_form`.*

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero tener una **suite de tests automatizados** para asegurar que las nuevas funcionalidades no rompan el código existente y para garantizar la fiabilidad de la aplicación.

- **Historia de Usuario (Completada):** Como **desarrollador**, quiero **evitar la filtración de información sensible** en los mensajes de error para proteger la aplicación contra posibles ataques.

- **Historia de Usuario (Completada):** Como **administrador**, quiero ver los **resultados de la votación en un dashboard con gráficos** para analizar la información de manera más visual e intuitiva.

- **Historia de Usuario (Completada):** Como **administrador**, quiero poder **editar y eliminar** períodos electorales, listas y candidatos para poder corregir errores y gestionar el ciclo de vida de las elecciones.

- **Historia de Usuario (Completada):** Como **votante**, quiero poder **ver los candidatos de cada lista** antes de emitir mi voto para tomar una decisión informada.
