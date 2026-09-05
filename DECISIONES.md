# Contrato operativo y supervisión humana

## Seis piezas del contrato

1. **Rol:** agente de registro y clasificación de gastos personales.
2. **Objetivo:** transformar un comprobante visual o PDF en una propuesta de gasto verificable.
3. **Entrada y contexto:** un archivo de imagen o PDF, con hasta diez comprobantes por lote; el agente solo usa la información visible del comprobante.
4. **Instrucciones y límites:** no inventar datos, marcar ambigüedades, elegir una categoría válida y no afirmar que el gasto fue guardado.
5. **Salida estructurada:** JSON con `estado`, `campos`, `observaciones` y `preguntas`; los campos son fecha, importe, moneda, comercio_destinatario, cbu_destino, medio_pago, categoria y comentario.
6. **Handoff y supervisión:** mostrar los resultados en un formulario editable; la persona revisa, corrige y confirma antes de cualquier escritura en Google Sheets.

Los textos completos y literales utilizados están en `prompts/system_prompt.md`, `prompts/user_prompt.md` y en la sección **Cómo se lo pedí** del README.

## Niveles de autonomía L0–L4

| Nivel | Qué hace el sistema | Qué revisa una persona | Quién firma |
|---|---|---|---|
| **L0 · Manual** | Permite cargar un gasto sin usar el agente. | Todos los campos y el destino. | La persona usuaria al guardar. |
| **L1 · Asistencia** | Lee un comprobante y propone campos en JSON. | Cada dato extraído, importe, fecha y categoría. | La persona usuaria. |
| **L2 · Lote supervisado** | Analiza hasta diez comprobantes y señala observaciones o preguntas. | Cada registro del lote en el formulario editable. | La persona usuaria por el lote confirmado. |
| **L3 · Acción confirmada** | Después de la confirmación, solicita OAuth y agrega las filas a Google Sheets. | La autorización Google, la planilla y el resultado del guardado. | La persona usuaria, mediante el botón de guardar. |
| **L4 · Autónomo** | **No habilitado.** El agente no guarda, modifica ni elimina datos sin confirmación humana. | No aplica: este nivel está deliberadamente bloqueado. | No aplica. |

## Herramientas y conectores reales

- **OpenAI Responses API:** analiza imágenes y PDFs y devuelve el JSON del contrato.
- **Archivos locales y cámara:** aportan las imágenes/PDF seleccionados por la persona.
- **Google OAuth, Drive y Sheets API:** permiten seleccionar, crear, leer y agregar filas en una planilla propiedad del usuario.
- **Modo demo:** permite evaluar la interfaz con datos sintéticos sin utilizar ninguna credencial ni enviar archivos.

## Decisiones de seguridad

- Las claves de OpenAI y Google se cargan como variables de entorno y nunca se incluyen en el frontend.
- `credentials*.json`, tokens, comprobantes y archivos `.env` están excluidos por `.gitignore`.
- La carpeta y la planilla de Google solo se crean después de la autorización explícita del usuario.
- El modo demo no transmite documentos ni escribe en Google Sheets.
