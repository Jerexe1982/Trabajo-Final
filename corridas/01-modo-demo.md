# Corrida 1 — Modo demo

## Objetivo

Verificar que la aplicación inicia, responde y procesa un lote sin transmitir archivos ni utilizar credenciales reales.

## Comando

```powershell
$env:DEMO_MODE="1"
$env:PORT="8013"
py server.py
```

## Prueba realizada

- `GET /api/health`
- `POST /api/analyze-receipts`
- Lote sintético de 2 documentos: un PDF y una imagen.

## Resultado observado

```json
{
  "ok": true,
  "demo_mode": true,
  "api_key_configured": false,
  "google_configured": false
}
```

El lote respondió correctamente con `count: 2`. La aplicación devolvió resultados estructurados con categoría `Alimentación` y no envió archivos a OpenAI ni a Google.

## Estado

**Aprobada.**
