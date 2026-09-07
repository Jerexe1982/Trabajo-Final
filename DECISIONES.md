# Contrato operativo y supervisión humana

## Seis piezas del contrato

1. **Rol:** agente de registro y clasificación de gastos personales.
2. **Objetivo:** transformar un comprobante visual o PDF en una propuesta de gasto verificable.
3. **Entrada y contexto:** un archivo de imagen o PDF, con hasta diez comprobantes por lote; el agente solo usa la información visible del comprobante.
4. **Instrucciones y límites:** no inventar datos, marcar ambigüedades, elegir una categoría válida y no afirmar que el gasto fue guardado.
5. **Salida estructurada:** JSON con `estado`, `campos`, `observaciones` y `preguntas`; los campos son fecha, importe, moneda, comercio_destinatario, cbu_destino, medio_pago, categoria y comentario.
6. **Handoff y supervisión:** mostrar los resultados en un formulario editable; la persona revisa, corrige, confirma y puede luego editar o borrar una fila antes o después de sincronizarla con Google Sheets. El agente analiza cada comprobante por separado, incluso dentro de un lote de hasta diez; la aplicación coordina el lote, detecta duplicados, consulta la cotización, solicita OAuth y ejecuta la escritura en Google Sheets solo después de la confirmación humana.

Los textos completos y literales utilizados están en `prompts/system_prompt.md`, `prompts/user_prompt.md` y en la sección **Cómo se lo pedí** del README.

## Niveles de autonomía L0–L4

| Nivel | Qué hace el sistema | Qué revisa una persona | Quién firma |
|---|---|---|---|
| **L0 · Consultar** | Permite consultar el estado de configuración o cargar un gasto manual sin invocar el agente. | Todos los campos y el destino si decide guardar. | Exequiel Pinto, propietario y operador. |
| **L1 · Proponer** | Lee cada comprobante y propone campos en JSON; en un lote procesa hasta diez comprobantes por separado. | Cada dato extraído, importe, fecha, categoría, observaciones y duplicados. | Exequiel Pinto, al confirmar el formulario. |
| **L2 · Ejecutar con revisión** | Tras la revisión, prepara el lote y permite guardar, editar o borrar filas en Google Sheets. | La vista completa, los filtros, la planilla destino y cada cambio antes de aplicarlo. | Exequiel Pinto, mediante el botón de acción correspondiente. |
| **L3 · Ejecutar y avisar** | **No habilitado:** el sistema no ejecuta escrituras, ediciones o borrados en segundo plano para luego avisar. | No aplica mientras este nivel siga bloqueado. | No aplica. |
| **L4 · Autónomo** | **No habilitado.** El agente nunca guarda, modifica ni elimina datos sin confirmación humana. | No aplica: este nivel está deliberadamente bloqueado. | No aplica. |

## Herramientas y conectores reales

- **OpenAI Responses API:** analiza imágenes y PDFs y devuelve el JSON del contrato.
- **Archivos locales y cámara:** aportan las imágenes/PDF seleccionados por la persona.
- **Google OAuth, Drive y Sheets API:** permiten seleccionar, crear, leer y agregar filas en una planilla propiedad del usuario.
- **Google Drive:** limita el selector a la carpeta `Finanzas claras` y permite renombrar o enviar archivos a la papelera solo después de una confirmación humana.
- **Binance P2P:** aporta una cotización cercana USDT/ARS para precargar la conversión; la persona puede corregirla.
- **Modo demo:** permite evaluar la interfaz con datos sintéticos sin utilizar ninguna credencial ni enviar archivos.

## Decisiones de seguridad

- Las claves de OpenAI y Google se cargan como variables de entorno y nunca se incluyen en el frontend.
- `credentials*.json`, tokens, comprobantes y archivos `.env` están excluidos por `.gitignore`.
- La carpeta y la planilla de Google solo se crean después de la autorización explícita del usuario.
- El modo demo no transmite documentos ni escribe en Google Sheets.
- Los cambios de edición y borrado requieren una acción explícita y se muestran en una pestaña separada antes de aplicarse.
- La sesión de OAuth se conserva solo en memoria del servidor mientras la aplicación está abierta y se limpia al cerrar la ventana.
- El selector de planilla muestra únicamente archivos de la carpeta de trabajo; los filtros de año, mes y rubro se aplican en el frontend sin cambiar datos hasta que se guarda una edición.

## Historia de iteraciones y errores literales

La siguiente historia conserva decisiones verificables del desarrollo. Cada error produjo un cambio de contrato, de permisos o de interfaz; no se presenta el sistema como si hubiera funcionado desde el primer intento.

