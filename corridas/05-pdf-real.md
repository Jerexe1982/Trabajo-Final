# Corrida 5 — PDF real individual

## Objetivo

Verificar el flujo completo para un comprobante PDF: análisis multimodal, extracción estructurada, cotización, revisión humana, detección de duplicados, guardado e intervención posterior en Google Sheets.

## Resultado

### Ejecutado y aprobado

- **Fecha:** 6 de septiembre de 2026.
- **Entrada:** un comprobante real en formato PDF.
- **Análisis OpenAI:** aprobado; el servidor registró `POST /api/analyze-receipts HTTP/1.1" 200`.
- **Cotización:** se consultó correctamente la cotización USDT/ARS para la fecha `2026-07-25`; el servidor registró respuesta `200`.
- **Revisión humana:** el resultado apareció en un formulario editable con fecha, importe, moneda, categoría, medio de pago, CBU, comentario y cotización.
- **Detección de duplicado:** la aplicación identificó un posible duplicado y solicitó confirmación antes de continuar.
- **Guardado:** Google Sheets recibió el registro; el servidor registró `POST /api/google-save HTTP/1.1" 200`.
- **Lectura posterior:** la planilla pudo seleccionarse y leerse correctamente; el servidor registró `GET /api/google-files HTTP/1.1" 200` y `GET /api/google-read?... HTTP/1.1" 200`.
- **Eliminación supervisada:** el registro de prueba se eliminó posteriormente de Google Sheets; el servidor registró `POST /api/google-delete HTTP/1.1" 200`.

## Evidencia textual del servidor

```text
[06/Sep/2026 13:11:24] "POST /api/analyze-receipts HTTP/1.1" 200 -
[06/Sep/2026 13:11:25] "GET /api/usdt-rate?date=2026-07-25 HTTP/1.1" 200 -
[06/Sep/2026 13:12:49] "POST /api/google-save HTTP/1.1" 200 -
[06/Sep/2026 13:13:04] "GET /api/google-files HTTP/1.1" 200 -
[06/Sep/2026 13:13:11] "GET /api/google-read?spreadsheet_id=... HTTP/1.1" 200 -
[06/Sep/2026 13:14:06] "POST /api/google-delete HTTP/1.1" 200 -
```

## Estado

Corrida aprobada.
