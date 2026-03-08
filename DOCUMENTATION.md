# Documentación del Proyecto de Votación

## 1. Descripción General

Este proyecto es una aplicación web de votación desarrollada en Python utilizando el micro-framework Flask. La aplicación permite a los administradores gestionar todo el ciclo electoral, desde la creación de períodos y la carga de votantes hasta la gestión de listas y candidatos. Por otro lado, los usuarios (votantes) pueden iniciar sesión de forma segura para emitir su voto, garantizando que solo puedan votar una vez por elección.

## 2. Estructura del Proyecto

El proyecto sigue una estructura modular utilizando Blueprints de Flask para organizar la funcionalidad en componentes lógicos:

- `src/`: Contiene el código fuente principal de la aplicación.
    - `__init__.py`: Fábrica de la aplicación. Inicializa la aplicación Flask, las extensiones (SQLAlchemy, LoginManager, Migrate) y registra los Blueprints.
    - `models.py`: Define los modelos de la base de datos utilizando SQLAlchemy ORM.
    - `templates/`: Contiene las plantillas HTML para la interfaz de usuario.
    - `auth/`: Blueprint para la autenticación de usuarios.
    - `admin/`: Blueprint para toda la funcionalidad de administración.
    - `main/`: Blueprint para las rutas principales (página de inicio).
    - `voto/`: Blueprint para el proceso de votación del usuario final.
- `migrations/`: Contiene las migraciones de la base de datos generadas por Flask-Migrate.
- `instance/`: Carpeta para archivos de configuración de la instancia y la base de datos SQLite.
- `requirements.txt`: Lista de las dependencias de Python del proyecto.
- `devserver.sh`: Script para ejecutar el servidor de desarrollo de Flask.
- `main.py`: Punto de entrada que inicia la aplicación Flask.

## 3. Modelos de la Base de Datos (`src/models.py`)

- **`User`**: Representa a un usuario del sistema (administrador o votante).
- **`Voter`**: Almacena los datos de una persona habilitada para votar. Tiene una relación (`votes`) que permite acceder a todos los votos que ha emitido.
- **`ElectionPeriod`**: Representa un período electoral (ej. "Elecciones Estudiantiles 2024").
- **`CandidateList`**: Representa una lista o partido político dentro de un período electoral. Mantiene una relación (`candidates`) para acceder a todos sus candidatos.
- **`Candidate`**: Representa a un candidato individual que pertenece a una `CandidateList`.
- **`Vote`**: Registra un voto emitido por un `Voter` en un `ElectionPeriod` específico, asociado a un `Candidate`.

## 4. Funcionalidad de los Módulos

### 4.1. Autenticación (`src/auth`)

- **Creación de Administrador**: Permite crear el primer usuario administrador del sistema.
- **Inicio y Cierre de Sesión**: Gestiona las sesiones para todos los usuarios.

### 4.2. Administración (`src/admin`)

- **Gestión de Votantes**: Permite a un administrador cargar el padrón de votantes desde un archivo CSV.
- **Gestión Electoral Completa**: Ofrece funcionalidades CRUD (Crear, Leer, Actualizar, Borrar) para períodos electorales, listas de candidatos y candidatos, permitiendo una administración flexible.

### 4.3. Votación (`src/voto`)

- **Selección de Elección**: Muestra al votante los períodos electorales en los que aún no ha votado.
- **Emisión de Voto Informado**: Presenta las listas y sus respectivos candidatos de forma clara para que el votante pueda tomar una decisión. El sistema valida que el voto sea único por elección.

## 5. Dependencias Clave

- **`Flask`**: El framework web sobre el que se construye todo.
- **`Flask-SQLAlchemy`**: Para la interacción con la base de datos a través del ORM.
- **`Flask-Login`**: Para gestionar las sesiones de usuario y la autenticación.
- **`Flask-Migrate`**: Para gestionar las migraciones y la evolución del esquema de la base de datos.
- **`python-dotenv`**: Para gestionar variables de entorno de forma segura.
- **`pandas` y `openpyxl`**: Para la lectura y procesamiento de archivos CSV/Excel en la carga de votantes.
