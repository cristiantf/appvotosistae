# Investigación: Sistemas de Votación Electrónica en Educación Superior — Ecuador

> **Fecha de investigación:** Junio 2026  
> **Contexto:** Proyecto ISTAE — Sistema de Votación Electrónica

---

## 1. Marco Normativo y Legal

### 1.1. Ley Orgánica de Educación Superior (LOES)

La **LOES** es el instrumento jurídico principal que regula los procesos electorales dentro de las instituciones de educación superior (IES) en Ecuador. Establece los siguientes principios fundamentales:

| Principio | Descripción |
|---|---|
| **Voto universal** | Todos los miembros habilitados del padrón tienen derecho a votar |
| **Voto directo** | Sin intermediarios ni representantes delegados |
| **Voto secreto** | Garantía de anonimato del sufragante |
| **Voto obligatorio** | Para miembros habilitados en el padrón electoral |
| **Paridad de género** | Equidad obligatoria y alternancia en la conformación de listas |

### 1.2. Autonomía Universitaria

La LOES y la Constitución de Ecuador reconocen la **autonomía responsable** de las IES para gestionar sus procesos electorales internos. Esto implica:

- **No existe una plataforma nacional única**: cada institución define su propio sistema, reglamento y modalidad.
- Las instituciones, a través de sus **Consejos Universitarios / Órganos Colegiados Superiores (OCS)**, determinan si las elecciones serán presenciales o electrónicas.
- Cada IES debe contar con un **Reglamento de Elecciones** aprobado por su OCS.

### 1.3. Entidades Reguladoras

| Entidad | Rol |
|---|---|
| **Consejo de Educación Superior (CES)** | Regulación general del sistema de educación superior. Puede disponer nuevas elecciones en caso de irregularidades. |
| **Consejo Nacional Electoral (CNE)** | Puede intervenir a petición de parte para realizar veedurías y brindar asesoría técnica en procesos electorales universitarios. |
| **SENESCYT** | Supervisión y coordinación general de la política pública de educación superior. |

### 1.4. Requisitos Legales para Representantes Estudiantiles

Según la LOES y los estatutos institucionales:

- **Promedio académico:** Equivalente a "Muy Bueno" (generalmente ≥70% de la calificación máxima).
- **Avance curricular:** Haber aprobado al menos el **50% de la malla curricular**.
- **Plan de trabajo:** Presentar una propuesta formal para la dignidad a la cual se postula.
- **Reelección:** Permitida **una sola vez**, consecutiva o no.

### 1.5. Participación Estudiantil en el Cogobierno

- La votación estudiantil para elección de autoridades (rector, vicerrector) equivale a un porcentaje entre el **10% y el 25%** del total del personal académico con derecho a voto.
- La designación de autoridades académicas **no se realiza mediante elecciones universales** del estudiantado, sino conforme al estatuto de cada institución.

---

## 2. Modalidades de Votación

### 2.1. Voto Electrónico por Internet

- Permite el sufragio remoto desde cualquier ubicación.
- Requiere autenticación robusta (correo institucional, enlaces dinámicos únicos, tokens).
- Facilita la participación masiva sin necesidad de recintos presenciales.

### 2.2. Voto en Urna Electrónica

- Se realiza de forma presencial utilizando equipos informáticos en recintos electorales.
- Combina la seguridad del entorno controlado con la agilidad del conteo electrónico.

### 2.3. Voto Presencial Tradicional

- Papeleta física depositada en urna.
- Conteo manual.
- Aún utilizado en algunas instituciones, especialmente las más pequeñas.

---

## 3. Experiencias de Universidades Ecuatorianas

### 3.1. Universidad de Cuenca (UCuenca)

| Aspecto | Detalle |
|---|---|
| **Plataforma** | **UDECIDE** (desarrollada por CEDIA) |
| **Tecnología** | Blockchain para integridad, seguridad y anonimato |
| **Autenticación** | Correo institucional + enlaces dinámicos únicos |
| **Proveedores externos** | EVoting (empresa especializada en participación electrónica académica) |

### 3.2. Escuela Politécnica Nacional (EPN)

