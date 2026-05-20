-- ATS / SST schema for SQLite
-- Ready to execute in SQLite / DB Browser for SQLite / sqlite3 CLI
-- Project target: Reflex + SQLite
-- Encoding: UTF-8

PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- Drop views first
DROP VIEW IF EXISTS vw_ats_paso_peligro_control;
DROP VIEW IF EXISTS vw_ats_trabajador_snapshot;
DROP VIEW IF EXISTS vw_ats_metrica_por_peligro;
DROP VIEW IF EXISTS vw_ats_metrica_por_estado;
DROP VIEW IF EXISTS vw_ats_resumen;

-- Drop triggers
DROP TRIGGER IF EXISTS trg_usuario_updated_at;
DROP TRIGGER IF EXISTS trg_ats_updated_at;
DROP TRIGGER IF EXISTS trg_ats_paso_updated_at;
DROP TRIGGER IF EXISTS trg_ats_trabajador_updated_at;
DROP TRIGGER IF EXISTS trg_ats_firma_final_updated_at;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS ats_documento;
DROP TABLE IF EXISTS ats_firma_final;
DROP TABLE IF EXISTS ats_trabajador;
DROP TABLE IF EXISTS ats_paso_peligro_control;
DROP TABLE IF EXISTS ats_paso_peligro;
DROP TABLE IF EXISTS ats_paso;
DROP TABLE IF EXISTS ats_peligro;
DROP TABLE IF EXISTS ats_certificado;
DROP TABLE IF EXISTS ats_apoyo;
DROP TABLE IF EXISTS ats;
DROP TABLE IF EXISTS firma_tipo_catalogo;
DROP TABLE IF EXISTS control_catalogo;
DROP TABLE IF EXISTS trabajador;
DROP TABLE IF EXISTS peligro_catalogo;
DROP TABLE IF EXISTS certificado_catalogo;
DROP TABLE IF EXISTS apoyo_catalogo;
DROP TABLE IF EXISTS ats_tipo;
DROP TABLE IF EXISTS ats_estado;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS rol;

COMMIT;

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- =========================================================
-- 1) SEGURIDAD
-- =========================================================

CREATE TABLE rol (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL UNIQUE,
    rol_id INTEGER NOT NULL,
    nombre_completo TEXT NOT NULL,
    email TEXT UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES rol(id)
);

-- =========================================================
-- 2) CATALOGOS ATS
-- =========================================================

CREATE TABLE ats_estado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    orden INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE ats_tipo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE apoyo_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1)),
    orden INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE certificado_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1)),
    orden INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE peligro_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    numero_visual INTEGER NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1)),
    orden INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE control_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo_control TEXT,
    permite_descripcion_libre INTEGER NOT NULL DEFAULT 0 CHECK (permite_descripcion_libre IN (0,1)),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trabajador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL UNIQUE,
    numero_documento TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    cargo TEXT,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE firma_tipo_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    orden INTEGER NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

-- =========================================================
-- 3) ENTIDADES PRINCIPALES DEL ATS
-- =========================================================

CREATE TABLE ats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL UNIQUE,
    codigo_publico TEXT NOT NULL UNIQUE,
    estado_id INTEGER NOT NULL,
    tipo_ats_id INTEGER NOT NULL,
    creado_por_usuario_id INTEGER NOT NULL,

    empresa_persona_ejecuta TEXT NOT NULL,
    fecha_elaboracion TEXT NOT NULL, -- ISO: YYYY-MM-DD
    ciudad TEXT NOT NULL,
    area_lugar TEXT NOT NULL,
    numero_ats TEXT,
    duracion_actividad TEXT NOT NULL,
    actividad_alto_riesgo INTEGER NOT NULL DEFAULT 0 CHECK (actividad_alto_riesgo IN (0,1)),
    descripcion_actividad TEXT NOT NULL,
    observaciones TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (estado_id) REFERENCES ats_estado(id),
    FOREIGN KEY (tipo_ats_id) REFERENCES ats_tipo(id),
    FOREIGN KEY (creado_por_usuario_id) REFERENCES usuario(id)
);

