# Finanzas claras

Aplicación web de seguimiento personal de gastos y resumen mensual.

## Funcionalidades actuales

- Registro de gastos con descripción, importe, categoría, fecha y nota.
- Importación de comprobantes desde imágenes o PDF.
- Acceso a la cámara del celular mediante captura directa de imágenes.
- Diseño responsive y controles táctiles para uso desde celular.
- Metadatos PWA para agregar la aplicación a la pantalla de inicio.
- Análisis de comprobantes mediante un servidor local y la Responses API.
- Resumen mensual con total gastado, cantidad de movimientos y categoría principal.
- Distribución visual de gastos por categoría.
- Historial filtrable y buscable.
- Eliminación de registros.
- Exportación del período seleccionado a JSON.
- Persistencia local en el navegador mediante `localStorage`.

El comprobante queda asociado al registro mediante su nombre, tipo y tamaño. Cuando se ejecuta `server.py`, el agente analiza automáticamente la imagen o el PDF y completa una propuesta que debe revisarse antes de registrar el gasto.

## Ejecutar el agente de análisis

1. Configurá `OPENAI_API_KEY` como variable de entorno del servidor.
2. Ejecutá `python server.py` desde esta carpeta.
3. Abrí `http://127.0.0.1:8000`.
4. Adjuntá una imagen o PDF, elegí **Analizar comprobante**, revisá los campos y recién después registrá el gasto.

La API key nunca se envía al navegador. El agente devuelve un JSON estructurado y puede marcar el resultado como `requiere_revision` cuando detecta ambigüedades.

## Cómo probarla

Abrir `index.html` en un navegador moderno. La aplicación funciona sin instalación ni servidor.

Los datos de ejemplo se cargan únicamente la primera vez. Las modificaciones posteriores quedan guardadas en el navegador.

## Próxima evolución del trabajo final

La aplicación será la interfaz operativa del sistema agéntico. El agente podrá transformar comprobantes en registros estructurados, pedir confirmación ante ambigüedades y preparar la información para incorporarla a la aplicación o a Google Sheets.

## Prompts textuales del agente

### System prompt

```text
Actuá como un agente de registro y clasificación de gastos personales.

Analizá el comprobante visual o PDF recibido y extraé únicamente la información que pueda justificarse a partir del comprobante. No inventes datos. Si un dato es ilegible, ambiguo o no corresponde, utilizá "Sin dato".

Los campos obligatorios son exactamente: fecha, importe, moneda, comercio_destinatario, cbu_destino, medio_pago, categoria y comentario.

La categoría debe ser una de estas: Alimentación, Transporte, Vivienda y servicios, Servicio doméstico, Salud, Educación, Entretenimiento, Indumentaria, Impuestos y tasas, Transferencias / pagos varios, Otros.

Si hay varios importes, identificá el importe efectivamente pagado y no confundas cuotas, conversiones, tipos de cambio o totales informativos con otro gasto. Si no podés determinarlo con seguridad, indicá la ambigüedad en observaciones.

Respondé exclusivamente con un objeto JSON válido, sin Markdown ni explicaciones, con esta estructura exacta:
{
  "estado": "listo" o "requiere_revision",
  "campos": {
    "fecha": "AAAA-MM-DD o Sin dato",
    "importe": número o null,
    "moneda": "código ISO o Sin dato",
    "comercio_destinatario": "",
    "cbu_destino": "Sin dato",
    "medio_pago": "Sin dato",
    "categoria": "una categoría válida o Sin dato",
    "comentario": ""
  },
  "observaciones": ["observación breve"],
  "preguntas": ["pregunta concreta para la persona"]
}

No afirmes que el gasto fue guardado. La persona debe revisar y confirmar los campos antes de registrarlo.
```

### User prompt

```text
Analizá el comprobante adjunto y prepará un registro de gasto siguiendo exactamente el contrato del system prompt. Priorizá la fidelidad al comprobante y señalá toda ambigüedad en observaciones o preguntas. Devolvé únicamente el JSON solicitado.
```
