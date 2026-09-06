# Corrida 2 — Análisis real con OpenAI

## Objetivo

Verificar el análisis multimodal de comprobantes reales, la revisión humana, la edición de campos y la conversión antes de guardar.

## Preparación

Ejecutar `iniciar-finanzas.local.ps1` con una clave válida en `OPENAI.txt` y seleccionar hasta 10 comprobantes de prueba.

## Pasos

1. Abrir la aplicación.
2. Seleccionar uno o más comprobantes de prueba.
3. Presionar **Analizar comprobantes**.
4. Verificar fecha, importe, comercio, moneda y rubro.
5. Modificar manualmente al menos un campo.
6. Revisar la cotización precargada.
7. Confirmar que el resultado aparece en formato editable.

## Resultado

### Ejecutado y aprobado

- **Fecha y hora:** 6 de septiembre de 2026, 03:42 (hora local).
- **Entrada:** lote de 5 comprobantes reales seleccionado en una única operación.
- **Análisis:** la aplicación mostró los 5 resultados y habilitó la revisión de cada comprobante.
- **Supervisión humana:** se editó al menos un registro antes de confirmar el guardado.
- **Persistencia:** Google Sheets recibió el lote y reflejó la corrección realizada en la planilla.
- **Evidencia del servidor:** `POST /api/google-save HTTP/1.1" 200`.

### Observación económica

Esta corrida confirma el funcionamiento real del flujo, pero el servidor no conservó en la evidencia visible el objeto `usage` con `input_tokens` y `output_tokens`. Por eso el costo exacto de esta corrida no se presenta como medido; se utiliza la proyección documentada en `README.md` hasta incorporar o registrar ese dato en una corrida posterior.

### Estado

Corrida aprobada.