| Aspecto | Detalle |
|---|---|
| **Enfoque** | Proyectos de desarrollo interno y tesis de grado |
| **Arquitectura** | Modelo-Vista-Controlador (MVC) |
| **Tecnologías** | Angular (frontend) + .NET Framework (backend) + SQL Server (BD) |
| **Seguridad** | Firma ciega RSA + investigaciones con Blockchain |

### 3.3. Escuela Superior Politécnica del Litoral (ESPOL)

| Aspecto | Detalle |
|---|---|
| **Enfoque** | Prototipos de aplicaciones móviles y web |
| **Tecnologías** | Flutter (multiplataforma) + Blockchain Ethereum |
| **Objetivo** | Sufragio remoto y seguro, superando limitaciones presenciales |
| **Seguridad** | Descentralización del conteo de votos mediante Blockchain |

### 3.4. Universidad Estatal Amazónica (UEA)

| Aspecto | Detalle |
|---|---|
| **Sistema** | **UEA Elecciones** (desarrollo propio) |
| **Framework** | Yii2 (PHP) |
| **Base de datos** | MySQL |
| **Autenticación** | Active Directory / LDAP (cuentas institucionales) |

### 3.5. Otras Instituciones

- Muchas universidades e IST recurren a **aplicaciones web a medida**, frecuentemente desarrolladas como **proyectos de titulación**.
- Se utilizan metodologías ágiles como **Scrum** o **Extreme Programming (XP)**.
- Tendencia creciente hacia **Blockchain** y autenticación mediante **LDAP** con correos institucionales.

---

## 4. Requisitos Técnicos para Sistemas de Votación Electrónica

Según la normativa y las mejores prácticas identificadas, un sistema de votación electrónica para IES debe cumplir con:

### 4.1. Seguridad

- [x] Cifrado de datos en tránsito (HTTPS/TLS) y en reposo
- [x] Autenticación robusta (credenciales únicas por votante)
- [x] Prevención de voto múltiple
- [x] Protección contra ataques comunes (SQL Injection, XSS, CSRF)
- [ ] Firma digital o hash de integridad del voto (avanzado)
- [ ] Registro inmutable / Blockchain (avanzado)

### 4.2. Transparencia

- [x] Registro de auditoría de acciones administrativas
- [x] Generación de resultados verificables
- [x] Dashboard de resultados con gráficos
- [ ] Auditoría independiente por Tribunal Electoral

### 4.3. Funcionalidad Electoral

- [x] Gestión de períodos electorales (crear, activar, desactivar)
- [x] Carga masiva de padrones electorales (CSV/Excel)
- [x] Gestión de listas y candidatos con imágenes
- [x] Emisión de voto único por período
- [x] Visualización de resultados

### 4.4. Usabilidad

- [x] Interfaz intuitiva para votantes
- [x] Panel de administración completo
- [ ] Accesibilidad (WCAG 2.1)
- [ ] Diseño responsivo (móvil-first)
- [ ] Soporte multi-idioma (español nativo)

---

## 5. Tecnologías Comúnmente Utilizadas

| Categoría | Tecnologías |
|---|---|
| **Backend** | Python/Flask, PHP/Yii2, .NET, Node.js |
| **Frontend** | Bootstrap, Angular, React, Flutter |
| **Base de datos** | MySQL, PostgreSQL, SQL Server, SQLite |
| **Autenticación** | LDAP/Active Directory, OAuth2, JWT, correo institucional |
| **Seguridad avanzada** | Blockchain (Ethereum), firma ciega RSA, hashing SHA-256 |
| **Plataformas dedicadas** | UDECIDE (CEDIA), EVoting |

---

## 6. Fuentes y Referencias

1. Ley Orgánica de Educación Superior (LOES) — Asamblea Nacional del Ecuador
2. Consejo de Educación Superior (CES) — ces.gob.ec
3. Consejo Nacional Electoral (CNE) — cne.gob.ec
4. Universidad de Cuenca — Plataforma UDECIDE / CEDIA
5. ESPOL — Repositorio institucional (tesis de voto electrónico)
6. EPN — Repositorio institucional (proyectos de automatización electoral)
7. Universidad Estatal Amazónica — Sistema UEA Elecciones
8. EVoting — evoting.ec / evoting.com
