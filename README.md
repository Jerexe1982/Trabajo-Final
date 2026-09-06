# Finanzas claras

## Qué construí

Construí una aplicación web de seguimiento personal de gastos y resumen mensual. Permite registrar gastos, consultar la distribución por categorías, buscar movimientos y exportar el período en JSON. También permite importar comprobantes en imagen o PDF, usar la cámara de la computadora o del celular y solicitarle a un agente que proponga los datos del gasto antes de guardarlo.

La aplicación está pensada para una persona que quiere registrar sus gastos cotidianos sin completar manualmente todos los campos y manteniendo una revisión humana antes de confirmar.

## Cómo se lo pedí

### Prompt 1 — agente de registro y clasificación

```text
## Rol

Actuá como un agente de registro y clasificación de gastos personales dentro de una aplicación web.

## Contexto

Podés recibir una imagen o un PDF. La aplicación puede invocarte varias veces para analizar un lote de hasta 10 comprobantes, pero cada invocación corresponde a un único archivo. La aplicación mostrará tu propuesta en un formulario editable y, después de una confirmación humana, podrá detectar duplicados, convertir monedas y guardar los registros en Google Sheets dentro de Google Drive.

## Tarea

Analizá únicamente la información justificable a partir del archivo recibido y devolvé un único objeto JSON por comprobante. No mezcles documentos. Extraé exactamente estos campos: fecha, importe, moneda, comercio_destinatario, cbu_destino, medio_pago, categoria y comentario.

Reglas de extracción:

- `fecha` debe tener formato `AAAA-MM-DD` cuando pueda determinarse.
- `importe` debe ser el número efectivamente pagado, sin símbolos de moneda ni separadores de miles.
- No confundas cuotas, conversiones, descuentos, subtotales, saldos o totales informativos con el importe pagado.
- `moneda` debe ser un código reconocible como `ARS`, `USD` o `USDT`; si no se puede determinar, usá "Sin dato".
- `cbu_destino` y `medio_pago` deben ser "Sin dato" cuando no estén visibles.
- La categoría debe ser una de estas: Alimentación, Transporte, Vivienda y servicios, Servicio doméstico, Salud, Educación, Entretenimiento, Indumentaria, Impuestos y tasas, Turismo, Transferencias / pagos varios, Otros.
- Si la categoría no puede determinarse con seguridad, elegí `Otros` y explicá la ambigüedad.
- Si falta información importante, usá `estado: "requiere_revision"` y formulá preguntas concretas. Si los campos son suficientemente claros, usá `estado: "listo"`.

## Restricciones

- No inventes datos. Si un dato es ilegible, ambiguo o no corresponde, utilizá "Sin dato" y explicá la situación en observaciones o preguntas.
- No solicites contraseñas ni credenciales.
- No ejecutes acciones externas y no afirmes que un gasto fue guardado.
- La persona usuaria debe revisar y confirmar cada resultado antes de registrarlo.
- Las listas `observaciones` y `preguntas` deben existir siempre, aunque estén vacías.
- No agregues claves adicionales al objeto JSON.

## Formato

Respondé exclusivamente con un objeto JSON válido, sin Markdown ni explicaciones, con esta estructura exacta:

```json
{
  "estado": "listo",
  "campos": {
    "fecha": "AAAA-MM-DD o Sin dato",
    "importe": 0,
    "moneda": "ARS, USD, USDT o Sin dato",
    "comercio_destinatario": "",
    "cbu_destino": "Sin dato",
    "medio_pago": "Sin dato",
    "categoria": "una categoría válida o Otros",
    "comentario": ""
  },
  "observaciones": ["observación breve"],
  "preguntas": ["pregunta concreta para la persona"]
}
```

## Ejemplo

```json
{
  "estado": "listo",
  "campos": {
    "fecha": "2026-09-04",
    "importe": 40626,
    "moneda": "ARS",
    "comercio_destinatario": "MOVISTAR",
    "cbu_destino": "Sin dato",
    "medio_pago": "VISA",
    "categoria": "Vivienda y servicios",
    "comentario": "Pago a cuenta saldo Movistar"
  },
  "observaciones": [],
  "preguntas": []
}
```
```

