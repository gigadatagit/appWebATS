from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

from .config import get_database_url, is_sqlite_url
from .security import hash_password

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "ats_app.db"
SCHEMA_PATH = ROOT_DIR / "sql" / "01_schema.sql"

CONTROL_SEED_ROWS: list[tuple[str, str, str, str, int]] = [
    (
        "USO_EPP_BASICO",
        "Uso obligatorio de EPP basico",
        "Casco, gafas, guantes, botas y proteccion auditiva segun actividad.",
        "EPP",
        0,
    ),
    (
        "ARNES_LINEA_VIDA",
        "Arnes y linea de vida certificados",
        "Verificar puntos de anclaje, inspeccion preuso y certificacion vigente.",
        "EPP",
        0,
    ),
    (
        "DELIMITACION_AREA",
        "Delimitacion y senalizacion del area",
        "Instalar conos, cinta, barreras y avisos preventivos.",
        "Administrativo",
        0,
    ),
    (
        "BLOQUEO_ETIQUETADO",
        "Bloqueo y etiquetado de energias",
        "Aplicar LOTO, verificar ausencia de energia y liberar solo con autorizacion.",
        "Ingenieria",
        0,
    ),
    (
        "PERMISO_TRABAJO",
        "Permiso de trabajo aprobado",
        "Validar permiso, alcance, responsables, vigencia y condiciones de seguridad.",
        "Administrativo",
        0,
    ),
    (
        "INSPECCION_HERRAMIENTAS",
        "Inspeccion preoperacional de herramientas",
        "Retirar herramientas defectuosas y registrar hallazgos.",
        "Administrativo",
        0,
    ),
    (
        "ORDEN_ASEO",
        "Orden y aseo permanente",
        "Mantener rutas libres, retirar obstaculos y controlar residuos.",
        "Administrativo",
        0,
    ),
    (
        "VENTILACION_MONITOREO",
        "Ventilacion y monitoreo atmosferico",
        "Verificar condiciones de oxigeno, gases y ventilacion antes y durante la tarea.",
        "Ingenieria",
        0,
    ),
    (
        "EXTINTOR_VIGIA",
        "Extintor y vigia de seguridad",
        "Disponer extintor, vigia y control de fuentes de ignicion.",
        "Administrativo",
        0,
    ),
    (
        "PAUSAS_ACTIVAS",
        "Pausas activas y manejo ergonomico",
        "Aplicar tecnicas de levantamiento, rotacion de tareas y pausas activas.",
        "Administrativo",
        0,
    ),
    (
        "CONTROL_CAIDA_OBJETOS",
        "Control de caida de objetos",
        "Usar amarre de herramientas, rodapies y exclusion de area inferior.",
        "Ingenieria",
        0,
    ),
    (
        "COMUNICACION_PERMANENTE",
        "Comunicacion permanente del equipo",
        "Mantener radio/telefono operativo y canal de comunicacion definido.",
        "Administrativo",
        0,
    ),
    (
        "OTROS",
        "OTROS",
        "Control definido manualmente por SISO cuando no existe en catalogo.",
        "Otro",
        1,
    ),
]


def ensure_database() -> None:
    if not is_sqlite_url(get_database_url()):
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    first_creation = not DB_PATH.exists()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        if first_creation:
            schema = SCHEMA_PATH.read_text(encoding="utf-8")
            conn.executescript(schema)
            conn.commit()

        _run_runtime_migrations(conn)
        _seed_control_catalog(conn)
        _seed_demo_users(conn)
    finally:
        conn.close()


