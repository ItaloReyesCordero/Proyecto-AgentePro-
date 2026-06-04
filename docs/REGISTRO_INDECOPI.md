# Paquete de registro de obra ante INDECOPI — AgentePro

> **Para qué sirve este documento:** reúne, en orden, todo lo que necesitas para
> registrar tu software como **obra (programa de ordenador)** ante el
> **INDECOPI – Dirección de Derecho de Autor (DDA)**. Copia/pega de aquí al
> formulario y adjunta los anexos que se indican.

---

## ⚠️ Lo primero: patente vs. derecho de autor

En el Perú **el software NO se patenta**. La patente de invención (Dirección de
Invenciones y Nuevas Tecnologías) **excluye expresamente** al "programa de ordenador
como tal". La vía correcta y la que sí te aceptan es:

- **Registro de obra — Programa de ordenador (software)**, en la
  **Dirección de Derecho de Autor (DDA)** de INDECOPI.
- Base legal: **Decreto Legislativo N.º 822** (Ley sobre el Derecho de Autor) y la
  Decisión Andina 351. El software se protege como **obra literaria**.

El derecho de autor **nace con la creación** de la obra (no necesitas registrarla para
ser el titular). El registro te da **prueba oficial con fecha cierta**, indispensable
si alguien te copia, o si vendes/licencias/levantas inversión.

---

## 1. Datos de la obra (para el formulario)

| Campo | Valor |
|---|---|
| **Título de la obra** | AgentePro |
| **Tipo de obra** | Programa de ordenador (software) |
| **Clase** | Obra literaria (software) |
| **¿Obra originaria o derivada?** | Originaria |
| **¿Inédita o publicada?** | (Elige según corresponda; si aún no la has comercializado/publicado, marca *inédita*) |
| **Año de creación** | 2026 |
| **País de origen** | Perú |
| **Lenguajes de programación** | Python (backend), TypeScript/JavaScript (frontend), SQL |

## 2. Datos del autor y titular

| Campo | Valor |
|---|---|
| **Autor** | Italo Eduardo Reyes Cordero |
| **Titular de los derechos patrimoniales** | Italo Eduardo Reyes Cordero (mismo autor) |
| **Documento de identidad** | DNI N.º 75220834 |
| **Domicilio** | Jr. Grau N.º 419, distrito de Jauja, provincia de Jauja, departamento de Junín |
| **Correo** | italoreyescordero1@gmail.com |
| **Teléfono** | 916085873 |
| **Nacionalidad** | Peruana |

> Si en el futuro creas una empresa (E.I.R.L./S.A.C.) y quieres que la titularidad sea
> de la empresa, se registra una **cesión de derechos** del autor a la empresa. Por
> ahora conviene registrar a tu nombre como persona natural.

## 3. Resumen / descripción de la obra (pégalo en el formulario)

> **AgentePro** es una plataforma de software como servicio (SaaS) multi-empresa
> (multi-tenant) que automatiza la atención al cliente y la gestión comercial de
> negocios mediante inteligencia artificial. Cada negocio cliente recibe, de forma
> automática, un agente conversacional de WhatsApp con IA que responde 24/7, un agente
> de voz telefónica, sincronización con un CRM, automatizaciones de seguimiento de
> clientes potenciales (leads), un generador de contenido para Instagram y un panel de
> control (dashboard) unificado en tiempo real.
>
> La obra comprende: (a) el **código fuente del backend**, desarrollado en Python con
> el framework FastAPI y comunicación en tiempo real vía Socket.io, que implementa la
> lógica de negocio, el aislamiento de datos entre empresas, la integración con
> servicios externos (modelos de IA, mensajería, telefonía, CRM, almacenamiento) y los
> webhooks de integración; (b) el **código fuente del frontend**, desarrollado en
> React con TypeScript, que implementa la interfaz de usuario, el panel del negocio y
> el panel de superadministración; (c) el **esquema de base de datos** y sus
> migraciones; y (d) la **arquitectura** y documentación técnica que la acompaña.
>
> El elemento original y distintivo de la obra es su arquitectura multi-empresa con
> aislamiento de datos forzado a nivel de aplicación, el aprovisionamiento automático
> de los canales de cada negocio (mensajería, voz, redes sociales) y la orquestación de
> un motor de inteligencia artificial para responder, calificar y dar seguimiento a los
> clientes de cada negocio.

