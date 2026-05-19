from __future__ import annotations

from typing import Optional

import reflex as rx
from sqlmodel import Field


class Rol(rx.Model, table=True):
    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    activo: int = 1


class Usuario(rx.Model, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    rol_id: int = Field(foreign_key="rol.id")
    nombre_completo: str
    email: Optional[str] = Field(default=None, unique=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    activo: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AtsEstado(rx.Model, table=True):
    __tablename__ = "ats_estado"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    orden: int
    activo: int = 1


class AtsTipo(rx.Model, table=True):
    __tablename__ = "ats_tipo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    activo: int = 1


class ApoyoCatalogo(rx.Model, table=True):
    __tablename__ = "apoyo_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: int = 0
    orden: int
    activo: int = 1


class CertificadoCatalogo(rx.Model, table=True):
    __tablename__ = "certificado_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: int = 0
    orden: int
    activo: int = 1


class PeligroCatalogo(rx.Model, table=True):
    __tablename__ = "peligro_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    numero_visual: int = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: int = 0
    orden: int
    activo: int = 1


class ControlCatalogo(rx.Model, table=True):
    __tablename__ = "control_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    descripcion: Optional[str] = None
    tipo_control: Optional[str] = None
    permite_descripcion_libre: int = 0
    activo: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Trabajador(rx.Model, table=True):
    __tablename__ = "trabajador"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    numero_documento: str = Field(index=True, unique=True)
    nombre_completo: str
    cargo: Optional[str] = None
    activo: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FirmaTipoCatalogo(rx.Model, table=True):
    __tablename__ = "firma_tipo_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    orden: int
    activo: int = 1
