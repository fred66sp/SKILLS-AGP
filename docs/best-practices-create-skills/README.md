# Buenas prácticas para crear skills de agente

Esta guía explica cómo escribir skills de nivel profesional para agentes, validarlas con LLM y mantener una ventana de contexto ajustada.

Esta guía es un conjunto concentrado de buenas prácticas para crear skills de agente. Si buscas documentación exhaustiva, consulta [la documentación de Claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**Referencia estricta:** [agentskills.io](https://agentskills.io/). Esta guía la resume y añade pruebas de validación; la especificación es la que manda.

**Para evaluar si tus skills funcionan bien y evitar regresiones, revisa [skillgrade](https://github.com/mgechev/skillgrade).**

## Estructura de una skill

Toda skill debe seguir esta estructura de directorios:

Texto plano

```
skill-name/
├── SKILL.md              # Obligatorio: metadatos + instrucciones centrales (<500 líneas)
├── scripts/              # Código ejecutable (Python/Bash) diseñado como CLIs minúsculas
├── references/           # Contexto complementario (esquemas, cheatsheets)
└── assets/               # Plantillas o archivos estáticos usados en la salida
```

* **SKILL.md:** actúa como el "cerebro". Úsalo para la navegación y los procedimientos de alto nivel.  
* **references:** enlázalos directamente desde SKILL.md. Mantenlos **a un único nivel de profundidad**.  
* **scripts:** úsalos para operaciones frágiles o repetitivas donde la variación es un error. **No empaquetes aquí código de librería**;

## Optimiza el frontmatter para el descubrimiento

El `name` y la `description` del frontmatter de tu `SKILL.md` son los únicos campos que el agente ve antes de disparar una skill. Si no están optimizados para el descubrimiento y no son lo bastante específicos, tu skill es invisible.

* **Respeta una nomenclatura estricta:** el campo name debe tener entre 1 y 64 caracteres, contener solo letras minúsculas, números y guiones (sin guiones consecutivos) y **debe coincidir exactamente con el nombre del directorio padre** (por ejemplo, name: `angular-testing` debe residir en `angular-testing/SKILL.md`).  
* **Escribe descripciones optimizadas para el disparo:** (máximo 1024 caracteres). Son los únicos metadatos que el agente ve para el enrutamiento. Describe la capacidad en tercera persona e incluye "disparadores negativos".  
  * **Mal:** "React skills." (demasiado vago).
  * **Bien:** "Creates and builds React components using Tailwind CSS. Use when the user wants to update component styles or UI logic. Don't use it for Vue, Svelte, or vanilla CSS projects."

## Divulgación progresiva y gestión de recursos

Mantén una ventana de contexto impecable cargando información solo cuando sea necesario. **SKILL.md** es el "cerebro" de la lógica de alto nivel; delega los detalles en subdirectorios.

* **Mantén SKILL.md ligero:** limita el archivo principal a **\<500 líneas**. Úsalo para la navegación y los procedimientos principales.  
* **Usa subdirectorios planos:** mueve el contexto voluminoso a carpetas estándar. Mantén los archivos exactamente **a un nivel de profundidad** (por ejemplo, `references/schema.md`, no `references/db/v1/schema.md`).  
  * `references/`: documentación de API, cheatsheets, lógica de dominio.  
  * `scripts/`: código ejecutable para tareas deterministas.  
  * `assets/`: plantillas de salida, esquemas JSON, imágenes.  
* **Carga justo a tiempo (JiT):** indica explícitamente al agente cuándo debe leer un archivo. No verá estos recursos hasta que se lo indiques (por ejemplo, *"Consulta `references/auth-flow.md` para los códigos de error concretos"*).  
* **Rutas explícitas:** usa siempre **rutas relativas a la carpeta de la skill** con barras inclinadas (`/`), independientemente del sistema operativo. Pi resuelve una ruta relativa contra el directorio del `SKILL.md`, no contra el directorio de trabajo.

Las skills son para agentes, no para personas. El fin es mantener la ventana de contexto ajustada y evitar un consumo innecesario de tokens. **No crees:**

* **Archivos de documentación:** `README.md`, `CHANGELOG.md` o `INSTALLATION_GUIDE.md`.  
* **Lógica redundante:** si el agente ya resuelve una tarea de forma fiable sin ayuda, elimina la instrucción.  
* **Código de librería:** las skills deben referenciar herramientas existentes o contener scripts minúsculos de un solo propósito. El código de librería de larga vida pertenece a los directorios CLI estándar del repositorio.

## Usa instrucciones procedimentales específicas en lugar de prosa

Crea instrucciones para LLM, no para personas.

* **Usa numeración paso a paso:** define el flujo de trabajo como una secuencia cronológica estricta. Si hay un árbol de decisión, mapéalo con claridad (por ejemplo, *"Paso 2: si necesitas mapas de código fuente, ejecuta `ng build --source-map`. En caso contrario, salta al paso 3."*).  
* **Aporta plantillas concretas:** los agentes hacen coincidencia de patrones excepcionalmente bien. En lugar de gastar párrafos describiendo cómo debería verse una salida JSON, coloca una plantilla en la carpeta assets/ e indica al agente que copie su estructura.  
* **Escribe en imperativo y en tercera persona:** formula las instrucciones como órdenes directas al agente (por ejemplo, *"Extrae el texto..."* en lugar de *"Voy a extraer..."* o *"Deberías extraer..."*).

Sé específico y coherente en cómo referencias los conceptos en los archivos de tu skill.

* **Usa terminología idéntica:** elige un único término para referirte a un concepto concreto.  
* **Especificidad**: usa la terminología más específica y propia del dominio que describes. Por ejemplo, en Angular usa el concepto "template" en lugar de "html", "markup" o "view".

## Incluye scripts deterministas para operaciones repetitivas

No pidas al LLM que escriba lógica de análisis compleja o código repetitivo desde cero cada vez que ejecuta una skill.

* **Delega las tareas frágiles o repetitivas:** si el agente necesita analizar un conjunto de datos complejo o consultar una base de datos concreta, dale un script probado de Python, Bash o Node para ejecutar desde el directorio scripts/.  
* **Gestiona los casos límite con elegancia:** un agente se apoya en la salida estándar (stdout/stderr) para saber si un script ha funcionado. Escribe scripts que devuelvan mensajes de error muy descriptivos y legibles, para que el agente sepa exactamente cómo autocorregirse sin necesidad de intervención del usuario.

## Composición de skills

Puedes componer skills (también conocidas como skills enrutadoras) si quieres incluir una skill de forma condicional o crear una skill compuesta por subskills. Ejemplo:

```
---
name: build-project
description: ...
---

## Descripción general
...

## Objetivos de compilación

### Cliente

Para compilar el cliente en un binario desplegable, consulta [ruta a las skills].

### Servidor

Para compilar el servidor en un binario desplegable, consulta [ruta a la skill].

...
```

# Guía de validación

Como los LLM van a usar tus skills, la mejor forma que he identificado de asegurar que son útiles es hacerlo en colaboración con LLM.

Es fundamental tener evaluaciones de tus skills para asegurar que los cambios que haces tienen un impacto positivo y no introducen regresiones. Un benchmark popular para skills es [SkillsBench](https://arxiv.org/abs/2602.12670), que puede servirte de inspiración.

Cuando tengas redactada la versión inicial de tus skills, puedes validar tu trabajo siguiendo estos pasos:

### Validación del descubrimiento

Los agentes cargan las skills basándose estrictamente en el frontmatter YAML. Prueba cómo interpreta un LLM tu descripción de forma aislada, para evitar falsos disparos (por ejemplo, que se active para una aplicación React cuando está pensada para Angular).

Pega exactamente el texto siguiente en un chat de LLM nuevo:

> Estoy creando una Agent Skill basada en la especificación de agentskills.io. Los agentes decidirán si cargan esta skill basándose enteramente en los metadatos YAML de abajo.
>
> ```
> name: angular-vite-migrator
> description: Migrates Angular CLI projects from Webpack to Vite and esbuild. Use when the user wants to update builder configurations, replace webpack plugins with rollup equivalents, or speed up Angular compilation.
> ```
>
> Basándote estrictamente en esta descripción:
> 1. Genera 3 prompts de usuario realistas que con total seguridad deberían disparar esta skill.
> 2. Genera 3 prompts de usuario que suenen parecido pero que NO deberían disparar esta skill (por ejemplo, migrar una aplicación React a Vite o simplemente actualizar versiones de Angular).
> 3. Critica la descripción: ¿es demasiado amplia? Propón una reescritura optimizada.

Además, encarga a los agentes tareas que esperas que disparen la lectura de una skill e inspecciona su proceso de razonamiento. Itera con el agente para identificar por qué eligió (o no) determinadas skills.

### Validación de la lógica

Asegúrate de que tus instrucciones paso a paso son deterministas y no fuerzan al agente a alucinar pasos que faltan.

Entrega al LLM tu `SKILL.md` completo y el árbol de directorios:

> Aquí tienes el borrador completo de mi SKILL.md y el árbol de directorios de sus archivos de apoyo.
> 
> ```
> ├── SKILL.md
> ├── scripts/esbuild-optimizer.mjs
> └── assets/vite.config.template.ts
> ```
> 
> [Pega aquí el contenido de tu SKILL.md]
> Actúa como un agente autónomo que acaba de disparar esta skill. Simula tu ejecución paso a paso ante la petición "Migra mi aplicación Angular v17 a Vite".
>
> Para cada paso, escribe tu monólogo interno:
> 1. ¿Qué estás haciendo exactamente?
> 2. ¿Qué archivo o script concreto estás leyendo o ejecutando?
> 3. Señala cualquier bloqueo de ejecución: indica la línea exacta en la que te ves obligado a adivinar o alucinar porque mis instrucciones son ambiguas (por ejemplo, cómo mapear los archivos de entorno de Angular a import.meta.env de Vite).

### Pruebas de casos límite

Fuerza al LLM a buscar vulnerabilidades, configuraciones no soportadas y estados de fallo propios de las herramientas web.

Pide al LLM que ataque tu lógica:

> Ahora cambia de rol. Actúa como un probador de QA implacable. Tu objetivo es romper esta skill.
> Hazme entre 3 y 5 preguntas muy específicas y exigentes sobre casos límite, estados de fallo o respaldos ausentes en el SKILL.md. Céntrate en:
>
> * ¿Qué ocurre si `scripts/esbuild-optimizer.mjs` falla por una dependencia CommonJS heredada?
> * ¿Qué ocurre si el `angular.json` del usuario contiene builders de Webpack muy personalizados (`@angular-builders/custom-webpack`) que Vite no soporta?
> * ¿Hay suposiciones implícitas sobre el entorno Node del usuario que yo haya asumido?
>
> No corrijas estos problemas todavía. Hazme solo las preguntas numeradas y espera a que las responda.

### Refinamiento de la arquitectura

A menudo los LLM intentan meter archivos de configuración grandes directamente en el prompt principal. Usa este paso para imponer la divulgación progresiva y reducir el consumo de tokens.

Pide al LLM que aplique tus correcciones y reestructure la skill:

> A partir de mis respuestas a tus preguntas sobre casos límite, reescribe el archivo SKILL.md aplicando estrictamente el patrón de diseño de divulgación progresiva:
>
> 1. Mantén el `SKILL.md` principal estrictamente como un conjunto de pasos de alto nivel, con comandos en imperativo y tercera persona (por ejemplo, Ejecuta el script de esbuild, Lee la plantilla de configuración de Vite).
> 2. Si hay reglas densas, plantillas grandes de `vite.config.ts` o esquemas complejos de `angular.json` que ahora mismo están en el archivo, elimínalos. Indícame que cree un archivo nuevo en `references/` o `assets/`, y sustituye el texto de `SKILL.md` por una orden estricta de leer ese archivo concreto solo cuando sea necesario.
> 3. Añade al final una sección dedicada a la gestión de errores que incorpore mis respuestas sobre los respaldos de Webpack y la resolución de CommonJS.
