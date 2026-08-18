# Plantillas HTML SST

Los documentos SST se generan con Jinja2 desde `templates/<formato>/template.html`.
El HTML resultante debe ser autocontenido, estatico y seguro para almacenar como
historico en Supabase Storage.

## Reglas de plantilla

- Extiende `_base.html` e importa `_macros.html` cuando necesites tablas, checklist o firmas.
- No incluyas JavaScript ni URLs firmadas dentro del HTML.
- No uses `|safe` para datos ingresados por usuarios.
- Usa las estructuras ya preparadas por el servicio: `formato`, `documento`, `general`,
  `trabajadores`, `pasos`, `peligros`, `checklist_secciones`, `firmas`, `cierre`,
  `logo_data_uri` y `recurso_principal`.
- Conserva reglas de impresion Letter, `thead` repetible y `break-inside: avoid`.
- Las imagenes finales deben llegar como `data:image/...;base64,...`.

## Como agregar un formato

1. Registra el formato en `ats_reflex_app/services/sst_formats.py` con codigo,
   nombre, tabla principal, tabla documental, columna FK, ruta de plantilla y
   metadatos oficiales del encabezado.
2. Crea un loader en `ats_reflex_app/services/documentos/html_documents.py` que consulte
   las tablas transaccionales y devuelva un contexto organizado. La plantilla no debe
   consultar base de datos.
3. Agrega el loader a `_LOADERS`.
4. Crea `templates/<formato>/template.html`.
5. Si requiere imagen local, guarda en base de datos una ruta relativa bajo `assets/`
   y deja que `resolve_asset_data_uri()` la valide.
6. Agrega pruebas de smoke, render minimo, filas dinamicas y recursos.

## Recursos y firmas

- El logo obligatorio es `assets/brand/logoGIGAJPEG.jpeg`.
- Las rutas de maquinaria o medios se resuelven contra `assets/`; rutas con `..` o
  fuera del directorio se rechazan.
- Firmas vacias, corruptas o ausentes no bloquean la generacion; se muestran como
  `Firma no registrada` y se agregan advertencias.
- Si falta una imagen secundaria, se muestra `Imagen no disponible` y se registra
  advertencia.