CREATE TABLE ats_apoyo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    apoyo_id INTEGER NOT NULL,
    descripcion_otro TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (apoyo_id) REFERENCES apoyo_catalogo(id),
    UNIQUE (ats_id, apoyo_id)
);

CREATE TABLE ats_certificado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    certificado_id INTEGER NOT NULL,
    descripcion_otro TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (certificado_id) REFERENCES certificado_catalogo(id),
    UNIQUE (ats_id, certificado_id)
);

CREATE TABLE ats_peligro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    peligro_id INTEGER NOT NULL,
    descripcion_otro TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (peligro_id) REFERENCES peligro_catalogo(id),
    UNIQUE (ats_id, peligro_id)
);

CREATE TABLE ats_paso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    numero_paso INTEGER NOT NULL CHECK (numero_paso > 0),
    descripcion_paso TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    UNIQUE (ats_id, numero_paso)
);

CREATE TABLE ats_paso_peligro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_paso_id INTEGER NOT NULL,
    ats_peligro_id INTEGER NOT NULL,
    descripcion_otro TEXT,
    FOREIGN KEY (ats_paso_id) REFERENCES ats_paso(id) ON DELETE CASCADE,
    FOREIGN KEY (ats_peligro_id) REFERENCES ats_peligro(id) ON DELETE CASCADE,
    UNIQUE (ats_paso_id, ats_peligro_id)
);

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
);

CREATE TABLE ats_trabajador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    numero_orden INTEGER NOT NULL CHECK (numero_orden > 0),
    nombre_trabajador TEXT NOT NULL,
    numero_documento TEXT NOT NULL,
    cargo_trabajador TEXT,
    firma_base64 TEXT,
    trabajador_id INTEGER,
    nombre_snapshot TEXT,
    documento_snapshot TEXT,
    cargo_snapshot TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (trabajador_id) REFERENCES trabajador(id),
    UNIQUE (ats_id, numero_orden)
);

CREATE TABLE ats_firma_final (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    firma_tipo_id INTEGER NOT NULL,
    nombre_completo TEXT NOT NULL,
    cargo TEXT,
    firma_base64 TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (firma_tipo_id) REFERENCES firma_tipo_catalogo(id),
    UNIQUE (ats_id, firma_tipo_id)
);

CREATE TABLE ats_documento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ats_id INTEGER NOT NULL,
    tipo_documento TEXT NOT NULL,   -- PDF, DOCX, etc.
    nombre_archivo TEXT NOT NULL,
    ruta_archivo TEXT NOT NULL,
    mime_type TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    generado_por_usuario_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ats_id) REFERENCES ats(id) ON DELETE CASCADE,
    FOREIGN KEY (generado_por_usuario_id) REFERENCES usuario(id)
);

-- =========================================================
-- 4) INDICES
-- =========================================================

CREATE INDEX idx_usuario_rol ON usuario(rol_id);
CREATE INDEX idx_ats_estado ON ats(estado_id);
CREATE INDEX idx_ats_tipo ON ats(tipo_ats_id);
CREATE INDEX idx_ats_fecha ON ats(fecha_elaboracion);
CREATE INDEX idx_ats_creado_por ON ats(creado_por_usuario_id);
CREATE INDEX idx_ats_apoyo_ats ON ats_apoyo(ats_id);
CREATE INDEX idx_ats_certificado_ats ON ats_certificado(ats_id);
CREATE INDEX idx_ats_peligro_ats ON ats_peligro(ats_id);
CREATE INDEX idx_ats_paso_ats ON ats_paso(ats_id);
CREATE INDEX idx_ats_paso_peligro_paso ON ats_paso_peligro(ats_paso_id);
CREATE INDEX idx_app_control_app ON ats_paso_peligro_control(ats_paso_peligro_id);
CREATE INDEX idx_app_control_control ON ats_paso_peligro_control(control_id);
CREATE INDEX idx_ats_trabajador_ats ON ats_trabajador(ats_id);
CREATE INDEX idx_ats_trabajador_trabajador ON ats_trabajador(trabajador_id);
CREATE INDEX idx_ats_firma_final_ats ON ats_firma_final(ats_id);
CREATE INDEX idx_ats_documento_ats ON ats_documento(ats_id);
CREATE INDEX idx_control_catalogo_activo ON control_catalogo(activo);
CREATE INDEX idx_control_catalogo_tipo ON control_catalogo(tipo_control);
CREATE INDEX idx_trabajador_activo ON trabajador(activo);
CREATE INDEX idx_trabajador_nombre ON trabajador(nombre_completo);

