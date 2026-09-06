# Corrida 4 — Imagen real individual

## Objetivo

Verificar el flujo completo para un comprobante de imagen: análisis multimodal, cotización, revisión/guardado en Google Sheets y edición posterior sincronizada.

## Resultado

### Ejecutado y aprobado

- **Fecha:** 6 de septiembre de 2026.
- **Entrada:** un comprobante real en formato imagen.
- **Análisis OpenAI:** aprobado; el servidor registró `POST /api/analyze-receipts HTTP/1.1" 200`.
- **Cotización:** se consultó correctamente la cotización USDT/ARS para la fecha `2026-08-30`; el servidor registró respuesta `200`.
- **Guardado:** Google Sheets recibió el registro; el servidor registró `POST /api/google-save HTTP/1.1" 200`.
- **Lectura posterior:** la aplicación volvió a leer correctamente la planilla; el servidor registró `GET /api/google-read?... HTTP/1.1" 200`.
- **Edición:** se actualizó el registro en Google Sheets; el servidor registró `POST /api/google-update HTTP/1.1" 200`.

## Evidencia textual del servidor

```text
[06/Sep/2026 13:02:31] "POST /api/analyze-receipts HTTP/1.1" 200 -
[06/Sep/2026 13:02:31] "GET /api/usdt-rate?date=2026-08-30 HTTP/1.1" 200 -
[06/Sep/2026 13:06:56] "POST /api/google-save HTTP/1.1" 200 -
[06/Sep/2026 13:07:27] "GET /api/google-read?spreadsheet_id=... HTTP/1.1" 200 -
[06/Sep/2026 13:07:34] "POST /api/google-update HTTP/1.1" 200 -
```

## Estado

Corrida aprobada.
