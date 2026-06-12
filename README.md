# Sistema de Votación con Flask

Este proyecto es una aplicación web de votación construida con el micro-framework de Python, Flask. Permite a los administradores gestionar elecciones y a los usuarios emitir sus votos de forma segura.

## Características Principales

- **Gestión Avanzada y Seguridad:**
  - Roles avanzados con jerarquía: Super Admin y Administrador.
  - Creación y gestión de períodos electorales con **automatización por fechas** y controles manuales de emergencia.
  - Carga masiva de padrones de votantes desde archivos Excel o CSV.
  - Sistema dinámico de Dignidades electorales.
  - Generación de **Actas Oficiales de Escrutinio en PDF** (`fpdf2`).
  - Registro anónimo de votos para garantizar secreto y transparencia.
  - Función de impersonación (`Login As`) para auditoría y soporte por Super Admins.

- **Plataforma de Votación y Resultados:**
  - Interfaz UI/UX moderna, responsive y accesible basada en un diseño **Premium** de tarjetas e interacciones.
  - Iniciar sesión de forma segura con credenciales únicas.
  - Paneles de control temporizados con cuentas regresivas automáticas.
  - Visualización estructurada de las papeletas, incluyendo Voto Nulo y Voto en Blanco.
  - Dashboard interactivo de Resultados con `Chart.js` rediseñado y exportación PDF.
  - Emisión de voto único garantizado por sistema anti-doble voto.

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