-- =========================================================
-- 5) TRIGGERS PARA updated_at
-- =========================================================

CREATE TRIGGER trg_usuario_updated_at
AFTER UPDATE ON usuario
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE usuario
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;

CREATE TRIGGER trg_ats_updated_at
AFTER UPDATE ON ats
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE ats
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;

CREATE TRIGGER trg_ats_paso_updated_at
AFTER UPDATE ON ats_paso
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE ats_paso
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;

CREATE TRIGGER trg_ats_trabajador_updated_at
AFTER UPDATE ON ats_trabajador
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE ats_trabajador
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;

CREATE TRIGGER trg_ats_firma_final_updated_at
AFTER UPDATE ON ats_firma_final
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE ats_firma_final
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;

-- =========================================================
-- 6) VISTAS DE APOYO PARA DASHBOARD / CONSULTAS
-- =========================================================

CREATE VIEW vw_ats_resumen AS
SELECT
    a.id,
    a.uuid,
    a.codigo_publico,
    a.fecha_elaboracion,
    a.ciudad,
    a.area_lugar,
    a.numero_ats,
    a.empresa_persona_ejecuta,
    a.duracion_actividad,
    a.actividad_alto_riesgo,
    a.descripcion_actividad,
    a.observaciones,
    e.codigo AS estado_codigo,
    e.nombre AS estado_nombre,
    t.codigo AS tipo_codigo,
    t.nombre AS tipo_nombre,
    u.username AS creado_por_username,
    u.nombre_completo AS creado_por_nombre,
    a.created_at,
    a.updated_at
FROM ats a
JOIN ats_estado e ON e.id = a.estado_id
JOIN ats_tipo t ON t.id = a.tipo_ats_id
JOIN usuario u ON u.id = a.creado_por_usuario_id;

CREATE VIEW vw_ats_metrica_por_estado AS
SELECT
    e.id AS estado_id,
    e.codigo AS estado_codigo,
    e.nombre AS estado_nombre,
    COUNT(a.id) AS total_ats
FROM ats_estado e
LEFT JOIN ats a
       ON a.estado_id = e.id
GROUP BY e.id, e.codigo, e.nombre
ORDER BY e.orden;

CREATE VIEW vw_ats_metrica_por_peligro AS
SELECT
    p.id AS peligro_id,
    p.numero_visual,
    p.codigo AS peligro_codigo,
    p.nombre AS peligro_nombre,
    COUNT(ap.id) AS total_selecciones
FROM peligro_catalogo p
LEFT JOIN ats_peligro ap
       ON ap.peligro_id = p.id
GROUP BY p.id, p.numero_visual, p.codigo, p.nombre
ORDER BY p.orden;

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
LEFT JOIN trabajador t ON t.id = at.trabajador_id;

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
JOIN ats a ON a.id = p.ats_id;

-- =========================================================
-- 7) DATOS SEMILLA
-- =========================================================

INSERT INTO rol (codigo, nombre, activo) VALUES
('ADMIN', 'Administrador', 1),
('SISO', 'Responsable SST', 1);

INSERT INTO ats_estado (codigo, nombre, orden, activo) VALUES
('BORRADOR', 'Borrador', 1, 1),
('EN_PROCESO', 'En proceso', 2, 1),
('FINALIZADO', 'Finalizado', 3, 1),
('DOCUMENTO_GENERADO', 'Documento generado', 4, 1),
('ANULADO', 'Anulado', 5, 1);

INSERT INTO ats_tipo (codigo, nombre, activo) VALUES
('NUEVO', 'Nuevo', 1),
('REVISION', 'Revisión', 1);

