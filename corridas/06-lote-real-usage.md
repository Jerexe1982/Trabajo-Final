# Corrida 06 — lote real con uso medido

- **Fecha:** 2026-09-07 01:02:48 UTC
- **Modelo:** `gpt-4.1-mini`
- **Modo:** real, no demo
- **Cantidad:** 5 comprobantes PDF
- **Resultado:** los 5 comprobantes fueron analizados y quedaron disponibles para revisión editable.
- **Evidencia JSON completa:** archivo local descargado como `evidencia-analisis-2026-09-07T01-02-48-481Z.json`.
- **Evidencia pública anonimizada:** [`06-evidencia-anonimizada.json`](06-evidencia-anonimizada.json).

## Consumo medido

| Concepto | Tokens |
|---|---:|
| Entrada | 11.083 |
| Salida | 659 |
| Total | 11.742 |

Con las tarifas documentadas para `gpt-4.1-mini` — USD 0,40 por millón de tokens de entrada y USD 1,60 por millón de tokens de salida — el costo de esta corrida fue:

```text
(11.083 / 1.000.000 × 0,40) + (659 / 1.000.000 × 1,60)
= USD 0,005488
```

## Trazabilidad

La evidencia descargada conserva la fecha, el modelo, los nombres y tamaños de los archivos, los resultados completos y el arreglo `respuesta.usage` por comprobante. El archivo contiene datos personales extraídos de comprobantes, por lo que no se copia sin anonimizar al repositorio público; se conserva localmente como respaldo de la corrida.
