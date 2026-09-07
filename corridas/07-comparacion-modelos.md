# Corrida 07 — comparación controlada de modelos

- **Fecha:** 2026-09-07
- **Entrada común:** el mismo PDF anonimizado de un comprobante de servicio.
- **Fixture público:** [`07-entrada-fixture.json`](07-entrada-fixture.json).
- **Prompt:** el mismo `prompts/system_prompt.md` y `prompts/user_prompt.md`.
- **Cambios entre pruebas:** únicamente `OPENAI_MODEL`.
- **Modo:** real, no demo.

## Resultados

| Modelo | JSON válido | Fecha | Importe | Moneda | Rubro propuesto | Entrada | Salida | Costo |
|---|---|---|---:|---|---|---:|---:|---:|
| `gpt-4.1-nano` | Sí | 2026-09-04 | 40.626 | ARS | Otros | 2.649 | 148 | USD 0,000324 |
| `gpt-4.1-mini` | Sí | 2026-09-04 | 40.626 | ARS | Vivienda y servicios | 2.219 | 117 | USD 0,001075 |

## Decisión

Los dos modelos extrajeron correctamente los datos básicos y respetaron el contrato JSON. `gpt-4.1-mini` produjo una categoría más específica y coherente con el tipo de comprobante; `gpt-4.1-nano` devolvió `Otros`, lo que aumenta la revisión manual. Por eso se mantiene `gpt-4.1-mini`: cuesta más por corrida, pero reduce el riesgo de clasificación genérica y sigue siendo el modelo más chico que funcionó bien para la tarea completa.

## Cálculo

Para `gpt-4.1-nano` se aplicaron USD 0,10/M de entrada y USD 0,40/M de salida:

```text
(2.649 / 1.000.000 × 0,10) + (148 / 1.000.000 × 0,40) = USD 0,000324
```

Para `gpt-4.1-mini` se aplicaron USD 0,40/M de entrada y USD 1,60/M de salida:

```text
(2.219 / 1.000.000 × 0,40) + (117 / 1.000.000 × 1,60) = USD 0,001075
```

La entrada y los resultados con datos personales se conservan fuera del repositorio. Este documento contiene únicamente la comparación anonimizada necesaria para reproducir la decisión.

## RECÁLCULO

```text
gpt-4.1-nano:
(2.649 / 1.000.000 × 0,10) + (148 / 1.000.000 × 0,40)
= USD 0,0003241 → USD 0,000324 declarado

gpt-4.1-mini:
(2.219 / 1.000.000 × 0,40) + (117 / 1.000.000 × 1,60)
= USD 0,0010748 → USD 0,001075 declarado

Desvío por redondeo: menor al 0,05 % en ambos casos.
```