INSERT INTO apoyo_catalogo (codigo, nombre, permite_descripcion_libre, orden, activo) VALUES
('PROGRAMA', 'Programa', 0, 1, 1),
('PROCEDIMIENTO', 'Procedimiento', 0, 2, 1),
('INSTRUCTIVO', 'Instructivo', 0, 3, 1),
('ORDEN_SERVICIO', 'Orden de Servicio', 0, 4, 1),
('PLAN_EMERGENCIA', 'Plan de Emergencia', 0, 5, 1),
('PROC_MANTENIMIENTO', 'Procedimiento de Mantenimiento', 0, 6, 1),
('OTROS', 'Otros', 1, 7, 1);

INSERT INTO certificado_catalogo (codigo, nombre, permite_descripcion_libre, orden, activo) VALUES
('ALTURAS', 'Alturas', 0, 1, 1),
('ELECTRICOS', 'Eléctricos', 0, 2, 1),
('ESPACIOS_CONFINADOS', 'Espacios Confinados', 0, 3, 1),
('TRABAJOS_EN_CALIENTE', 'Trabajos en Caliente', 0, 4, 1),
('OTROS', 'Otros', 1, 5, 1);

INSERT INTO peligro_catalogo (codigo, numero_visual, nombre, permite_descripcion_libre, orden, activo) VALUES
('CAIDA_PERSONA_DISTINTO_NIVEL', 1, 'Caídas de Persona a Distinto Nivel', 0, 1, 1),
('CAIDA_PERSONA_MISMO_NIVEL', 2, 'Caídas de Persona al Mismo Nivel', 0, 2, 1),
('CAIDA_OBJETOS_DESPLOME', 3, 'Caída de Objetos por Desplome', 0, 3, 1),
('CAIDA_OBJETOS_MANIPULACION', 4, 'Caídas de Objetos por Manipulación', 0, 4, 1),
('CHOQUES_GOLPES_CONTRA', 5, 'Choques o Golpes con o Contra', 0, 5, 1),
('CORTES_HERRAMIENTAS_OBJETOS', 6, 'Cortes por Herramientas u Objetos', 0, 6, 1),
('PROYECCION_PARTICULAS', 7, 'Proyección de Partículas', 0, 7, 1),
('ATRAPAMIENTO_APLASTAMIENTO', 8, 'Atrapamiento o Aplastamiento', 0, 8, 1),
('CONTACTO_ENERGIAS_PELIGROSAS', 9, 'Contacto con Energías Peligrosas', 0, 9, 1),
('TRABAJO_EN_CALIENTE', 10, 'Trabajo en Caliente', 0, 10, 1),
('CAIDAS_DE_ALTURAS', 11, 'Caídas de Alturas', 0, 11, 1),
('INGRESO_ESPACIO_CONFINADO', 12, 'Ingreso a Espacio Confinado', 0, 12, 1),
('SOBREESFUERZOS', 13, 'Sobreesfuerzos', 0, 13, 1),
('POSTURAS_PROLONGADAS', 14, 'Posturas Prolongadas o Incómodas', 0, 14, 1),
('MANIPULACION_MANUAL_CARGAS', 15, 'Manipulación Manual de Cargas', 0, 15, 1),
('MOVIMIENTOS_REPETITIVOS', 16, 'Movimientos Repetitivos', 0, 16, 1),
('EXPOSICION_SUSTANCIAS_QUIMICAS', 17, 'Exposición o Contacto con Sustancias Químicas', 0, 17, 1),
('EXPOSICION_GASES_VAPORES_POLVOS', 18, 'Exposición a Gases, Vapores o Polvos', 0, 18, 1),
('CONTACTO_AGENTES_BIOLOGICOS', 19, 'Contactos con Agentes Biológicos', 0, 19, 1),
('EXPOSICION_TEMPERATURAS_EXTREMAS', 20, 'Exposición a Temperaturas Extremas', 0, 20, 1),
('RUIDO', 21, 'Ruido (Impacto, Continuo, Intermitente)', 0, 21, 1),
('RADIACIONES', 22, 'Radiaciones (Ionizantes, No Ionizantes)', 0, 22, 1),
('VIBRACIONES', 23, 'Vibraciones (Segmentos, Cuerpo Entero)', 0, 23, 1),
('LUZ_EXCESO_DEFICIENTE', 24, 'Luz en Exceso o Deficiente', 0, 24, 1),
('INCENDIO_EXPLOSION', 25, 'Incendio o Explosión', 0, 25, 1),
('DERRAME_SUSTANCIAS', 26, 'Derrame de Sustancias', 0, 26, 1),
('ACCIDENTES_TRANSITO', 27, 'Accidentes de Tránsito', 0, 27, 1),
('ORDEN_PUBLICO', 28, 'Orden Público', 0, 28, 1),
('OTRO_PELIGRO', 29, 'Otro Peligro', 1, 29, 1);