## 4. Magnitud de la obra (referencia técnica)

| Componente | Tecnología | Tamaño aprox. |
|---|---|---|
| Backend | Python / FastAPI / SQLAlchemy / Socket.io | ~129 archivos · ~9,958 líneas |
| Frontend | React 19 / TypeScript / Vite | ~55 archivos · ~4,951 líneas |
| Base de datos | PostgreSQL (17 modelos de datos) + migraciones Alembic | — |
| **Total estimado** | — | **~15,000 líneas de código fuente** |

Módulos/modelos de datos principales: `tenant`, `user`, `subscription`, `contact`,
`conversation`, `message`, `call`, `call_summary`, `agent_config`, `voice_config`,
`instagram_post`, `automation`, `automation_run`, `hubspot_sync_log`, `webhook_log`,
`password_reset`.

## 5. Anexos a presentar (lo que adjuntas)

INDECOPI **no exige todo el código fuente**. Lo habitual para un programa de ordenador:

1. **Formato de solicitud de registro** de obra (lo descargas del portal de INDECOPI o
   lo llenas en mesa de partes / Mesa de Partes Virtual).
2. **Comprobante de pago de la tasa** (ver TUPA vigente; el costo del registro de obra
   es bajo — del orden de unas decenas de soles. Verifica el monto exacto al momento de
   tramitar).
3. **Copia del DNI** del autor.
4. **Ejemplar de la obra**: para software se entrega un **extracto representativo del
   código fuente** — habitualmente las **primeras 10 y últimas 10 páginas** impresas (o
   en CD/USB/PDF), con un identificador en cada página. (Confirma el formato exacto con
   la DDA al presentar; algunas sedes piden CD, otras aceptan PDF por Mesa de Partes
   Virtual.)
5. Este documento como **memoria descriptiva** (opcional pero recomendado).

> Sugerencia para el extracto de código: imprime los archivos núcleo que mejor
> representan la originalidad de la obra, por ejemplo: `backend/app/main.py`,
> `backend/app/core/tenant_scope.py` (aislamiento multi-empresa),
> `backend/app/services/provisioning/` (aprovisionamiento automático),
> `backend/app/services/ai/` (orquestación de IA) y `frontend/src/App.tsx`.

## 6. Cómo presentarlo (pasos)

1. Entra al portal de **INDECOPI** → **Derecho de Autor** → **Registro de obra**
   (presencial en sede o por **Mesa de Partes Virtual**).
2. Selecciona la modalidad **"Programa de ordenador / software"**.
3. Llena la solicitud con los datos de las secciones **1 y 2** de este documento.
4. Paga la tasa (TUPA) y guarda el comprobante.
5. Adjunta los anexos de la sección **5**.
6. Presenta. Te asignan un expediente y, al aprobarse, emiten el **certificado de
   registro** con número y fecha — esa es tu prueba oficial de autoría.

## 7. Buenas prácticas de evidencia (mientras tramitas)

- Guarda este repositorio con su **historial** (fechas de creación de archivos).
- Conserva los correos/recibos de servicios usados durante el desarrollo (fechan tu
  trabajo).
- El aviso de copyright ya está en el `README.md` y se recomienda repetirlo como
  cabecera en los archivos fuente principales (queda como tarea opcional; ver el plan).

---

**Datos del autor ya completados** (DNI 75220834, domicilio en Jauja–Junín, teléfono 916085873).
Solo queda **decidir si la obra se declara *inédita* o *publicada*** al llenar el formulario.
