# ATS Reflex App - Base inicial

Base inicial en **Reflex + SQLite** para el módulo **Formato ATS** con:

- conexión a la base SQLite
- bootstrap automático del esquema SQL
- login local por roles (`ADMIN`, `SISO`)
- sidebar izquierda
- página ATS con estructura base tipo wizard
- dashboard administrativo básico
- listado de ATS recientes
- modelos `rx.Model` alineados con el esquema

## 1) Crear entorno e instalar

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## 2) Iniciar proyecto Reflex

```bash
reflex init
```

Si `reflex init` te pregunta por archivos que ya existen, conserva los de este proyecto.

## 3) Ejecutar la app

```bash
reflex run
```

La primera vez, el proyecto crea automáticamente:

- `data/ats_app.db`
- el esquema desde `sql/01_schema.sql`
- dos usuarios demo locales si no existen

## 4) Usuarios demo

- **admin** / `Admin123*`
- **siso** / `Siso123*`

Cámbialos apenas valides la base.

## 5) Estructura

```text
ats_reflex_app/
├─ rxconfig.py
├─ requirements.txt
├─ README.md
├─ data/
├─ sql/
│  └─ 01_schema.sql
└─ ats_reflex_app/
   ├─ __init__.py
   ├─ ats_reflex_app.py
   ├─ db_bootstrap.py
   ├─ security.py
   ├─ styles.py
   ├─ template.py
   ├─ components/
   ├─ models/
   ├─ pages/
   └─ state/
```

## 6) Qué hace ya esta base

- login local usando la tabla `usuario`
- separación por estados/páginas
- carga y persistencia básica de ATS
- tarjetas de resumen para admin
- placeholders listos para seguir con:
  - peligros y riesgos
  - pasos dinámicos
  - trabajadores dinámicos
  - firmas
  - generación PDF

## 7) Siguiente paso recomendado

1. completar el wizard ATS por secciones
2. conectar checklists de peligros, apoyos y certificados
3. agregar componente de firma real
4. generar PDF con Python
5. endurecer autenticación y permisos
