# Documentación Técnica: App Voto ISTAE

## 1. Arquitectura del Sistema

El sistema está construido siguiendo una arquitectura Monolítica Modular (Modelo-Vista-Controlador) utilizando el framework **Flask (Python)**. 

### Stack Tecnológico
- **Backend:** Python 3.x, Flask
- **ORM:** Flask-SQLAlchemy
- **Base de Datos:** MySQL (Producción/Staging/Local)
- **Migraciones:** Alembic (Flask-Migrate)
- **Frontend:** HTML5, Jinja2 Templates, Bootstrap 4, CSS Vainilla Premium
- **Testing:** Pytest, pytest-flask

## 2. Estructura de Directorios

La aplicación utiliza el patrón **Application Factory** y **Blueprints** para modularidad.

```
appvotosistae/
│
├── src/                      # Código fuente de la aplicación
│   ├── __init__.py           # Application Factory (create_app)
│   ├── models.py             # Modelos de base de datos SQLAlchemy
│   ├── utils.py              # Funciones utilitarias (ej. carga de Excel)
│   ├── commands.py           # Comandos CLI de Flask
│   ├── decorators.py         # Decoradores personalizados (admin_required)
│   │
│   ├── admin/                # Blueprint de Administración
│   ├── auth/                 # Blueprint de Autenticación
│   ├── main/                 # Blueprint Principal (Vistas públicas/Resultados)
│   ├── voting/               # Blueprint de Votación (Lógica de sufragio)
│   │
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes subidas)
│   └── templates/            # Plantillas Jinja2
│
├── tests/                    # Pruebas automatizadas (pytest)
├── migrations/               # Scripts de migración de base de datos
├── instance/                 # Base de datos SQLite local (en desarrollo)
├── requirements.txt          # Dependencias de Python
├── config.py                 # Configuración de entornos
├── main.py                   # Entry point de la aplicación (run script)
└── .env                      # Variables de entorno sensibles (no versionado)
```

## 3. Modelos de Base de Datos (Esquema Relacional)

La base de datos relacional define las siguientes entidades principales en `src/models.py`:

- **`User`**: Representa a un usuario del sistema que puede hacer login. Tiene roles definidos por el flag booleano `is_admin`. Se relaciona con un `Voter`.
- **`Voter`**: (Padrón Electoral) Almacena los datos del elector (Cédula, Nombres, Apellidos). Es la entidad central de validación.
- **`ElectionPeriod`**: Define un proceso electoral (Ej. "Elecciones Estudiantiles 2024"). Controla el estado general (Activo/Inactivo) y las fechas de inicio/fin.
- **`CandidateList`**: Representa un movimiento o partido, así como opciones predeterminadas (Voto Nulo, Voto en Blanco). Se asocia obligatoriamente a un `ElectionPeriod`.
- **`Candidate`**: Persona que se postula a una dignidad específica dentro de un `CandidateList`. Debe estar registrado previamente como `Voter` válido.
- **`VoterParticipation`**: Registra la asistencia de un elector a las urnas. Relaciona a un `Voter` con un `ElectionPeriod` para validar que ya votó, sin saber qué opción eligió.
- **`Vote`**: Representa el sufragio emitido anónimo. Relaciona un `ElectionPeriod` y un `CandidateList` sin almacenar quién lo emitió.
- **`AuditLog`**: Registra las acciones críticas de los administradores en el sistema, asegurando trazabilidad.
- **`voter_period_association`**: Tabla intermedia que relaciona qué votantes están habilitados para participar en qué periodos electorales.

## 4. Seguridad y Autenticación

- **Manejo de Sesiones:** Utiliza `Flask-Login` para gestionar la sesión de usuario y la persistencia del estado de autenticación.
- **Hashing de Contraseñas:** Se emplea `werkzeug.security` (`generate_password_hash`, `check_password_hash`) para almacenar contraseñas seguras en la base de datos (algoritmo pbkdf2:sha256).
- **Autorización:** Se utiliza el decorador `@login_required` para proteger rutas, y un decorador personalizado `@admin_required` (en `src/decorators.py`) para restringir el acceso a paneles administrativos.
- **Protección CSRF:** Implementado automáticamente a través de `Flask-WTF` en todos los formularios de la aplicación.

## 5. Procesamiento de Archivos y Cargas

- **Listas y Candidatos:** Las imágenes de listas y candidatos se procesan a través de la función `save_picture` en `admin/routes.py`, la cual genera un token hexadecimal aleatorio (con el módulo `secrets`) para el nombre de archivo, evitando colisiones y sanitizando la entrada antes de guardar en `src/static/uploads/`.
- **Carga de Padrones:** Se utiliza la librería `pandas` para leer archivos `.xlsx` o `.csv`. La función `load_voters_from_excel` (en `src/utils.py`) optimiza la inserción extrayendo las cédulas y haciendo una "Bulk Query" para minimizar las consultas a la base de datos, asociándolos luego al periodo electoral actual.

## 6. Lógica Crítica: Emisión de Votos

El proceso de sufragio se maneja en el Blueprint `voting` (`src/voting/routes.py`).

1. **Validación de Periodo:** Verifica que el periodo (`ElectionPeriod`) exista y esté marcado como `is_active=True`.
2. **Validación de Participación:** Consulta la tabla `VoterParticipation` buscando un registro previo que coincida con `current_user.voter_id` y `election_period_id`. Si existe, se rechaza la operación.
3. **Registro Anónimo:** Si pasa las validaciones, se insertan dos registros independientes: 
   - Un registro en `VoterParticipation` para asentar la comparecencia del elector.
   - Un registro en `Vote` relacionando el periodo y la lista seleccionada. Se hace el `db.session.commit()`.

## 7. Pruebas y Despliegue

### Pruebas (Testing)
El directorio `tests/` utiliza la librería `pytest` junto con un fixture (en `conftest.py`) que levanta una base de datos SQLite temporal en memoria (`sqlite:///:memory:`) para asegurar que las pruebas sean rápidas, aisladas y no afecten los datos de desarrollo o producción.

### Base de Datos y Migraciones
Los cambios en los modelos de base de datos se propagan mediante Flask-Migrate:
```bash
flask db migrate -m "Mensaje del cambio"
flask db upgrade
```

### Configuración (config.py y .env)
El entorno debe proveer:
- `SECRET_KEY`: Llave de encriptación para cookies y sesiones.
- `DATABASE_URL`: URI de conexión a la base de datos.
