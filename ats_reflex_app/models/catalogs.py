from __future__ import annotations

from datetime import datetime
from typing import Optional

import reflex as rx
from sqlmodel import Field


class Rol(rx.Model, table=True):
    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    activo: bool = True


class Usuario(rx.Model, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    auth_user_id: Optional[str] = Field(default=None, unique=True, index=True)
    rol_id: int = Field(foreign_key="rol.id")
    nombre_completo: str
    email: Optional[str] = Field(default=None, unique=True)
    username: str = Field(index=True, unique=True)
    password_hash: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AtsEstado(rx.Model, table=True):
    __tablename__ = "ats_estado"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    orden: int
    activo: bool = True


class AtsTipo(rx.Model, table=True):
    __tablename__ = "ats_tipo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    activo: bool = True


class ApoyoCatalogo(rx.Model, table=True):
    __tablename__ = "apoyo_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: bool = False
    orden: int
    activo: bool = True


class CertificadoCatalogo(rx.Model, table=True):
    __tablename__ = "certificado_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: bool = False
    orden: int
    activo: bool = True


class PeligroCatalogo(rx.Model, table=True):
    __tablename__ = "peligro_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    numero_visual: int = Field(index=True, unique=True)
    nombre: str
    permite_descripcion_libre: bool = False
    orden: int
    activo: bool = True


class ControlCatalogo(rx.Model, table=True):
    __tablename__ = "control_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    descripcion: Optional[str] = None
    tipo_control: Optional[str] = None
    permite_descripcion_libre: bool = False
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Trabajador(rx.Model, table=True):
    __tablename__ = "trabajador"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    numero_documento: str = Field(index=True, unique=True)
    nombre_completo: str
    cargo: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FirmaTipoCatalogo(rx.Model, table=True):
    __tablename__ = "firma_tipo_catalogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True)
    nombre: str
    orden: int
    activo: bool = True