def _run_runtime_migrations(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        _create_missing_catalog_tables(conn)
        _migrate_control_catalog_schema(conn)
        _migrate_ats_paso_peligro_schema(conn)
        _migrate_ats_trabajador_schema(conn)
        _backfill_worker_catalog_and_snapshots(conn)
        _create_missing_indexes(conn)
        _create_or_replace_views(conn)
        conn.commit()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    if not _table_exists(conn, table_name):
        return False
    rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return any(str(row[1]) == column_name for row in rows)


def _add_column_if_missing(conn: sqlite3.Connection, table_name: str, column_def: str) -> None:
    column_name = column_def.split()[0]
    if _column_exists(conn, table_name, column_name):
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")


def _create_missing_catalog_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trabajador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            numero_documento TEXT NOT NULL UNIQUE,
            nombre_completo TEXT NOT NULL,
            cargo TEXT,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS control_catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            tipo_control TEXT,
            permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1)),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def _migrate_control_catalog_schema(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "control_catalogo"):
        return

    _add_column_if_missing(conn, "control_catalogo", "descripcion TEXT")
    _add_column_if_missing(conn, "control_catalogo", "tipo_control TEXT")
    _add_column_if_missing(conn, "control_catalogo", "permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1))")
    _add_column_if_missing(conn, "control_catalogo", "activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))")
    _add_column_if_missing(conn, "control_catalogo", "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
    _add_column_if_missing(conn, "control_catalogo", "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")

    conn.execute(
        """
        UPDATE control_catalogo
        SET permite_descripcion_libre = 1
        WHERE UPPER(COALESCE(codigo, '')) = 'OTROS'
           OR UPPER(COALESCE(nombre, '')) = 'OTROS'
        """
    )


def _ensure_otro_control_id(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id
        FROM control_catalogo
        WHERE UPPER(COALESCE(codigo, '')) = 'OTROS'
           OR UPPER(COALESCE(nombre, '')) = 'OTROS'
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row is None:
        cur.execute(
            """
            INSERT INTO control_catalogo (
                codigo,
                nombre,
                descripcion,
                tipo_control,
                permite_descripcion_libre,
                activo
            )
            VALUES ('OTROS', 'OTROS', ?, 'Otro', 1, 1)
            """,
            ("Control definido manualmente por SISO cuando no existe en catalogo.",),
        )
        return int(cur.lastrowid or 0)

    otro_id = int(row[0] or 0)
    if otro_id > 0:
        cur.execute(
            """
            UPDATE control_catalogo
            SET permite_descripcion_libre = 1
            WHERE id = ?
            """,
            (otro_id,),
        )
    return otro_id


def _migrate_ats_paso_peligro_schema(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS _tmp_ats_paso_peligro_legacy_controls")
    conn.execute("DROP TABLE IF EXISTS _tmp_ats_paso_peligro_new")

    if not _table_exists(conn, "ats_paso_peligro"):
        conn.execute(
            """
            CREATE TABLE ats_paso_peligro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ats_paso_id INTEGER NOT NULL,
                ats_peligro_id INTEGER NOT NULL,
                descripcion_otro TEXT,
                FOREIGN KEY (ats_paso_id) REFERENCES ats_paso(id) ON DELETE CASCADE,
                FOREIGN KEY (ats_peligro_id) REFERENCES ats_peligro(id) ON DELETE CASCADE,
                UNIQUE (ats_paso_id, ats_peligro_id)
            )
            """
        )
    else:
        columns = [
            str(row[1] or "").strip().lower()
            for row in conn.execute("PRAGMA table_info('ats_paso_peligro')").fetchall()
        ]
        column_set = set(columns)
        legacy_has_control_cols = "control_id" in column_set or "control_aplicado" in column_set
        has_core_columns = {"id", "ats_paso_id", "ats_peligro_id"}.issubset(column_set)
        requires_rebuild = legacy_has_control_cols or not has_core_columns

        if legacy_has_control_cols and _column_exists(conn, "ats_paso", "controles_a_realizar"):
            conn.execute(
                """
                UPDATE ats_paso_peligro
                SET control_aplicado = (
                    SELECT p.controles_a_realizar
                    FROM ats_paso p
                    WHERE p.id = ats_paso_peligro.ats_paso_id
                    LIMIT 1
                )
                WHERE COALESCE(TRIM(control_aplicado), '') = ''
                """
            )

        if legacy_has_control_cols:
            otro_control_id = _ensure_otro_control_id(conn)
            conn.execute(
                """
                CREATE TABLE _tmp_ats_paso_peligro_legacy_controls AS
                SELECT
                    id AS ats_paso_peligro_id,
                    COALESCE(NULLIF(control_id, 0), ?) AS control_id,
                    TRIM(COALESCE(control_aplicado, '')) AS control_aplicado
                FROM ats_paso_peligro
                WHERE COALESCE(NULLIF(control_id, 0), 0) > 0
                   OR COALESCE(TRIM(control_aplicado), '') <> ''
                """,
                (otro_control_id,),
            )

        if requires_rebuild:
            conn.execute("DROP VIEW IF EXISTS vw_ats_paso_peligro_control")
            conn.execute(
                """
                CREATE TABLE _tmp_ats_paso_peligro_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ats_paso_id INTEGER NOT NULL,
                    ats_peligro_id INTEGER NOT NULL,
                    descripcion_otro TEXT,
                    FOREIGN KEY (ats_paso_id) REFERENCES ats_paso(id) ON DELETE CASCADE,
                    FOREIGN KEY (ats_peligro_id) REFERENCES ats_peligro(id) ON DELETE CASCADE,
                    UNIQUE (ats_paso_id, ats_peligro_id)
                )
                """
            )
            source_descripcion_expr = (
                "NULLIF(TRIM(COALESCE(descripcion_otro, '')), '')"
                if "descripcion_otro" in column_set
                else "NULL"
            )
            conn.execute(
                """
                INSERT INTO _tmp_ats_paso_peligro_new (id, ats_paso_id, ats_peligro_id, descripcion_otro)
                SELECT id, ats_paso_id, ats_peligro_id, """
                + source_descripcion_expr
                + """
                FROM ats_paso_peligro
                """
            )
            conn.execute("DROP TABLE ats_paso_peligro")
            conn.execute("ALTER TABLE _tmp_ats_paso_peligro_new RENAME TO ats_paso_peligro")

    _add_column_if_missing(conn, "ats_paso_peligro", "descripcion_otro TEXT")
    conn.execute(
        """
        UPDATE ats_paso_peligro
        SET descripcion_otro = (
            SELECT NULLIF(TRIM(COALESCE(ap.descripcion_otro, '')), '')
            FROM ats_peligro ap
            JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
            WHERE ap.id = ats_paso_peligro.ats_peligro_id
              AND UPPER(COALESCE(pc.codigo, '')) = 'OTRO_PELIGRO'
            LIMIT 1
        )
        WHERE COALESCE(TRIM(descripcion_otro), '') = ''
          AND EXISTS (
              SELECT 1
              FROM ats_peligro ap
              JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
              WHERE ap.id = ats_paso_peligro.ats_peligro_id
                AND UPPER(COALESCE(pc.codigo, '')) = 'OTRO_PELIGRO'
                AND COALESCE(TRIM(ap.descripcion_otro), '') <> ''
          )
        """
    )

    if not _table_exists(conn, "ats_paso_peligro_control"):
        conn.execute(
            """
            CREATE TABLE ats_paso_peligro_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ats_paso_peligro_id INTEGER NOT NULL,
                control_id INTEGER NOT NULL,
                control_aplicado TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ats_paso_peligro_id) REFERENCES ats_paso_peligro(id) ON DELETE CASCADE,
                FOREIGN KEY (control_id) REFERENCES control_catalogo(id),
                UNIQUE (ats_paso_peligro_id, control_id, control_aplicado)
            )
            """
        )

    if _table_exists(conn, "_tmp_ats_paso_peligro_legacy_controls"):
        conn.execute(
            """
            INSERT OR IGNORE INTO ats_paso_peligro_control (
                ats_paso_peligro_id,
                control_id,
                control_aplicado
            )
            SELECT
                l.ats_paso_peligro_id,
                l.control_id,
                COALESCE(
                    NULLIF(TRIM(l.control_aplicado), ''),
                    (SELECT c.nombre FROM control_catalogo c WHERE c.id = l.control_id LIMIT 1),
                    'OTROS'
                )
            FROM _tmp_ats_paso_peligro_legacy_controls l
            WHERE COALESCE(l.control_id, 0) > 0
            """
        )
        conn.execute("DROP TABLE IF EXISTS _tmp_ats_paso_peligro_legacy_controls")


def _migrate_ats_trabajador_schema(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "ats_trabajador"):
        conn.execute(
            """
            CREATE TABLE ats_trabajador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ats_id INTEGER NOT NULL,
                numero_orden INTEGER NOT NULL CHECK (numero_orden > 0),
                nombre_trabajador TEXT NOT NULL,
                numero_documento TEXT NOT NULL,
                cargo_trabajador TEXT,
                firma_base64 TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                trabajador_id INTEGER,
                nombre_snapshot TEXT,
                documento_snapshot TEXT,
                cargo_snapshot TEXT,
                FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
                UNIQUE (ats_id, numero_orden)
            )
            """
        )
        return

    _add_column_if_missing(conn, "ats_trabajador", "trabajador_id INTEGER")
    _add_column_if_missing(conn, "ats_trabajador", "nombre_snapshot TEXT")
    _add_column_if_missing(conn, "ats_trabajador", "documento_snapshot TEXT")
    _add_column_if_missing(conn, "ats_trabajador", "cargo_snapshot TEXT")

    conn.execute(
        """
        UPDATE ats_trabajador
        SET nombre_snapshot = COALESCE(NULLIF(TRIM(nombre_snapshot), ''), nombre_trabajador),
            documento_snapshot = COALESCE(NULLIF(TRIM(documento_snapshot), ''), numero_documento),
            cargo_snapshot = COALESCE(NULLIF(TRIM(cargo_snapshot), ''), cargo_trabajador)
        """
    )


def _backfill_worker_catalog_and_snapshots(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "trabajador") or not _table_exists(conn, "ats_trabajador"):
        return

    conn.execute(
        """
        INSERT INTO trabajador (uuid, numero_documento, nombre_completo, cargo, activo)
        SELECT
            lower(hex(randomblob(16))) AS uuid,
            src.documento,
            src.nombre,
            NULLIF(src.cargo, ''),
            1
        FROM (
            SELECT
                TRIM(COALESCE(documento_snapshot, numero_documento, '')) AS documento,
                TRIM(COALESCE(nombre_snapshot, nombre_trabajador, '')) AS nombre,
                TRIM(COALESCE(cargo_snapshot, cargo_trabajador, '')) AS cargo
            FROM ats_trabajador
        ) AS src
        LEFT JOIN trabajador t ON t.numero_documento = src.documento
        WHERE src.documento <> ''
          AND src.nombre <> ''
          AND t.id IS NULL
        GROUP BY src.documento
        """
    )

    conn.execute(
        """
        UPDATE ats_trabajador
        SET trabajador_id = (
            SELECT t.id
            FROM trabajador t
            WHERE t.numero_documento = TRIM(COALESCE(ats_trabajador.documento_snapshot, ats_trabajador.numero_documento, ''))
            LIMIT 1
        )
        WHERE COALESCE(trabajador_id, 0) <= 0
        """
    )

    conn.execute(
        """
        UPDATE ats_trabajador
        SET nombre_snapshot = COALESCE(NULLIF(TRIM(nombre_snapshot), ''), (
                SELECT t.nombre_completo
                FROM trabajador t
                WHERE t.id = ats_trabajador.trabajador_id
                LIMIT 1
            )),
            documento_snapshot = COALESCE(NULLIF(TRIM(documento_snapshot), ''), (
                SELECT t.numero_documento
                FROM trabajador t
                WHERE t.id = ats_trabajador.trabajador_id
                LIMIT 1
            )),
            cargo_snapshot = COALESCE(NULLIF(TRIM(cargo_snapshot), ''), (
                SELECT t.cargo
                FROM trabajador t
                WHERE t.id = ats_trabajador.trabajador_id
                LIMIT 1
            ))
        """
    )

    conn.execute(
        """
        UPDATE ats_trabajador
        SET nombre_trabajador = COALESCE(NULLIF(TRIM(nombre_trabajador), ''), nombre_snapshot),
            numero_documento = COALESCE(NULLIF(TRIM(numero_documento), ''), documento_snapshot),
            cargo_trabajador = COALESCE(NULLIF(TRIM(cargo_trabajador), ''), cargo_snapshot)
        """
    )


def _create_missing_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trabajador_activo ON trabajador(activo)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trabajador_nombre ON trabajador(nombre_completo)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_control_catalogo_activo ON control_catalogo(activo)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_control_catalogo_tipo ON control_catalogo(tipo_control)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ats_trabajador_trabajador ON ats_trabajador(trabajador_id)")
    conn.execute("DROP INDEX IF EXISTS idx_ats_paso_peligro_control")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ats_paso_peligro_paso ON ats_paso_peligro(ats_paso_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_control_app ON ats_paso_peligro_control(ats_paso_peligro_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_control_control ON ats_paso_peligro_control(control_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ats_paso_ats ON ats_paso(ats_id)")


def _create_or_replace_views(conn: sqlite3.Connection) -> None:
    conn.execute("DROP VIEW IF EXISTS vw_ats_trabajador_snapshot")
    conn.execute(
        """
        CREATE VIEW vw_ats_trabajador_snapshot AS
        SELECT
            at.id AS ats_trabajador_id,
            a.id AS ats_id,
            a.uuid AS ats_uuid,
            a.codigo_publico,
            at.numero_orden,
            t.id AS trabajador_id,
            t.uuid AS trabajador_uuid,
            at.nombre_snapshot,
            at.documento_snapshot,
            at.cargo_snapshot,
            at.firma_base64,
            at.created_at
        FROM ats_trabajador at
        JOIN ats a ON a.id = at.ats_id
        LEFT JOIN trabajador t ON t.id = at.trabajador_id
        """
    )

    conn.execute("DROP VIEW IF EXISTS vw_ats_paso_peligro_control")
    conn.execute(
        """
        CREATE VIEW vw_ats_paso_peligro_control AS
        SELECT
            a.id AS ats_id,
            a.uuid AS ats_uuid,
            a.codigo_publico,
            p.id AS paso_id,
            p.numero_paso,
            p.descripcion_paso,
            app.id AS ats_paso_peligro_id,
            app.descripcion_otro AS peligro_descripcion_otro,
            pc.id AS peligro_catalogo_id,
            pc.codigo AS peligro_codigo,
            pc.nombre AS peligro_nombre,
            c.id AS control_id,
            c.codigo AS control_codigo,
            c.nombre AS control_nombre,
            appc.control_aplicado
        FROM ats_paso_peligro_control appc
        JOIN ats_paso_peligro app ON app.id = appc.ats_paso_peligro_id
        JOIN ats_paso p ON p.id = app.ats_paso_id
        JOIN ats_peligro ap ON ap.id = app.ats_peligro_id
        JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
        JOIN control_catalogo c ON c.id = appc.control_id
        JOIN ats a ON a.id = p.ats_id
        """
    )


def _seed_control_catalog(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "control_catalogo"):
        return

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM control_catalogo")
    total_rows = int(cur.fetchone()[0] or 0)

    if total_rows <= 0:
        cur.executemany(
            """
            INSERT INTO control_catalogo (
                codigo,
                nombre,
                descripcion,
                tipo_control,
                permite_descripcion_libre,
                activo
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            CONTROL_SEED_ROWS,
        )
    else:
        cur.execute("SELECT UPPER(COALESCE(codigo, '')) FROM control_catalogo")
        existing_codes = {str(row[0] or "").strip().upper() for row in cur.fetchall()}
        pending_rows = [row for row in CONTROL_SEED_ROWS if str(row[0]).strip().upper() not in existing_codes]
        if pending_rows:
            cur.executemany(
                """
                INSERT INTO control_catalogo (
                    codigo,
                    nombre,
                    descripcion,
                    tipo_control,
                    permite_descripcion_libre,
                    activo
                )
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                pending_rows,
            )

    otros_id = _ensure_otro_control_id(conn)

    if otros_id > 0 and _table_exists(conn, "ats_paso_peligro_control"):
        cur.execute(
            """
            UPDATE ats_paso_peligro_control
            SET control_id = ?
            WHERE COALESCE(control_id, 0) <= 0
              AND COALESCE(TRIM(control_aplicado), '') <> ''
            """,
            (otros_id,),
        )
        cur.execute(
            """
            UPDATE ats_paso_peligro_control
            SET control_aplicado = COALESCE(
                NULLIF(TRIM(control_aplicado), ''),
                (SELECT c.nombre FROM control_catalogo c WHERE c.id = ats_paso_peligro_control.control_id LIMIT 1),
                'OTROS'
            )
            WHERE COALESCE(TRIM(control_aplicado), '') = ''
            """
        )

    conn.commit()


def _seed_demo_users(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuario")
    total_users = int(cur.fetchone()[0] or 0)
    if total_users > 0:
        return

    cur.execute("SELECT id, codigo FROM rol")
    roles = {codigo: role_id for role_id, codigo in cur.fetchall()}

    demo_users = [
        {
            "rol_codigo": "ADMIN",
            "nombre_completo": "Administrador Demo",
            "email": "admin@example.local",
            "username": "admin",
            "password": "Admin123*",
        },
        {
            "rol_codigo": "SISO",
            "nombre_completo": "Responsable SST Demo",
            "email": "siso@example.local",
            "username": "siso",
            "password": "Siso123*",
        },
    ]

    for user in demo_users:
        role_id = roles.get(user["rol_codigo"])
        if role_id is None:
            continue
        cur.execute(
            """
            INSERT INTO usuario (
                uuid, rol_id, nombre_completo, email, username, password_hash, activo
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                str(uuid.uuid4()),
                role_id,
                user["nombre_completo"],
                user["email"],
                user["username"],
                hash_password(user["password"]),
            ),
        )

    conn.commit()