INSERT INTO control_catalogo (
    codigo, nombre, descripcion, tipo_control, permite_descripcion_libre, activo
) VALUES
('USO_EPP_BASICO', 'Uso obligatorio de EPP basico', 'Casco, gafas, guantes, botas y proteccion auditiva segun actividad.', 'EPP', 0, 1),
('ARNES_LINEA_VIDA', 'Arnes y linea de vida certificados', 'Verificar puntos de anclaje, inspeccion preuso y certificacion vigente.', 'EPP', 0, 1),
('DELIMITACION_AREA', 'Delimitacion y senalizacion del area', 'Instalar conos, cinta, barreras y avisos preventivos.', 'Administrativo', 0, 1),
('BLOQUEO_ETIQUETADO', 'Bloqueo y etiquetado de energias', 'Aplicar LOTO, verificar ausencia de energia y liberar solo con autorizacion.', 'Ingenieria', 0, 1),
('PERMISO_TRABAJO', 'Permiso de trabajo aprobado', 'Validar permiso, alcance, responsables, vigencia y condiciones de seguridad.', 'Administrativo', 0, 1),
('INSPECCION_HERRAMIENTAS', 'Inspeccion preoperacional de herramientas', 'Retirar herramientas defectuosas y registrar hallazgos.', 'Administrativo', 0, 1),
('ORDEN_ASEO', 'Orden y aseo permanente', 'Mantener rutas libres, retirar obstaculos y controlar residuos.', 'Administrativo', 0, 1),
('VENTILACION_MONITOREO', 'Ventilacion y monitoreo atmosferico', 'Verificar condiciones de oxigeno, gases y ventilacion antes y durante la tarea.', 'Ingenieria', 0, 1),
('EXTINTOR_VIGIA', 'Extintor y vigia de seguridad', 'Disponer extintor, vigia y control de fuentes de ignicion.', 'Administrativo', 0, 1),
('PAUSAS_ACTIVAS', 'Pausas activas y manejo ergonomico', 'Aplicar tecnicas de levantamiento, rotacion de tareas y pausas activas.', 'Administrativo', 0, 1),
('CONTROL_CAIDA_OBJETOS', 'Control de caida de objetos', 'Usar amarre de herramientas, rodapies y exclusion de area inferior.', 'Ingenieria', 0, 1),
('COMUNICACION_PERMANENTE', 'Comunicacion permanente del equipo', 'Mantener radio/telefono operativo y canal de comunicacion definido.', 'Administrativo', 0, 1),
('OTROS', 'OTROS', 'Control definido manualmente por SISO cuando no existe en catalogo.', 'Otro', 1, 1);

INSERT INTO firma_tipo_catalogo (codigo, nombre, orden, activo) VALUES
('AUTORIZA', 'Autoriza Actividad SST', 1, 1),
('SUPERVISA', 'Supervisa Actividad SST', 2, 1),
('EJECUTA', 'Ejecuta Actividad', 3, 1);

COMMIT;

-- =========================================================
-- 8) NOTAS DE USO
-- =========================================================
-- 1. Este script no inserta usuarios por defecto para no forzar
--    una estrategia concreta de hashing de contraseñas.
-- 2. Se recomienda guardar fecha_elaboracion en formato ISO:
--    YYYY-MM-DD
-- 3. Las firmas se almacenan como base64 para el prototipo.
--    Más adelante se pueden migrar a archivos + ruta.
-- 4. codigo_publico puede ser algo como:
--    ATS-2026-0001
-- 5. Para eliminar un ATS y todos sus detalles asociados,
--    basta con borrar el registro de la tabla ats.