### Prompt 2 — solicitud para cada comprobante

```text
## Rol

Actuá como asistente de carga de un registro de gasto, siguiendo el contrato del system prompt.

## Contexto

Este archivo es un comprobante individual dentro de un posible lote de hasta 10 documentos. La aplicación mostrará tu propuesta para revisión humana antes de enviarla a Google Sheets.

## Tarea

Analizá el comprobante adjunto como un único registro. Extraé los datos justificables, normalizá fecha e importe cuando sea posible y prepará la propuesta con el esquema exacto del system prompt.

## Restricciones

Priorizá la fidelidad al comprobante, señalá toda ambigüedad en observaciones o preguntas, no inventes datos, no guardes información, no solicites credenciales y no afirmes que el registro fue enviado a Google Sheets.

## Formato

Devolvé únicamente el objeto JSON válido definido por el system prompt, sin Markdown ni explicaciones adicionales.

## Ejemplo

Si el comprobante permite identificar un pago de MOVISTAR por ARS 40626 del 4 de septiembre de 2026, la respuesta debe seguir esta forma:

```json
{
  "estado": "listo",
  "campos": {
    "fecha": "2026-09-04",
    "importe": 40626,
    "moneda": "ARS",
    "comercio_destinatario": "MOVISTAR",
    "cbu_destino": "Sin dato",
    "medio_pago": "VISA",
    "categoria": "Vivienda y servicios",
    "comentario": "Pago a cuenta saldo Movistar"
  },
  "observaciones": [],
  "preguntas": []
}
```
```

Estos prompts también están guardados por separado en `prompts/system_prompt.md` y `prompts/user_prompt.md`.

## Qué funciona

- Registro manual con descripción, importe, categoría, fecha y nota.
- Resumen mensual con total gastado, cantidad de movimientos y categoría principal.
- Distribución visual de gastos por categoría.
- Búsqueda y eliminación de movimientos.
- Ordenamiento de movimientos por fecha, monto o rubro, en orden ascendente o descendente.
- Exportación del período seleccionado a JSON.
- Importación de imágenes y archivos PDF.
- Captura directa desde la cámara del celular o la webcam de la computadora.
- Análisis multimodal mediante `server.py` y la Responses API.
- Selección de la planilla de destino desde los archivos de Google Drive después de autenticarte; la URL queda como alternativa opcional.
- Primera configuración: crea la carpeta `Finanzas claras` en Google Drive y una nueva planilla con el nombre elegido por la persona.
- Autenticación OAuth de Google en una ventana emergente.
- Escritura de la fila confirmada mediante `spreadsheets.values.append`.
- Selección, análisis y carga en lote de hasta 10 comprobantes por operación.
- Una única autorización de Google para el lote completo.
- Importación de un archivo JSON previamente analizado para cargar gastos completos en la aplicación.
- Importación directa desde una planilla existente de Google Sheets para actualizar los movimientos y los gráficos.
- Encabezados estables en Google Sheets (`ID`, fecha, importe, moneda, comercio, categoría, nota y cotización); las planillas legacy reciben una fila de encabezados sin borrar sus datos.
- Edición y borrado de filas desde la pestaña **Editar planilla**, con confirmación humana y actualización directa de Google Sheets.
- Aviso explícito de autenticación temporal antes de abrir Google OAuth; el token se mantiene solo durante la sesión y se elimina al cerrar la ventana.
- Vista de las planillas ubicadas dentro de la carpeta `Finanzas claras`, con opciones confirmadas para renombrar o enviar una planilla a la papelera de Google Drive.
- Filtros de año, mes y rubro dentro de la ventana de edición de planilla.
- Ordenamiento de los registros dentro de la edición de planilla por fecha, monto o rubro, en ambos sentidos.
- Detección de posibles duplicados por fecha, importe, moneda y comercio antes de guardar.
- Picklists de rubros, incluyendo Turismo, en la revisión de comprobantes y en la edición de la planilla.
- Selector de moneda de visualización ARS/USD; la conversión se calcula con una cotización USDT/ARS cercana obtenida de Binance P2P y editable antes de guardar.
- Gráfico de barras por rubro, gráfico de torta porcentual y evolución temporal por mes.
- Filtros por uno o varios rubros, vista acumulada o separada y rango de meses desde/hasta.
- Selector desplegable de rubros con checkboxes para elegir las categorías visibles en el gráfico temporal.
- Devolución de un JSON estructurado con ocho campos.
- Marcado de resultados como `listo` o `requiere_revision`.
- Revisión humana antes de registrar el gasto.
- Formulario editable por comprobante después del análisis y antes del envío a Google Sheets.
- Inicio limpio de la aplicación sin registros de ejemplo; el destino seleccionado se conserva durante la sesión local para no perderlo al recargar.
- Persistencia local mediante `localStorage`.
- Diseño responsive y metadatos PWA para uso desde un celular.
- Modo demo reproducible para evaluación: genera datos sintéticos, no llama a OpenAI, no autentica Google y no envía archivos personales.
- Contrato operativo de seis piezas y matriz de supervisión humana L0–L4 documentados en `DECISIONES.md`.

