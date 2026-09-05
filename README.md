# Finanzas claras

## Qué construí

Construí una aplicación web de seguimiento personal de gastos y resumen mensual. Permite registrar gastos, consultar la distribución por categorías, buscar movimientos y exportar el período en JSON. También permite importar comprobantes en imagen o PDF, usar la cámara de la computadora o del celular y solicitarle a un agente que proponga los datos del gasto antes de guardarlo.

La aplicación está pensada para una persona que quiere registrar sus gastos cotidianos sin completar manualmente todos los campos y manteniendo una revisión humana antes de confirmar.

## Cómo se lo pedí

### Prompt 1 — agente de registro y clasificación

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

### Prompt 2 — solicitud para cada comprobante

```text
Analizá el comprobante adjunto y prepará un registro de gasto siguiendo exactamente el contrato del system prompt. Priorizá la fidelidad al comprobante y señalá toda ambigüedad en observaciones o preguntas. Devolvé únicamente el JSON solicitado.
```

Estos prompts también están guardados por separado en `prompts/system_prompt.md` y `prompts/user_prompt.md`.

## Qué funciona

- Registro manual con descripción, importe, categoría, fecha y nota.
- Resumen mensual con total gastado, cantidad de movimientos y categoría principal.
- Distribución visual de gastos por categoría.
- Búsqueda y eliminación de movimientos.
- Exportación del período seleccionado a JSON.
- Importación de imágenes y archivos PDF.
- Captura directa desde la cámara del celular o la webcam de la computadora.
- Análisis multimodal mediante `server.py` y la Responses API.
- Solicitud de URL de Google Sheets antes de guardar.
- Autenticación OAuth de Google en una ventana emergente.
- Escritura de la fila confirmada mediante `spreadsheets.values.append`.
- Devolución de un JSON estructurado con ocho campos.
- Marcado de resultados como `listo` o `requiere_revision`.
- Revisión humana antes de registrar el gasto.
- Persistencia local mediante `localStorage`.
- Diseño responsive y metadatos PWA para uso desde un celular.

Para usar el agente:

```powershell
$env:OPENAI_API_KEY="tu_api_key"
py server.py
```

Después se abre `http://127.0.0.1:8000`, se adjunta un comprobante, se elige **Analizar comprobante**, se revisan los campos y finalmente se registra el gasto.

Para habilitar Google Sheets también hay que configurar en Google Cloud un cliente OAuth para aplicación web, activar Google Sheets API y registrar exactamente `http://127.0.0.1:8000/oauth2callback` como URI de redirección. Luego se ejecuta:

```powershell
$env:GOOGLE_CLIENT_ID="tu_client_id"
$env:GOOGLE_CLIENT_SECRET="tu_client_secret"
py server.py
```

Al guardar, Google administra la contraseña, la clave y la autenticación. La aplicación nunca solicita ni almacena esas credenciales.

## Qué falta o qué falló

La primera versión abría el explorador de archivos al elegir la opción de cámara en la computadora. El motivo fue que `capture="environment"` funciona principalmente como captura directa en celulares y no inicializa necesariamente la webcam en un navegador de escritorio. Se corrigió agregando `getUserMedia`, una vista previa de cámara y un botón para tomar la foto.

La aplicación todavía guarda los datos en el navegador y no en una base de datos multiusuario. La integración anterior con Google Sheets fue probada en el proyecto de la Entrega 1, pero todavía no está conectada automáticamente a esta aplicación.

La integración OAuth de Google quedó implementada, pero todavía falta probarla con un cliente OAuth propio, una planilla de prueba y una corrida real de escritura. El token se mantiene en memoria durante la ejecución actual del servidor; al reiniciar, Google volverá a solicitar autorización.

Todavía faltan las tres corridas reales documentadas en `corridas/`, el análisis económico de tokens y costos, la definición completa de niveles L0–L4, gobierno de permisos, riesgos y quién firma el resultado. También falta completar `DECISIONES.md` con la historia de iteraciones del trabajo.

La prueba completa contra la API requiere una clave válida en `OPENAI_API_KEY` y saldo o permisos disponibles en la cuenta. La clave no debe escribirse en el frontend ni subirse al repositorio.

## Qué aprendí

Aprendí que una aplicación útil no se resuelve solamente con un prompt: necesita una interfaz, un contrato de salida, una herramienta real y una instancia clara de revisión humana. También entendí que pedir JSON estricto ayuda a conectar el resultado del agente con otros componentes de software. Las pruebas con cámara y archivos mostraron que una misma funcionalidad puede comportarse distinto en celular y computadora. Finalmente, aprendí que documentar fallas y decisiones es tan importante como mostrar la versión que funciona.
