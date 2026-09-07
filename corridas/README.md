# Evidencia de corridas

Cada corrida reproducible debe conservar, en el mismo archivo o en archivos anexos con el mismo prefijo:

1. **Fecha y hora**, zona horaria y commit ejecutado.
2. **Entrada**, con comprobantes reales redactados o fixtures sintéticos; nunca se suben documentos personales sin anonimizar.
3. **Salida literal**, exactamente como la devuelve `POST /api/analyze-receipts`, incluyendo `results`, `count`, `model` y `usage`.
4. **Acciones posteriores**, como revisión, corrección, detección de duplicado, guardado, edición o eliminación en Google Sheets.
5. **Resultado verificable**, por ejemplo códigos HTTP del servidor y una captura o exportación redactada de la planilla.

Después de analizar, el botón **Descargar evidencia JSON** permite guardar una evidencia técnica con la fecha, el modelo, los nombres/tipos/tamaños de los archivos y la respuesta completa. No incluye el contenido base64 de los comprobantes ni ninguna credencial.

La respuesta de análisis conserva un elemento de `usage` por comprobante:

```json
{
  "archivo": "comprobante-01.pdf",
  "input_tokens": 0,
  "output_tokens": 0
}
```

Los ceros solo corresponden al modo demo. En una corrida real deben reemplazarse por los valores entregados por OpenAI. Si la API no informa `usage`, se registra explícitamente como dato no disponible y no se presenta un costo medido.

Las corridas históricas `01` a `05` documentan el comportamiento y los códigos HTTP observados, pero no contienen todos los archivos de entrada ni la respuesta JSON literal completa; por privacidad y porque esas respuestas no se conservaron en ese momento. Las próximas corridas deben seguir este formato para que un tercero pueda reconstruirlas.
