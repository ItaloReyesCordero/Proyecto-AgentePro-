# 📒 Conectar Notion a AgentePro — Guía paso a paso (bien detallada)

Esta guía te lleva de la mano para que tu agente lea los **servicios y precios**
desde **Notion**. Cuando termines, cada vez que cambies un precio en Notion y le
des "Sincronizar", el agente responderá con los datos nuevos.

> ⏱️ Tiempo: unos 10 minutos la primera vez.
> 💡 Hazlo desde una **computadora** (no el celular), es mucho más fácil.

---

## 🧭 Resumen de lo que vas a hacer (los 5 grandes pasos)

1. **Crear tu tabla en Notion** con tus servicios y precios.
2. **Crear una "integración"** en Notion (es como una llave 🔑) y copiar su **Token**.
3. **Conectar esa llave a tu tabla** (paso que casi todos olvidan ⚠️).
4. **Copiar el enlace** de tu tabla.
5. **Pegar el Token y el enlace en AgentePro** y darle "Conectar".

---

## 🟦 PASO 1 — Crear tu tabla de servicios en Notion

1. Abre tu navegador (Chrome) y entra a **https://www.notion.so**
2. Inicia sesión con tu cuenta de Notion (si no tienes, crea una gratis: botón **Sign up**).
3. En la barra de la izquierda, pasa el mouse y haz clic en **➕ Add a page**
   (Agregar página). Se abre una página en blanco.
4. Escribe arriba un título, por ejemplo: **Servicios de mi negocio**.
5. Ahora vamos a meter una **tabla (base de datos)**. Escribe `/` (la tecla de la
   barra inclinada) y aparece un menú. Escribe `table` y elige **Table - Inline**
   (Tabla en línea). Aparece una tablita.
6. Esa tabla trae por defecto una columna llamada **Name** (Nombre) y otra **Tags**.
   Vamos a dejar estas **4 columnas** (puedes renombrar/crear haciendo clic en el
   título de cada columna → **Edit property**):

   | Columna (título)  | Tipo en Notion         | Para qué sirve                |
   |-------------------|------------------------|-------------------------------|
   | **Nombre**        | Title (la primera)     | El nombre del servicio        |
   | **Precio**        | Text o Number          | El precio                     |
   | **Descripción**   | Text                   | Detalle corto del servicio    |
   | **Categoría**     | Select o Text          | (opcional) tipo de servicio   |

   > Para cambiar el tipo de una columna: clic en el **título de la columna** →
   > **Edit property** → **Type** → elige Text, Number o Select.

7. Llena una fila por cada servicio. Ejemplo para una barbería:

   | Nombre              | Precio | Descripción                      | Categoría |
   |---------------------|--------|----------------------------------|-----------|
   | Corte de cabello    | 25     | Corte clásico a tijera o máquina | Cabello   |
   | Corte + barba       | 35     | Corte completo con perfilado     | Combo     |
   | Solo barba          | 15     | Perfilado y arreglo de barba     | Barba     |
   | Tinte               | 60     | Aplicación de color              | Color     |

   > 💵 El **Precio** puede ser número (`25`) o texto (`S/25`, `Desde S/50`,
   > `Consultar`). Las dos formas funcionan.

✅ Listo el Paso 1. Deja esta pestaña abierta, la usaremos al final.

---

## 🟦 PASO 2 — Crear la "llave" (integración) y copiar el Token

1. En **otra pestaña** del navegador, entra a:
   **https://www.notion.so/my-integrations**
2. Haz clic en el botón **+ New integration** (Nueva integración).
3. Te pide unos datos:
   - **Name** (Nombre): escribe `AgentePro`.
   - **Associated workspace**: elige tu espacio de trabajo (donde está tu tabla).
4. Haz clic en **Submit** (Enviar) / **Save**.
5. Te lleva a la página de la integración. Busca la sección
   **Internal Integration Secret** (o "Internal Integration Token").
   - Haz clic en **Show** (Mostrar) y luego en **Copy** (Copiar).
   - Es un texto largo que empieza con **`secret_`** o **`ntn_`**.
   - 📋 **Guárdalo** (pégalo temporalmente en un bloc de notas). Lo necesitarás en el Paso 5.

> 🔒 Este Token es **secreto**, como una contraseña. No lo compartas ni lo subas a
> ningún sitio público.

✅ Listo el Paso 2. Ya tienes la llave.

---

## 🟦 PASO 3 — Conectar la llave a tu tabla (⚠️ el más olvidado)

La llave que creaste **todavía no puede ver tu tabla**. Hay que darle permiso:

1. Vuelve a la pestaña de **tu tabla** (la del Paso 1).
2. Arriba a la **derecha** de la página, haz clic en el botón **•••**
   (tres puntitos).
3. En el menú que se abre, baja hasta **Connections** (Conexiones) o
   **+ Add connections**.
4. En el buscador escribe **AgentePro** (el nombre que le pusiste a la integración)
   y haz clic en él.
