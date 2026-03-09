# Sistema de Votación con Flask

Este proyecto es una aplicación web de votación construida con el micro-framework de Python, Flask. Permite a los administradores gestionar elecciones y a los usuarios emitir sus votos de forma segura.

## Características Principales

- **Gestión de Administradores:**
  - Crear y gestionar períodos electorales.
  - Cargar padrones de votantes desde archivos CSV.
  - Crear y asignar candidatos a listas dentro de un período electoral.

- **Plataforma de Votación para Usuarios:**
  - Iniciar sesión de forma segura con credenciales únicas.
  - Ver los períodos electorales disponibles.
  - Visualizar las listas y los candidatos de cada elección.
  - Emitir un voto único por período electoral.

## Primeros Pasos

Este proyecto está configurado para ejecutarse en un entorno de desarrollo Nix.

1.  **Instalación de dependencias:** El entorno virtual y las dependencias listadas en `requirements.txt` se instalan automáticamente al crear el espacio de trabajo. Si necesitas instalar las dependencias manualmente, activa el entorno virtual y ejecuta `pip`:

    ```bash
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Ejecución del servidor:** Las vistas previas deberían ejecutarse automáticamente al iniciar un espacio de trabajo. Simplemente sigue las instrucciones en la terminal para iniciar el servidor de desarrollo de Flask con el script `devserver.sh`.

## Pruebas Automatizadas

El proyecto incluye una suite de pruebas automatizadas para garantizar la calidad del código y prevenir regresiones. Para ejecutar las pruebas, sigue estos pasos:

1.  **Activa el entorno virtual:**
    ```bash
    source .venv/bin/activate
    ```

2.  **Ejecuta Pytest:**
    ```bash
    PYTHONPATH=. pytest
    ```