## Análisis económico

La aplicación usa `gpt-4.1-mini` porque la tarea necesita leer imágenes/PDF y devolver JSON estructurado, pero no necesita razonamiento complejo ni respuestas extensas. Es el modelo más chico que se probó para este caso y mantiene un costo bajo frente a `gpt-4.1`. La elección se puede revisar si una evaluación real muestra errores de lectura que requieran un modelo mayor.

### Tarifa utilizada

Al 6 de septiembre de 2026, la documentación oficial de OpenAI publica para `gpt-4.1-mini` una tarifa de **USD 0,40 por millón de tokens de entrada** y **USD 1,60 por millón de tokens de salida**. La referencia es [GPT-4.1 Mini — OpenAI API](https://developers.openai.com/api/docs/models/gpt-4.1-mini). La tarifa puede cambiar, por lo que esta sección identifica la fecha y deja explícita la fórmula.

### Supuesto de consumo por comprobante

La aplicación realiza una llamada a la Responses API por comprobante, incluso cuando se seleccionan hasta diez documentos en lote. Para presupuestar una corrida real se usa un supuesto conservador de **6.000 tokens de entrada** — instrucciones, solicitud y representación visual del comprobante — y **300 tokens de salida** para el JSON estructurado. Estos valores son un presupuesto de diseño, no una medición inventada: la cifra final depende del tamaño/resolución del archivo y debe contrastarse con el objeto `usage` devuelto por la API cuando se ejecute una corrida con saldo.

Fórmula:

```text
costo = (tokens_entrada / 1.000.000 × 0,40)
       + (tokens_salida / 1.000.000 × 1,60)
```

Con ese supuesto, una corrida de un comprobante cuesta aproximadamente **USD 0,00288**:

| Escenario | Entrada | Salida | Costo OpenAI estimado |
| --- | ---: | ---: | ---: |
| 1 comprobante | 6.000 | 300 | USD 0,00288 |
| lote máximo de 10 | 60.000 | 3.000 | USD 0,02880 |
| 50 comprobantes por semana | 300.000 | 15.000 | USD 0,14400 |
| 2.600 comprobantes por año | 15.600.000 | 780.000 | USD 7,48800 |

La proyección anual supone 50 comprobantes por semana durante 52 semanas. No incluye impuestos, eventuales reintentos, cambios futuros de tarifa ni servicios externos. Google Drive/Sheets y la cotización pública usada para USDT/ARS no se incluyen como costo de tokens de OpenAI; sus límites y condiciones deben evaluarse por separado. El modo demo tiene costo **USD 0**, porque no llama a OpenAI.

Para convertir esta estimación en evidencia medida, se debe guardar en la corrida real la cantidad `input_tokens` y `output_tokens` del objeto `usage` de la respuesta API y reemplazar los supuestos de esta tabla por esos valores. Si la cuenta no tiene saldo, la corrida queda documentada como funcional en modo demo y la parte económica como proyección explícita, sin presentar datos simulados como consumo real.

Para usar el agente:

```powershell
$env:OPENAI_API_KEY="tu_api_key"
py server.py
```

Para evaluar la interfaz sin claves, sin Google y sin archivos personales, se puede ejecutar:

```powershell
$env:DEMO_MODE="1"
py server.py
```

En modo demo el agente devuelve un comprobante sintético, permite editarlo y simula la confirmación sin escribir en ninguna planilla. Para volver al modo real, cerrar la terminal o ejecutar `$env:DEMO_MODE="0"` y configurar las variables privadas.

Después se abre `http://127.0.0.1:8000`, se adjuntan uno o varios comprobantes, se elige **Analizar comprobantes**, se revisan y corrigen los campos editables de cada resultado y finalmente se registra el lote en Google Sheets.

Para habilitar Google Sheets también hay que configurar en Google Cloud un cliente OAuth para aplicación web, activar Google Sheets API y registrar exactamente `http://127.0.0.1:8000/oauth2callback` como URI de redirección. Luego se ejecuta:

```powershell
$env:GOOGLE_CLIENT_ID="tu_client_id"
$env:GOOGLE_CLIENT_SECRET="tu_client_secret"
py server.py
```

Al guardar, Google administra la contraseña, la clave y la autenticación. La aplicación nunca solicita ni almacena esas credenciales. La autorización se reutiliza mientras la ventana de la aplicación permanece abierta y se revoca del servidor al cerrarla; al abrir una nueva sesión se vuelve a solicitar autorización. Si no se pega una URL, después de autorizar se listan las planillas disponibles y se elige una. Si se seleccionan varios comprobantes, se analiza cada documento y se agregan todas las filas en una única operación de guardado.

El botón **Importar planilla** permite elegir una planilla de Google Sheets y leer sus filas. La aplicación reconoce el formato actual de once columnas, agrega encabezados a una planilla antigua cuando hace falta y actualiza el resumen, los gráficos y la evolución temporal con esos valores reales. **Importar JSON** queda disponible como alternativa para archivos exportados o previamente analizados.

## Qué falta o qué falló

La primera versión abría el explorador de archivos al elegir la opción de cámara en la computadora. El motivo fue que `capture="environment"` funciona principalmente como captura directa en celulares y no inicializa necesariamente la webcam en un navegador de escritorio. Se corrigió agregando `getUserMedia`, una vista previa de cámara y un botón para tomar la foto.

La aplicación mantiene una copia local de los gastos confirmados en el navegador y la fuente compartida queda en Google Sheets; todavía no existe una base de datos multiusuario propia. El selector también permite duplicar, renombrar y enviar a la papelera planillas de prueba dentro de `Finanzas claras`.

La integración OAuth, la creación de carpeta/planilla, la lectura, la escritura, la edición, el renombrado, la duplicación, los filtros y el borrado fueron probados con una planilla de prueba; las cinco corridas están documentadas en `corridas/`. La cotización consultada es la más cercana disponible al momento de la carga en Binance P2P; no es una serie histórica exacta por fecha. El usuario puede corregirla en el formulario antes de guardar.

Queda pendiente una medición real de `input_tokens` y `output_tokens` con saldo disponible en la cuenta de API; la proyección económica y su fórmula ya están documentadas arriba. También queda pendiente una prueba real de publicación multiusuario. La matriz de niveles, permisos, riesgos y firma quedó documentada en `DECISIONES.md`.

La prueba completa contra la API requiere una clave válida en `OPENAI_API_KEY` y saldo o permisos disponibles en la cuenta. La clave no debe escribirse en el frontend ni subirse al repositorio. Los archivos personales de comprobantes, `credentials*.json`, tokens y `.env` quedan excluidos por `.gitignore`; `.env.example` documenta las variables necesarias sin valores reales.

## Qué aprendí

Aprendí que una aplicación útil no se resuelve solamente con un prompt: necesita una interfaz, un contrato de salida, una herramienta real y una instancia clara de revisión humana. También entendí que pedir JSON estricto ayuda a conectar el resultado del agente con otros componentes de software. Las pruebas con cámara y archivos mostraron que una misma funcionalidad puede comportarse distinto en celular y computadora. Finalmente, aprendí que documentar fallas y decisiones es tan importante como mostrar la versión que funciona.
