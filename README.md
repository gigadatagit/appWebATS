# ATS Reflex App

Aplicacion ATS en `Reflex` con autenticacion en `Supabase Auth` y persistencia en PostgreSQL/Supabase via `DATABASE_URL`.

## Reglas clave actuales

- No se ejecuta DDL desde la app contra Supabase.
- No hay Alembic ni migraciones por version en esta etapa.
- `SQLite` se mantiene solo como fallback local de desarrollo.
- El login principal es por `Supabase Auth` (email/password).
- El perfil interno y roles se resuelven en `public.usuario` + `public.rol`.

## Variables de entorno

Define estas variables (por ejemplo en `.env`):

```bash
APP_ENV=development
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB
# Optional alternative if DATABASE_URL is empty:
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
ATS_PDF_ENGINE=word
SUPABASE_SIGNED_URL_TTL_SECONDS=600
# Opcional:
SUPABASE_JWT_SECRET=
```

### Notas

- Si `DATABASE_URL` no existe pero defines `DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME`, la app construye una URL PostgreSQL automaticamente.
- Si no existe ni `DATABASE_URL` ni esas variables, la app usa `sqlite:///data/ats_app.db`.
- Si tu password tiene caracteres especiales (`+`, `/`, `@`, `:`), usa variables `DB_*` para que el sistema codifique la URL correctamente.
- Si faltan `SUPABASE_URL` o `SUPABASE_ANON_KEY`, el login se bloquea por diseno.
- `SUPABASE_SERVICE_ROLE_KEY` es solo backend (nunca frontend/estado UI/logs).
- `SUPABASE_STORAGE_BUCKET` debe apuntar al bucket privado (`ATSDocumentos`).
- `ATS_PDF_ENGINE`:
  - `word`: entorno local Windows con Microsoft Word + `docx2pdf`.
  - `libreoffice`: entorno Linux/Railway con `soffice --headless`.
- `SUPABASE_SIGNED_URL_TTL_SECONDS` controla vigencia de URL firmada en historial (default 600s).

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
reflex run
```

## Conexion de base de datos

- `rxconfig.py` lee `DATABASE_URL`.
- `ats_reflex_app/config.py` tambien puede construir `DATABASE_URL` desde variables separadas (`DB_*` o `user/password/host/port/dbname`).
- `ats_reflex_app.py` ejecuta `ensure_database()` solo si la URL es SQLite.
- `db_bootstrap.py` queda aislado para desarrollo local SQLite.
- `ats_reflex_app/db_engine.py` incluye `create_sqlalchemy_engine()` y `test_database_connection()` (opcional, sin DDL).

## Autorizacion ATS (app-level, preparada para RLS)

- Rol `ADMIN`: acceso total a ATS.
- Rol `SISO`: solo ATS propios (`ats.creado_por_usuario_id == current_user_id`).
- Tablas hijas (`ats_*`) heredan permiso del ATS padre.
- `creado_por_usuario_id` se asigna desde sesion al crear ATS y no se edita despues.
- `generado_por_usuario_id` en documentos se asigna desde sesion.

## Reflex Cloud (staging/prod)

Configura secretos:

- `DATABASE_URL`
- `APP_ENV`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `ATS_PDF_ENGINE`
- `SUPABASE_SIGNED_URL_TTL_SECONDS`

Recomendacion de conexion:

1. Usar `Direct connection` si la red lo permite.
2. Si no, usar `Supavisor Session mode`.
3. Evitar `Transaction pooler` para este backend persistente con SQLAlchemy/Reflex.

## Despliegue en Railway con Docker (Fase 6)

- Railway detecta automaticamente el `Dockerfile` en la raiz del proyecto.
- El contenedor arranca en single-port con Reflex prod y usa `PORT` (Railway lo inyecta automaticamente).
- En runtime de contenedor, `DATABASE_URL` es obligatorio; si falta, el proceso termina para evitar fallback a SQLite en produccion.

Variables requeridas en Railway:

- `DATABASE_URL`
- `APP_ENV=production`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET=ATSDocumentos`
- `ATS_PDF_ENGINE=libreoffice`
- `SUPABASE_SIGNED_URL_TTL_SECONDS` (opcional recomendado)

Comandos de prueba local con Docker:

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
  -e ATS_PDF_ENGINE=libreoffice \
  ats-reflex-railway
```

## Checklist operativo minimo

1. El usuario existe en `auth.users`.
2. Existe perfil activo en `public.usuario` con `auth_user_id` enlazado.
3. Tiene `rol_id` valido (`ADMIN` o `SISO`) en `public.rol`.
4. `DATABASE_URL` y claves Supabase estan configuradas en el entorno.

## Prueba de documentos ATS (Fase 5)

### Local Windows (Word/docx2pdf)

1. Configura:
   - `ATS_PDF_ENGINE=word`
   - `SUPABASE_STORAGE_BUCKET=ATSDocumentos`
   - `SUPABASE_SERVICE_ROLE_KEY=...`
2. Verifica que Microsoft Word y `docx2pdf` funcionen en sesion interactiva.
3. En `/ats/documentos`, busca un ATS, genera PDF y confirma:
   - descarga automatica,
   - nuevo objeto en Storage con ruta `ATS-CODIGO/vN/ATS-CODIGO_vN.pdf`,
   - nuevo registro en `ats_documento` con version incremental.

### Linux / Railway (LibreOffice)

1. Configura:
   - `ATS_PDF_ENGINE=libreoffice`
   - `SUPABASE_STORAGE_BUCKET=ATSDocumentos`
   - `SUPABASE_SERVICE_ROLE_KEY=...`
2. Asegura que `soffice` este disponible en runtime.
3. Genera documento desde `/ats/documentos` y valida:
   - descarga automatica,
   - carga en bucket privado,
   - historial con URL firmada backend.
