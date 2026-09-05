# Finanzas claras

Aplicación web de seguimiento personal de gastos y resumen mensual.

## Funcionalidades actuales

- Registro de gastos con descripción, importe, categoría, fecha y nota.
- Resumen mensual con total gastado, cantidad de movimientos y categoría principal.
- Distribución visual de gastos por categoría.
- Historial filtrable y buscable.
- Eliminación de registros.
- Exportación del período seleccionado a JSON.
- Persistencia local en el navegador mediante `localStorage`.

## Cómo probarla

Abrir `index.html` en un navegador moderno. La aplicación funciona sin instalación ni servidor.

Los datos de ejemplo se cargan únicamente la primera vez. Las modificaciones posteriores quedan guardadas en el navegador.

## Próxima evolución del trabajo final

La aplicación será la interfaz operativa del sistema agéntico. El agente podrá transformar comprobantes en registros estructurados, pedir confirmación ante ambigüedades y preparar la información para incorporarla a la aplicación o a Google Sheets.
