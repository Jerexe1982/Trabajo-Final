# Corrida 3 — Google Drive y Google Sheets

## Objetivo

Verificar autenticación temporal, selección y administración de planillas, escritura, importación, filtros y edición sincronizada.

## Preparación

Ejecutar `iniciar-finanzas.local.ps1` con `OPENAI.txt` y `client_secret.json` locales. Usar una planilla de prueba dentro de la carpeta `Finanzas claras`.

## Pasos

1. Abrir **Importar planilla** o **Editar planilla**.
2. Confirmar el aviso de autenticación temporal.
3. Autorizar Google.
4. Seleccionar una planilla de la carpeta `Finanzas claras`.
5. Verificar encabezados y registros.
6. Probar filtros de año, mes y rubro.
7. Editar un rubro y guardar.
8. Confirmar que los gráficos se actualizan sin volver a importar.
9. Renombrar la planilla.
10. Probar el envío a papelera únicamente con una planilla de prueba.
11. Cerrar la aplicación y verificar que la próxima sesión solicite autenticación nuevamente.

## Resultado

### Ejecutado y aprobado

- La autenticación de Google funcionó y permitió seleccionar la planilla de prueba dentro de `Finanzas claras`.
- La planilla se importó correctamente con sus encabezados y registros.
- La edición sincronizada permitió actualizar los datos y reflejar los cambios en la aplicación.
- La eliminación de un registro se reflejó correctamente en Google Sheets.
- Luego del borrado, el registro desapareció de la tabla local y los gráficos se actualizaron sin volver a importar la planilla.
- La opción **Duplicar** creó una copia dentro de `Finanzas claras`.
- La copia apareció tanto en el selector de la aplicación como en Google Drive.
- La copia pudo renombrarse y luego enviarse a la papelera; finalmente quedó solo la planilla original.

### Pendiente para completar la corrida

- La autenticación temporal quedó verificada: al cerrar y volver a abrir la aplicación se mostró nuevamente el aviso y Google solicitó autorización otra vez.
- La prueba de renombrado y envío a papelera quedó aprobada utilizando una planilla de prueba.

### Estado final

Corrida aprobada.