| Iteración | Evidencia o error observado | Decisión antes/después |
|---|---|---|
| OAuth local | `redirect_uri_mismatch` para `http://127.0.0.1:8000/oauth2callback` y luego `invalid_client` (`OAuth client was not found`). | Antes se intentaba autorizar sin validar la configuración local. Después se documentó el callback exacto, se separaron credenciales locales y se agregó el mensaje de autorización temporal. |
| Credenciales OpenAI | `Incorrect API key provided` y `credit_balance_exhausted`. | Antes el error quedaba poco claro. Después las credenciales se cargan solo por entorno, el modo demo permite probar sin saldo y README separa costo proyectado de consumo medido. |
| Entrada multimodal | `Invalid 'input[0].content[1].file_data'`. | Antes el PDF se enviaba con un formato incompatible. Después se envía como `data:application/pdf;base64,...`; las imágenes usan `input_image` y ambos caminos quedan cubiertos por corridas reales. |
| Cámara | La cámara abría el explorador de archivos en vez de capturar. | Antes se reutilizaba el selector de archivos. Después se usa `getUserMedia`, con permiso explícito y alternativa de cargar archivo. |
| Lotes | El primer lote real mostró cinco comprobantes editables y guardó una corrección en Sheets. | Antes se documentaba solo un comprobante. Después el contrato permite hasta diez, con un resultado JSON por documento y revisión humana individual. |
| Planillas duplicadas | Una copia dentro de la carpeta no aparecía en el selector. | Antes el token tenía alcance insuficiente. Después se amplió el alcance Drive, se agregó listado de archivos y se habilitaron renombrar, duplicar y eliminar con confirmación. |
| Visualización | La última etiqueta mensual del gráfico quedaba cortada y el gráfico podía quedar desactualizado tras borrar o editar. | Después se corrigió el alineado de la última etiqueta y se fuerza la recarga de datos tras las operaciones de Sheets. |
| Rubros y orden | Faltaban rubros en algunos estados y el visualizador no permitía ordenar. | Después se sincronizó la lista de categorías, se agregaron filtros por año/mes/rubro y orden por fecha, monto y rubro, conservando el formulario editable. |

## Fallas previstas y respuesta operativa

| Falla | Respuesta del sistema | Revisión y salida |
|---|---|---|
| Comprobante ilegible o formato no compatible | Rechazar ese documento y devolver un error explícito; no inventar campos ni continuar silenciosamente. | La persona revisa el archivo y lo vuelve a cargar o lo corrige manualmente. |
| JSON inválido o respuesta incompleta del modelo | No mostrar el resultado como válido; registrar el error y pedir una nueva ejecución. | La persona no guarda nada y conserva la corrida fallida en la evidencia. |
| Duplicado detectado en Sheets | Mostrar advertencia y pedir confirmación expresa para guardar de todos modos. | Exequiel Pinto decide continuar o cancelar. |
| OAuth vencido o permisos insuficientes | Detener la operación, informar que se requiere autorización y no escribir en Sheets. | Exequiel Pinto reautoriza o abandona la operación. |
| Error de red/API al guardar, editar o borrar | Informar el estado de la operación; no afirmar éxito si no se recibió HTTP 200. | Se verifica la planilla y se reintenta manualmente solo si corresponde. |
| Cotización USDT/ARS ausente | Mantener el comprobante editable y marcar la cotización como pendiente; no bloquear la revisión del gasto en ARS. | La persona corrige o completa el valor antes de usar la conversión. |

## Alternativas descartadas

- **Clave de OpenAI en el frontend:** se descartó porque expone una credencial con capacidad de consumo; la llamada queda en el servidor y la clave proviene de `OPENAI_API_KEY`.
- **Incluir OAuth o comprobantes dentro del repositorio:** se descartó por privacidad y seguridad; `.gitignore` excluye credenciales, tokens, archivos locales y documentos reales.
- **Guardar automáticamente después del análisis:** se descartó porque convertiría una propuesta en una acción irreversible sin revisión; el guardado queda en L2 y requiere botón humano.
- **Usar solo una planilla fija o una URL manual:** se descartó porque no resolvía copias, renombrado y selección dentro de la carpeta; se implementó el listado de Drive y la gestión confirmada de archivos.
- **Presentar el costo estimado como consumo real:** se descartó; las corridas sin `usage` se declaran como no medidas y el servidor ahora expone el objeto `usage` por comprobante en la respuesta de análisis.

## Responsable y firma

El responsable operativo es **Exequiel Pinto**, propietario de la aplicación y usuario que autoriza Google, revisa cada comprobante, decide ante duplicados y confirma guardar, editar o borrar. La aplicación no tiene un tercero autorizado para firmar resultados ni ejecuta acciones autónomas L3/L4.
