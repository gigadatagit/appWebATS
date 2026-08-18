# SST Reflex App

Aplicacion web SST en Reflex con autenticacion Supabase Auth, persistencia en
PostgreSQL/Supabase y generacion documental HTML autocontenida.

## Reglas operativas

- La app no ejecuta DDL contra Supabase.
- No se modifica el esquema desde el backend.
- SQLite queda solo como fallback local de desarrollo.
- El login principal usa Supabase Auth.
- Roles internos se resuelven en `public.usuario` y `public.rol`.
- `ADMIN` puede consultar y generar documentos de cualquier registro.
- `SISO` solo puede consultar y generar documentos propios.

## Rutas principales

- `/sst/dashboard`: dashboard global SST.
- `/admin/dashboard`: dashboard ATS conservado por compatibilidad.
- `/sst/dashboard/preoperacionales`: preoperacionales de maquinaria.
- `/sst/dashboard/alturas`: permisos de trabajo en alturas.
- `/sst/dashboard/medios-acceso`: listas de chequeo de medios de acceso.
- `/sst/dashboard/energias-peligrosas`: permisos de energias peligrosas.
- `/sst/dashboard/trabajo-caliente`: permisos de trabajo seguro en caliente.
- `/sst/documentos`: generador HTML unificado e historial consolidado.
- `/ats/documentos`: ruta heredada que redirige al generador unificado.

Antes de usar dashboards SST o historial consolidado, ejecuta manualmente
`sql/02_views_sst_analytics.sql` en Supabase/PostgreSQL. Para que los tableros
de formatos cerrables usen `fecha_cierre`, ejecuta despues
`sql/03_dashboard_fecha_cierre.sql`. La app no aplica estas migraciones
automaticamente.

## Generacion documental HTML

El flujo vigente es:

```text
Tablas transaccionales
    -> consulta y transformacion
    -> plantilla Jinja HTML
    -> HTML UTF-8 autocontenido
    -> Supabase Storage privado
    -> registro en tabla documental
```

No se genera DOCX ni PDF en este flujo. Los documentos historicos PDF/Word siguen
apareciendo en el historial consolidado si existen registros en base de datos.

Caracteristicas del generador:

- Plantillas en `templates/<formato>/template.html`.
- Servicio central en `ats_reflex_app/services/documentos/html_documents.py`.
- Logo obligatorio `assets/brand/logoGIGAJPEG.jpeg` embebido como Data URI.
- Firmas e imagenes pequenas embebidas como Data URI.
- Imagenes opcionales ausentes muestran placeholder y advertencia.
- HTML sin JavaScript, sin rutas locales y sin marcadores Jinja residuales.
- Upload con MIME `text/html; charset=utf-8`.
- Versionado HTML independiente por `tipo_documento = 'HTML'`.
- Ruta Storage: `{codigo_publico}/v{version}/{codigo_publico}_v{version}.html`.
- URLs firmadas se usan solo para abrir o descargar el objeto desde Storage; no se
  incrustan dentro del HTML historico.

## Variables de entorno

Define estas variables, por ejemplo en `.env`:

```bash
APP_ENV=development
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB
# Alternativa opcional si DATABASE_URL esta vacia:
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_SSLMODE=require
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key-backend-only>
SUPABASE_STORAGE_BUCKET=ATSDocumentos
SUPABASE_SIGNED_URL_TTL_SECONDS=600
# Opcional:
SUPABASE_JWT_SECRET=
SECRET_KEY=
```

Notas:

- Si `DATABASE_URL` no existe pero defines `DB_USER`, `DB_PASSWORD`, `DB_HOST`,
  `DB_PORT` y `DB_NAME`, la app construye una URL PostgreSQL automaticamente.
- Si no existe `DATABASE_URL` ni esas variables, usa `sqlite:///data/ats_app.db`.
- Si faltan `SUPABASE_URL` o `SUPABASE_ANON_KEY`, el login se bloquea por diseno.
- `SUPABASE_SERVICE_ROLE_KEY` es solo backend. No debe exponerse en UI, logs ni
  estado Reflex.
- `SUPABASE_STORAGE_BUCKET` debe apuntar al bucket privado de documentos.
- `SUPABASE_SIGNED_URL_TTL_SECONDS` controla la vigencia de URLs firmadas.

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
reflex run
```

## Docker / Railway

El contenedor arranca Reflex en single-port y usa `PORT`.
En produccion, `DATABASE_URL` es obligatorio para evitar fallback a SQLite.

Variables requeridas:

- `DATABASE_URL`
- `APP_ENV=production`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET=ATSDocumentos`
- `SUPABASE_SIGNED_URL_TTL_SECONDS` opcional

Prueba local con Docker:

```bash
docker build -t ats-reflex-railway .
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_URL="<postgres-url>" \
  -e APP_ENV=production \
  -e SUPABASE_URL="<url>" \
  -e SUPABASE_ANON_KEY="<anon>" \
  -e SUPABASE_SERVICE_ROLE_KEY="<service_role>" \
  -e SUPABASE_STORAGE_BUCKET=ATSDocumentos \
  ats-reflex-railway
```

## Agregar un formato documental

Consulta `templates/README.md`. En resumen:

1. Registra el formato en `ats_reflex_app/services/sst_formats.py`.
2. Crea un loader en `ats_reflex_app/services/documentos/html_documents.py`.
3. Agrega el loader a `_LOADERS`.
4. Crea `templates/<formato>/template.html`.
5. Agrega pruebas de render, recursos y almacenamiento.

## Validacion

```bash
.venv\Scripts\python.exe -m unittest discover -v
.venv\Scripts\python.exe -m py_compile ats_reflex_app\services\documentos\html_documents.py
.venv\Scripts\reflex.exe compile
```
