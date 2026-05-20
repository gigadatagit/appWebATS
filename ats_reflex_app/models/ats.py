from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import reflex as rx
from sqlmodel import Field


class Ats(rx.Model, table=True):
    __tablename__ = "ats"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    codigo_publico: str = Field(index=True, unique=True)
    estado_id: int = Field(foreign_key="ats_estado.id")
    tipo_ats_id: int = Field(foreign_key="ats_tipo.id")
    creado_por_usuario_id: int = Field(foreign_key="usuario.id")

    empresa_persona_ejecuta: str
    fecha_elaboracion: date
    ciudad: str
    area_lugar: str
    numero_ats: Optional[str] = None
    duracion_actividad: str
    actividad_alto_riesgo: bool = False
    descripcion_actividad: str
    observaciones: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsApoyo(rx.Model, table=True):
    __tablename__ = "ats_apoyo"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    apoyo_id: int = Field(foreign_key="apoyo_catalogo.id")
    descripcion_otro: Optional[str] = None
    created_at: Optional[datetime] = None


class AtsCertificado(rx.Model, table=True):
    __tablename__ = "ats_certificado"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    certificado_id: int = Field(foreign_key="certificado_catalogo.id")
    descripcion_otro: Optional[str] = None
    created_at: Optional[datetime] = None


class AtsPeligro(rx.Model, table=True):
    __tablename__ = "ats_peligro"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    peligro_id: int = Field(foreign_key="peligro_catalogo.id")
    descripcion_otro: Optional[str] = None
    created_at: Optional[datetime] = None


class AtsPaso(rx.Model, table=True):
    __tablename__ = "ats_paso"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    numero_paso: int
    descripcion_paso: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsPasoPeligro(rx.Model, table=True):
    __tablename__ = "ats_paso_peligro"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_paso_id: int = Field(foreign_key="ats_paso.id")
    ats_peligro_id: int = Field(foreign_key="ats_peligro.id")
    descripcion_otro: Optional[str] = None


class AtsPasoPeligroControl(rx.Model, table=True):
    __tablename__ = "ats_paso_peligro_control"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_paso_peligro_id: int = Field(foreign_key="ats_paso_peligro.id")
    control_id: int = Field(foreign_key="control_catalogo.id")
    control_aplicado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsTrabajador(rx.Model, table=True):
    __tablename__ = "ats_trabajador"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    numero_orden: int
    nombre_trabajador: str
    numero_documento: str
    cargo_trabajador: Optional[str] = None
    firma_base64: Optional[str] = None
    trabajador_id: Optional[int] = Field(default=None, foreign_key="trabajador.id")
    nombre_snapshot: Optional[str] = None
    documento_snapshot: Optional[str] = None
    cargo_snapshot: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsFirmaFinal(rx.Model, table=True):
    __tablename__ = "ats_firma_final"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    firma_tipo_id: int = Field(foreign_key="firma_tipo_catalogo.id")
    nombre_completo: str
    cargo: Optional[str] = None
    firma_base64: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsDocumento(rx.Model, table=True):
    __tablename__ = "ats_documento"

    id: Optional[int] = Field(default=None, primary_key=True)
    ats_id: int = Field(foreign_key="ats.id")
    tipo_documento: str
    nombre_archivo: str
    ruta_archivo: str
    mime_type: Optional[str] = None
    version: int = 1
    generado_por_usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    created_at: Optional[datetime] = None