5. Sale una ventanita preguntando si confirmas → haz clic en **Confirm** (Confirmar).

> Si no haces este paso, AgentePro te dirá *"No se encontró la base de datos"* —
> porque la llave no tiene permiso para verla.

✅ Listo el Paso 3. Ahora la llave SÍ puede leer tu tabla.

---

## 🟦 PASO 4 — Copiar el enlace de tu tabla

1. Sigue en la pestaña de tu tabla.
2. Arriba a la derecha, haz clic en **Share** (Compartir) y luego en
   **Copy link** (Copiar enlace).
   - 👉 Alternativa: clic en **•••** (tres puntitos) → **Copy link**.
3. Te copia un enlace largo parecido a esto:
   `https://www.notion.so/Servicios-de-mi-negocio-2f1a9c8b7d6e4f0a9c8b7d6e4f0a1234?v=...`
4. 📋 Pégalo también en tu bloc de notas. **No tienes que recortarlo**: AgentePro saca
   solo lo que necesita del enlace completo.

✅ Listo el Paso 4. Ya tienes las **dos cosas**: el **Token** y el **enlace**.

---

## 🟩 PASO 5 — Pegarlo en AgentePro y conectar

1. Entra a tu panel de AgentePro: **http://localhost:5173** (o tu dominio cuando
   esté desplegado).
2. Inicia sesión con la cuenta **del negocio** (la del dueño, NO la de superadmin —
   el superadmin no tiene esta pantalla).
3. En el menú de la izquierda, haz clic en **Configuración** (el ícono de engranaje ⚙️).
4. Baja hasta la tarjeta que dice **"CRM en Notion"**.
5. Verás dos casillas:
   - **Token de integración (Notion)** → pega aquí el Token del **Paso 2**
     (el que empieza con `secret_` o `ntn_`).
   - **ID o enlace de la base de datos** → pega aquí el **enlace** del **Paso 4**
     (el enlace completo está bien).
6. Haz clic en el botón **Conectar y sincronizar**.
7. Espera unos segundos. Si todo está bien, aparece un mensaje verde arriba que dice
   algo como **"Notion conectado: 4 servicios sincronizados"** ✅.

🎉 ¡Listo! Tu agente ya tiene tus servicios y precios desde Notion.

---

## 🔁 Cuando cambies precios después

1. Edita tu tabla en Notion (cambia precios, agrega servicios, etc.).
2. Vuelve a AgentePro → **Configuración** → tarjeta **"CRM en Notion"**.
3. Haz clic en **Sincronizar ahora**. Listo, el agente ya usa lo nuevo.

> No necesitas reconectar el Token cada vez. Solo "Sincronizar ahora".

---

## 🧪 Cómo comprobar que funcionó

- En el panel: la tarjeta "CRM en Notion" mostrará **"Conectado"**, cuántos
  **servicios sincronizados** hay, y la **última sincronización**.
- En el chat de prueba del agente (o por WhatsApp si ya está conectado), pregunta:
  *"¿cuánto cuesta el corte?"* → debería responder con el precio de tu tabla.

> ⚠️ Para que el agente **responda por WhatsApp** necesita **saldo en Anthropic**.
> La conexión de Notion sí se hace sin eso, pero las respuestas del agente requieren
> ese saldo.

---

## ❓ Si algo sale mal (errores comunes)

| Mensaje / problema | Qué significa | Cómo arreglarlo |
|---|---|---|
| **"No se encontró la base de datos"** | La llave no tiene permiso sobre tu tabla | Repite el **Paso 3** (Connections → agregar AgentePro → Confirm) |
| **"...is a page, not a database"** | Pegaste el enlace de una página | Ya está resuelto: el sistema busca la tabla dentro de la página solo. Si aún falla, asegúrate de que la página tenga una **tabla** adentro y esté compartida con la integración (Paso 3) |
| **"Token de Notion inválido o sin permisos"** | El Token está mal copiado o incompleto | Vuelve al **Paso 2**, copia el Token completo de nuevo (empieza con `secret_`/`ntn_`) |
| **"0 servicios sincronizados"** | La tabla está vacía o no tiene columna de nombre | Asegúrate de tener filas con **Nombre** lleno (Paso 1) |
| **No veo la tarjeta "CRM en Notion"** | Entraste como superadmin | Cierra sesión y entra con la cuenta **del negocio** (dueño) |
| Precios salen raros al editarlos en el panel | El editor de "Agente IA" espera número | Es solo visual; el agente lee bien igual. Edita los precios en Notion y sincroniza |

---

## 📌 Cosas buenas que ya están cubiertas (no te preocupes por esto)

- Tu Token se guarda **cifrado** (encriptado); nadie lo ve, ni siquiera en los
  reportes del panel de superadmin.
- Cada negocio tiene **su propia** conexión de Notion (no se mezclan entre clientes).
- Si pones credenciales malas, **no se guarda nada a medias** (no se rompe).
- Lo sincronizado sirve **igual para WhatsApp y para las llamadas de voz**.
