from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import TypedDict

import reflex as rx
from sqlalchemy import text, delete
from sqlmodel import select

from ..access_control import (
    AccessDeniedError,
    assert_can_access_ats,
    assert_can_edit_ats,
    get_current_auth_context,
    is_admin,
    is_siso,
    resolve_ats_id_by_codigo,
    resolve_ats_id_by_uuid,
)
from ..models import (
    ApoyoCatalogo,
    AtsEstado,
    Ats,
    AtsApoyo,
    AtsCertificado,
    AtsDocumento,
    AtsFirmaFinal,
    AtsPaso,
    AtsPasoPeligro,
    AtsPasoPeligroControl,
    AtsPeligro,
    AtsTipo,
    CertificadoCatalogo,
    ControlCatalogo,
    FirmaTipoCatalogo,
    PeligroCatalogo,
    Trabajador,
    AtsTrabajador,
)
from ..config import get_ats_pdf_engine, get_supabase_signed_url_ttl_seconds
from ..docx_template_pdf import generate_pdf_bytes_from_template
from ..storage_supabase import (
    create_signed_file_url,
    delete_file_if_exists,
    upload_pdf_bytes,
)
from .session_state import SessionState


class PasoPeligroControlItem(TypedDict):
    uid: str
    id: int
    control_id: int
    control_nombre: str
    control_aplicado: str


class PasoPeligroItem(TypedDict):
    uid: str
    id: int
    peligro_id: int
    peligro_numero: int
    peligro_nombre: str
    descripcion_otro: str
    controls: list[PasoPeligroControlItem]


class PasoActividadItem(TypedDict):
    uid: str
    id: int
    numero_paso: int
    descripcion_paso: str
    peligros: list[PasoPeligroItem]


class TrabajadorActividadItem(TypedDict):
    uid: str
    id: int
    numero_orden: int
    trabajador_id: int
    nombre_trabajador: str
    numero_documento: str
    cargo_trabajador: str
    firma_base64: str


class FirmaFinalItem(TypedDict):
    uid: str
    id: int
    firma_tipo_id: int
    firma_tipo_codigo: str
    firma_tipo_nombre: str
    nombre_completo: str
    cargo: str
    firma_base64: str


class AtsFormState(rx.State):
    ATS_ESTADO_BORRADOR: str = "BORRADOR"
    ATS_ESTADO_EN_PROCESO: str = "EN_PROCESO"
    ATS_ESTADO_FINALIZADO: str = "FINALIZADO"
    ATS_ESTADO_DOCUMENTO_GENERADO: str = "DOCUMENTO_GENERADO"
    PELIGRO_OTRO_CODIGO: str = "OTRO_PELIGRO"

    current_step: int = 1

    ats_id: int = 0
    ats_uuid: str = ""
    codigo_publico: str = ""

    empresa_persona_ejecuta: str = ""
    fecha_elaboracion: str = str(date.today())
    ciudad: str = ""
    area_lugar: str = ""
    numero_ats: str = ""
    tipo_ats_id: int = 0
    duracion_actividad: str = ""
    actividad_alto_riesgo: bool = False
    descripcion_actividad: str = ""
    observaciones: str = ""

    tipos_ats: list[dict] = []
    firma_tipos_catalogo: list[dict] = []
    apoyos_catalogo: list[dict] = []
    certificados_catalogo: list[dict] = []
    peligros_catalogo: list[dict] = []
    controles_catalogo: list[dict] = []
    trabajadores_catalogo: list[dict] = []
    ats_recientes: list[dict] = []
    documentos_ats_options: list[dict] = []
    documentos_generados: list[dict] = []

    apoyos_seleccionados: list[int] = []
    certificados_seleccionados: list[int] = []
    load_codigo_input: str = ""
    documento_search_query: str = ""
    documento_selected_ats_id: int = 0
    documento_selected_codigo: str = ""
    documento_generado_url: str = ""
    documento_generado_nombre: str = ""
    documento_error: str = ""
    documento_success: str = ""
    current_auth_user_id: str = ""
    current_user_id: int = 0
    current_user_role_codigo: str = ""
    pasos_actividad: list[PasoActividadItem] = []
    paso3_peligro_modal_open: bool = False
    paso3_peligro_modal_step_uid: str = ""
    paso3_peligro_search: str = ""
    trabajadores_actividad: list[TrabajadorActividadItem] = []
    trabajador_import_modal_open: bool = False
    trabajador_import_search: str = ""
    trabajador_import_selected_ids: list[int] = []
    firmas_finales: list[FirmaFinalItem] = []

    @rx.var
    def ats_recientes_options(self) -> list[str]:
        return [row["codigo_publico"] for row in self.ats_recientes]

    @rx.var
    def tipos_ats_options(self) -> list[dict]:
        return [{"label": t["nombre"], "value": str(t["id"])} for t in self.tipos_ats]

    @rx.var
    def peligros_seleccionados_ids(self) -> list[int]:
        return [int(item["id"]) for item in self.peligros_catalogo if item.get("seleccionado")]

    @rx.var
    def peligros_seleccionados_count(self) -> int:
        return len(self.peligros_seleccionados_ids)

    @rx.var
    def controles_catalogo_options(self) -> list[dict]:
        return [
            {
                "label": str(item.get("nombre") or ""),
                "value": str(int(item.get("id") or 0)),
                "id": int(item.get("id") or 0),
                "codigo": str(item.get("codigo") or ""),
                "permite_descripcion_libre": bool(item.get("permite_descripcion_libre")),
            }
            for item in self.controles_catalogo
            if int(item.get("id") or 0) > 0
        ]

    @rx.var
    def control_otro_id(self) -> int:
        return self._otro_control_id()

    @rx.var
    def paso3_otro_peligro_id(self) -> int:
        return self._otro_peligro_id()

    @rx.var
    def paso3_peligros_filtrados(self) -> list[dict]:
        selected_ids: set[int] = set()
        for paso in self.pasos_actividad:
            if str(paso.get("uid")) != str(self.paso3_peligro_modal_step_uid):
                continue
            for peligro in paso.get("peligros", []):
                selected_ids.add(int(peligro.get("peligro_id") or 0))
            break

        query = str(self.paso3_peligro_search or "").strip().lower()
        result: list[dict] = []
        for item in self.peligros_catalogo:
            peligro_id = int(item.get("id") or 0)
            if peligro_id <= 0 or peligro_id in selected_ids:
                continue

            numero = int(item.get("numero") or 0)
            nombre = str(item.get("nombre") or "")
            code = f"P{numero}"
            haystack = f"{code} {nombre}".lower()
            if query and query not in haystack and query not in str(numero):
                continue
            result.append({"id": peligro_id, "numero": numero, "nombre": nombre})
        return result

    @rx.var
    def trabajadores_importables_filtrados(self) -> list[dict]:
        imported_ids = {
            int(item.get("trabajador_id") or 0)
            for item in self.trabajadores_actividad
            if int(item.get("trabajador_id") or 0) > 0
        }
        query = str(self.trabajador_import_search or "").strip().lower()
        filtered: list[dict] = []
        for item in self.trabajadores_catalogo:
            trabajador_id = int(item.get("id") or 0)
            if trabajador_id <= 0 or trabajador_id in imported_ids:
                continue

            nombre = str(item.get("nombre_completo") or "")
            documento = str(item.get("numero_documento") or "")
            cargo = str(item.get("cargo") or "")
            haystack = f"{nombre} {documento}".lower()
            if query and query not in haystack:
                continue

            filtered.append(
                {
                    "id": trabajador_id,
                    "nombre_completo": nombre,
                    "numero_documento": documento,
                    "cargo": cargo,
                    "seleccionado": trabajador_id in {int(v) for v in self.trabajador_import_selected_ids},
                }
            )
        return filtered

    @rx.var
    def pasos_actividad_count(self) -> int:
        return len(self.pasos_actividad)

    @rx.var
    def trabajadores_actividad_count(self) -> int:
        return len(self.trabajadores_actividad)

    @rx.var
    def firmas_finales_count(self) -> int:
        return len(self.firmas_finales)

    form_error: str = ""
    form_success: str = ""

    def _sync_auth_context(self, session_state: SessionState):
        auth_context = get_current_auth_context(session_state)
        self.current_auth_user_id = auth_context.auth_user_id
        self.current_user_id = int(auth_context.current_user_id or 0)
        self.current_user_role_codigo = str(auth_context.current_user_role_codigo or "")
        return auth_context

    def _require_authenticated_context(self) -> tuple[int, str]:
        user_id = int(self.current_user_id or 0)
        role_code = str(self.current_user_role_codigo or "").strip().upper()
        auth_user_id = str(self.current_auth_user_id or "").strip()
        if user_id <= 0 or not role_code or not auth_user_id:
            raise AccessDeniedError("Sesion no valida. Inicia sesion nuevamente.")
        return user_id, role_code

    def _require_ats_role_context(self) -> tuple[int, str]:
        user_id, role_code = self._require_authenticated_context()
        if not (is_admin(role_code) or is_siso(role_code)):
            raise AccessDeniedError("Tu rol actual no tiene permisos para operar ATS.")
        return user_id, role_code

    def _assert_ats_access(self, session, ats_id: int, for_edit: bool = False):
        user_id, role_code = self._require_ats_role_context()
        if for_edit:
            assert_can_edit_ats(session, ats_id, user_id, role_code)
            return
        assert_can_access_ats(session, ats_id, user_id, role_code)

    @staticmethod
    def _parse_iso_date(value: str) -> date:
        raw = str(value or "").strip()
        if not raw:
            return date.today()
        try:
            return date.fromisoformat(raw)
        except Exception:
            return date.today()

    @staticmethod
    def _ats_scope_condition_sql(alias: str, current_user_id: int, role_code: str) -> tuple[str, dict[str, int]]:
        if is_admin(role_code):
            return "1 = 1", {}
        return f"{alias}.creado_por_usuario_id = :current_user_id", {"current_user_id": int(current_user_id or 0)}

    @staticmethod
    def _normalize_estado_codigo(value: str) -> str:
        return str(value or "").strip().upper()

    def _estado_priority(self, codigo: str) -> int:
        normalized = self._normalize_estado_codigo(codigo)
        if normalized == self.ATS_ESTADO_BORRADOR:
            return 1
        if normalized == self.ATS_ESTADO_EN_PROCESO:
            return 2
        if normalized == self.ATS_ESTADO_FINALIZADO:
            return 3
        if normalized == self.ATS_ESTADO_DOCUMENTO_GENERADO:
            return 4
        return 0

    def _resolve_estado_id_by_codigo_with_session(self, session, codigo: str) -> int:
        normalized = self._normalize_estado_codigo(codigo)
        if not normalized:
            raise RuntimeError("Codigo de estado ATS invalido.")
        row = session.exec(select(AtsEstado).where(AtsEstado.codigo == normalized)).first()
        estado_id = int(row.id or 0) if row else 0
        if estado_id <= 0:
            raise RuntimeError(f"No existe el estado {normalized} en la base.")
        return estado_id

    def _resolve_estado_codigo_by_id_with_session(self, session, estado_id: int) -> str:
        target_id = int(estado_id or 0)
        if target_id <= 0:
            return ""
        row = session.get(AtsEstado, target_id)
        return self._normalize_estado_codigo(str(row.codigo or "")) if row else ""

    def _mark_ats_dirty_after_document(self, current_estado_codigo: str, target_estado_codigo: str) -> str:
        current_code = self._normalize_estado_codigo(current_estado_codigo)
        target_code = self._normalize_estado_codigo(target_estado_codigo)
        if current_code == self.ATS_ESTADO_DOCUMENTO_GENERADO and target_code != self.ATS_ESTADO_DOCUMENTO_GENERADO:
            return self.ATS_ESTADO_EN_PROCESO
        return target_code

    def _resolve_effective_estado_transition(self, current_estado_codigo: str, target_estado_codigo: str) -> str:
        current_code = self._normalize_estado_codigo(current_estado_codigo)
        requested_target = self._normalize_estado_codigo(target_estado_codigo)
        if not requested_target:
            raise RuntimeError("Codigo de estado ATS invalido.")

        # Regla de retrabajo: si ya tuvo documento generado y se edita cualquier seccion,
        # el ATS vuelve a EN_PROCESO.
        post_document_target = self._mark_ats_dirty_after_document(current_code, requested_target)
        if post_document_target == self.ATS_ESTADO_EN_PROCESO and current_code == self.ATS_ESTADO_DOCUMENTO_GENERADO:
            return post_document_target

        current_priority = self._estado_priority(current_code)
        target_priority = self._estado_priority(post_document_target)

        # Regla de prioridad: no degradar progreso entre BORRADOR/EN_PROCESO/FINALIZADO.
        if current_priority > target_priority:
            return current_code
        return post_document_target

    def _set_ats_status_with_session(
        self,
        session,
        ats_id: int,
        target_estado_codigo: str,
        user_id: int,
        role_code: str,
    ) -> str:
        target_ats_id = int(ats_id or 0)
        if target_ats_id <= 0:
            raise RuntimeError("ATS invalido para actualizar estado.")

        # Seguridad de ownership/rol aplicada de forma centralizada.
        assert_can_edit_ats(session, target_ats_id, user_id, role_code)

        ats = session.get(Ats, target_ats_id)
        if ats is None:
            raise RuntimeError("ATS no encontrado para actualizar estado.")

        current_code = self._resolve_estado_codigo_by_id_with_session(session, int(ats.estado_id or 0))
        desired_code = self._resolve_effective_estado_transition(current_code, target_estado_codigo)
        desired_estado_id = self._resolve_estado_id_by_codigo_with_session(session, desired_code)

        if int(ats.estado_id or 0) != int(desired_estado_id):
            ats.estado_id = int(desired_estado_id)
            ats.updated_at = datetime.utcnow()
            session.add(ats)

        return desired_code

    def set_step(self, step: int):
        self.current_step = step

    def next_step(self):
        if self.current_step < 7:
            self.current_step += 1

    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1

    def set_tipo_ats_id(self, value: int):
        self.tipo_ats_id = value

    def set_tipo_ats_id_from_select(self, value: str):
        clean_value = (value or "").strip()
        self.tipo_ats_id = int(clean_value) if clean_value else 0

    def _apply_apoyos_selection(self, selected_map: dict[int, str]):
        merged: list[dict] = []
        for item in self.apoyos_catalogo:
            apoyo_id = int(item.get("id") or 0)
            allows_free_text = bool(item.get("permite_descripcion_libre"))
            raw_desc = selected_map.get(apoyo_id, "") if allows_free_text else ""
            descripcion_otro = "" if str(raw_desc or "").strip().upper() == "N/A" else str(raw_desc or "")
            merged.append(
                {
                    "id": apoyo_id,
                    "codigo": str(item.get("codigo") or ""),
                    "nombre": str(item.get("nombre") or ""),
                    "permite_descripcion_libre": allows_free_text,
                    "seleccionado": apoyo_id in selected_map,
                    "descripcion_otro": descripcion_otro,
                }
            )
        self.apoyos_catalogo = merged
        self.apoyos_seleccionados = [int(item["id"]) for item in merged if bool(item.get("seleccionado"))]

    def _apply_certificados_selection(self, selected_map: dict[int, str]):
        merged: list[dict] = []
        for item in self.certificados_catalogo:
            certificado_id = int(item.get("id") or 0)
            allows_free_text = bool(item.get("permite_descripcion_libre"))
            raw_desc = selected_map.get(certificado_id, "") if allows_free_text else ""
            descripcion_otro = "" if str(raw_desc or "").strip().upper() == "N/A" else str(raw_desc or "")
            merged.append(
                {
                    "id": certificado_id,
                    "codigo": str(item.get("codigo") or ""),
                    "nombre": str(item.get("nombre") or ""),
                    "permite_descripcion_libre": allows_free_text,
                    "seleccionado": certificado_id in selected_map,
                    "descripcion_otro": descripcion_otro,
                }
            )
        self.certificados_catalogo = merged
        self.certificados_seleccionados = [
            int(item["id"]) for item in merged if bool(item.get("seleccionado"))
        ]

    def _load_apoyos_selection_with_session(self, session, ats_id: int):
        if ats_id <= 0:
            self._apply_apoyos_selection({})
            return

        rows = session.exec(select(AtsApoyo).where(AtsApoyo.ats_id == ats_id)).all()
        selected_map: dict[int, str] = {
            int(row.apoyo_id or 0): str(row.descripcion_otro or "")
            for row in rows
            if int(row.apoyo_id or 0) > 0
        }
        self._apply_apoyos_selection(selected_map)

    def _load_certificados_selection_with_session(self, session, ats_id: int):
        if ats_id <= 0:
            self._apply_certificados_selection({})
            return

        rows = session.exec(select(AtsCertificado).where(AtsCertificado.ats_id == ats_id)).all()
        selected_map: dict[int, str] = {
            int(row.certificado_id or 0): str(row.descripcion_otro or "")
            for row in rows
            if int(row.certificado_id or 0) > 0
        }
        self._apply_certificados_selection(selected_map)

    def set_apoyo_checked(self, apoyo_id: int, checked: bool):
        updated: list[dict] = []
        for item in self.apoyos_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(apoyo_id):
                current["seleccionado"] = bool(checked)
                if not checked and bool(current.get("permite_descripcion_libre")):
                    current["descripcion_otro"] = ""
            updated.append(current)
        self.apoyos_catalogo = updated
        self.apoyos_seleccionados = [int(item["id"]) for item in updated if bool(item.get("seleccionado"))]

    def set_certificado_checked(self, certificado_id: int, checked: bool):
        updated: list[dict] = []
        for item in self.certificados_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(certificado_id):
                current["seleccionado"] = bool(checked)
                if not checked and bool(current.get("permite_descripcion_libre")):
                    current["descripcion_otro"] = ""
            updated.append(current)
        self.certificados_catalogo = updated
        self.certificados_seleccionados = [
            int(item["id"]) for item in updated if bool(item.get("seleccionado"))
        ]

    def set_apoyo_descripcion_otro(self, apoyo_id: int, value: str):
        updated: list[dict] = []
        for item in self.apoyos_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(apoyo_id) and bool(current.get("permite_descripcion_libre")):
                current["descripcion_otro"] = value
            updated.append(current)
        self.apoyos_catalogo = updated

    def set_certificado_descripcion_otro(self, certificado_id: int, value: str):
        updated: list[dict] = []
        for item in self.certificados_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(certificado_id) and bool(current.get("permite_descripcion_libre")):
                current["descripcion_otro"] = value
            updated.append(current)
        self.certificados_catalogo = updated

    def set_load_codigo_input(self, value: str):
        self.load_codigo_input = value

    def _apply_peligros_selection(self, selected_map: dict[int, str]):
        merged: list[dict] = []
        for item in self.peligros_catalogo:
            peligro_id = int(item.get("id") or 0)
            allows_free_text = bool(item.get("permite_descripcion_libre"))
            descripcion_otro = selected_map.get(peligro_id, "") if allows_free_text else ""
            merged.append(
                {
                    "id": peligro_id,
                    "codigo": str(item.get("codigo") or ""),
                    "numero": item.get("numero"),
                    "nombre": item.get("nombre", ""),
                    "permite_descripcion_libre": allows_free_text,
                    "seleccionado": peligro_id in selected_map,
                    "descripcion_otro": descripcion_otro,
                }
            )
        self.peligros_catalogo = merged

    def _load_peligros_selection_with_session(self, session, ats_id: int):
        if ats_id <= 0:
            self._apply_peligros_selection({})
            return

        rows = session.exec(select(AtsPeligro).where(AtsPeligro.ats_id == ats_id)).all()
        selected_map: dict[int, str] = {
            int(row.peligro_id or 0): (row.descripcion_otro or "") for row in rows
        }
        self._apply_peligros_selection(selected_map)

    def load_peligros_for_current_ats(self):
        if not self.peligros_catalogo:
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self._apply_peligros_selection({})
            return

        try:
            with rx.session() as session:
                self._assert_ats_access(session, ats_id, for_edit=False)
                self._load_peligros_selection_with_session(session, ats_id)
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self._apply_peligros_selection({})

    def set_peligro_checked(self, peligro_id: int, checked: bool):
        updated: list[dict] = []
        for item in self.peligros_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(peligro_id):
                current["seleccionado"] = bool(checked)
                if not checked:
                    current["descripcion_otro"] = ""
            updated.append(current)
        self.peligros_catalogo = updated

    def set_peligro_descripcion_otro(self, peligro_id: int, value: str):
        updated: list[dict] = []
        for item in self.peligros_catalogo:
            current = dict(item)
            current_id = int(current.get("id") or 0)
            if current_id == int(peligro_id) and bool(current.get("permite_descripcion_libre")):
                current["descripcion_otro"] = value
            updated.append(current)
        self.peligros_catalogo = updated

    def _peligro_otro_catalog_row(self) -> dict:
        for item in self.peligros_catalogo:
            if str(item.get("codigo") or "").strip().upper() == self.PELIGRO_OTRO_CODIGO:
                return dict(item)
        return {}

    def _otro_peligro_id(self) -> int:
        row = self._peligro_otro_catalog_row()
        return int(row.get("id") or 0)

    def _is_peligro_otro(self, peligro_id: int) -> bool:
        if peligro_id <= 0:
            return False
        otro_id = self._otro_peligro_id()
        if otro_id > 0 and int(peligro_id) == otro_id:
            return True
        for item in self.peligros_catalogo:
            if int(item.get("id") or 0) != int(peligro_id):
                continue
            return str(item.get("codigo") or "").strip().upper() == self.PELIGRO_OTRO_CODIGO
        return False

    def set_paso3_descripcion_otro_peligro(self, paso_uid: str, peligro_uid: str, value: str):
        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != str(paso_uid):
                updated_steps.append(current_step)
                continue

            next_peligros: list[PasoPeligroItem] = []
            for peligro in current_step.get("peligros", []):
                current_peligro = dict(peligro)
                if (
                    str(current_peligro.get("uid")) == str(peligro_uid)
                    and self._is_peligro_otro(int(current_peligro.get("peligro_id") or 0))
                ):
                    current_peligro["descripcion_otro"] = value
                next_peligros.append(current_peligro)

            current_step["peligros"] = next_peligros
            updated_steps.append(current_step)

        self.pasos_actividad = updated_steps

    def _control_catalog_map(self) -> dict[int, dict]:
        return {
            int(item.get("id") or 0): dict(item)
            for item in self.controles_catalogo
            if int(item.get("id") or 0) > 0
        }

    def _otro_control_id(self) -> int:
        for item in self.controles_catalogo:
            if str(item.get("codigo") or "").strip().upper() == "OTROS":
                return int(item.get("id") or 0)
        return 0

    def _is_control_otro(self, control_id: int) -> bool:
        if control_id <= 0:
            return False
        if control_id == self._otro_control_id():
            return True
        control_row = self._control_catalog_map().get(control_id, {})
        return str(control_row.get("codigo") or "").strip().upper() == "OTROS"

    def _build_empty_paso_peligro_control(self) -> PasoPeligroControlItem:
        return {
            "uid": f"tmp-step-c-{uuid.uuid4().hex[:10]}",
            "id": 0,
            "control_id": 0,
            "control_nombre": "",
            "control_aplicado": "",
        }

    def _build_empty_paso(self, numero_paso: int) -> PasoActividadItem:
        return {
            "uid": f"tmp-step-{uuid.uuid4().hex[:10]}",
            "id": 0,
            "numero_paso": int(numero_paso),
            "descripcion_paso": "",
            "peligros": [],
        }

    def _reindex_pasos(self):
        updated: list[PasoActividadItem] = []
        for idx, paso in enumerate(self.pasos_actividad, start=1):
            current = dict(paso)
            current["numero_paso"] = idx
            updated.append(current)
        self.pasos_actividad = updated

    def add_paso_actividad(self):
        current = [dict(item) for item in self.pasos_actividad]
        current.append(self._build_empty_paso(len(current) + 1))
        self.pasos_actividad = current
        self._reindex_pasos()

    def remove_paso_actividad(self, paso_uid: str):
        self.pasos_actividad = [
            dict(item)
            for item in self.pasos_actividad
            if str(item.get("uid")) != str(paso_uid)
        ]
        self._reindex_pasos()

    def set_paso_descripcion(self, paso_uid: str, value: str):
        updated: list[PasoActividadItem] = []
        for item in self.pasos_actividad:
            current = dict(item)
            if str(current.get("uid")) == str(paso_uid):
                current["descripcion_paso"] = value
            updated.append(current)
        self.pasos_actividad = updated

    def open_paso3_peligro_modal(self, paso_uid: str):
        self.paso3_peligro_modal_step_uid = str(paso_uid or "")
        self.paso3_peligro_search = ""
        self.paso3_peligro_modal_open = True

    def set_paso3_peligro_modal_open(self, value: bool):
        self.paso3_peligro_modal_open = bool(value)
        if not self.paso3_peligro_modal_open:
            self.paso3_peligro_modal_step_uid = ""
            self.paso3_peligro_search = ""

    def close_paso3_peligro_modal(self):
        self.paso3_peligro_modal_open = False
        self.paso3_peligro_modal_step_uid = ""
        self.paso3_peligro_search = ""

    def set_paso3_peligro_search(self, value: str):
        self.paso3_peligro_search = value

    def add_peligro_to_paso(self, peligro_id: int):
        target_step_uid = str(self.paso3_peligro_modal_step_uid or "")
        if not target_step_uid:
            return

        peligro_row = next(
            (
                item
                for item in self.peligros_catalogo
                if int(item.get("id") or 0) == int(peligro_id)
            ),
            None,
        )
        if peligro_row is None:
            return

        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != target_step_uid:
                updated_steps.append(current_step)
                continue

            peligros = [dict(p) for p in current_step.get("peligros", [])]
            exists = any(int(p.get("peligro_id") or 0) == int(peligro_id) for p in peligros)
            if not exists:
                peligros.append(
                    {
                        "uid": f"tmp-step-p-{uuid.uuid4().hex[:10]}",
                        "id": 0,
                        "peligro_id": int(peligro_id),
                        "peligro_numero": int(peligro_row.get("numero") or 0),
                        "peligro_nombre": str(peligro_row.get("nombre") or ""),
                        "descripcion_otro": "",
                        "controls": [self._build_empty_paso_peligro_control()],
                    }
                )
            current_step["peligros"] = peligros
            updated_steps.append(current_step)

        self.pasos_actividad = updated_steps

    def remove_peligro_from_paso(self, paso_uid: str, peligro_uid: str):
        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current = dict(paso)
            if str(current.get("uid")) != str(paso_uid):
                updated_steps.append(current)
                continue

            current["peligros"] = [
                dict(p)
                for p in current.get("peligros", [])
                if str(p.get("uid")) != str(peligro_uid)
            ]
            updated_steps.append(current)
        self.pasos_actividad = updated_steps

    def add_control_to_paso_peligro(self, paso_uid: str, peligro_uid: str):
        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != str(paso_uid):
                updated_steps.append(current_step)
                continue

            next_peligros: list[PasoPeligroItem] = []
            for peligro in current_step.get("peligros", []):
                current_peligro = dict(peligro)
                controls = [dict(control) for control in current_peligro.get("controls", [])]
                if str(current_peligro.get("uid")) == str(peligro_uid):
                    controls.append(self._build_empty_paso_peligro_control())
                current_peligro["controls"] = controls
                next_peligros.append(current_peligro)

            current_step["peligros"] = next_peligros
            updated_steps.append(current_step)
        self.pasos_actividad = updated_steps

    def remove_control_from_paso_peligro(self, paso_uid: str, peligro_uid: str, control_uid: str):
        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != str(paso_uid):
                updated_steps.append(current_step)
                continue

            next_peligros: list[PasoPeligroItem] = []
            for peligro in current_step.get("peligros", []):
                current_peligro = dict(peligro)
                controls = [
                    dict(control)
                    for control in current_peligro.get("controls", [])
                    if str(control.get("uid")) != str(control_uid)
                ]
                if str(current_peligro.get("uid")) == str(peligro_uid):
                    current_peligro["controls"] = controls
                next_peligros.append(current_peligro)

            current_step["peligros"] = next_peligros
            updated_steps.append(current_step)
        self.pasos_actividad = updated_steps

    def set_paso_peligro_control(self, paso_uid: str, peligro_uid: str, control_uid: str, value: str):
        selected_id = int(str(value or "").strip() or 0)
        control_map = self._control_catalog_map()
        updated_steps: list[PasoActividadItem] = []

        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != str(paso_uid):
                updated_steps.append(current_step)
                continue

            next_peligros: list[PasoPeligroItem] = []
            for peligro in current_step.get("peligros", []):
                current_peligro = dict(peligro)
                controls: list[PasoPeligroControlItem] = []
                for control in current_peligro.get("controls", []):
                    current_control = dict(control)
                    if str(current_peligro.get("uid")) == str(peligro_uid) and str(current_control.get("uid")) == str(control_uid):
                        control_row = control_map.get(selected_id, {})
                        control_name = str(control_row.get("nombre") or "") if selected_id > 0 else ""
                        current_control["control_id"] = selected_id
                        current_control["control_nombre"] = control_name

                        if selected_id <= 0:
                            current_control["control_aplicado"] = ""
                        elif self._is_control_otro(selected_id):
                            current_control["control_aplicado"] = str(current_control.get("control_aplicado") or "")
                        else:
                            current_control["control_aplicado"] = control_name
                    controls.append(current_control)

                current_peligro["controls"] = controls
                next_peligros.append(current_peligro)

            current_step["peligros"] = next_peligros
            updated_steps.append(current_step)

        self.pasos_actividad = updated_steps

    def set_paso_peligro_control_aplicado(self, paso_uid: str, peligro_uid: str, control_uid: str, value: str):
        updated_steps: list[PasoActividadItem] = []
        for paso in self.pasos_actividad:
            current_step = dict(paso)
            if str(current_step.get("uid")) != str(paso_uid):
                updated_steps.append(current_step)
                continue

            next_peligros: list[PasoPeligroItem] = []
            for peligro in current_step.get("peligros", []):
                current_peligro = dict(peligro)
                controls: list[PasoPeligroControlItem] = []
                for control in current_peligro.get("controls", []):
                    current_control = dict(control)
                    if str(current_peligro.get("uid")) == str(peligro_uid) and str(current_control.get("uid")) == str(control_uid):
                        current_control["control_aplicado"] = value
                    controls.append(current_control)
                current_peligro["controls"] = controls
                next_peligros.append(current_peligro)

            current_step["peligros"] = next_peligros
            updated_steps.append(current_step)
        self.pasos_actividad = updated_steps

    def _load_pasos_for_current_ats_with_session(self, session, ats_id: int):
        if ats_id <= 0:
            self.pasos_actividad = []
            return

        pasos_rows = session.execute(
            text(
                """
                SELECT p.id, p.numero_paso, p.descripcion_paso
                FROM ats_paso p
                WHERE p.ats_id = :ats_id
                ORDER BY p.numero_paso, p.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        peligro_rows = session.execute(
            text(
                """
                SELECT
                    app.id AS ats_paso_peligro_id,
                    app.ats_paso_id,
                    ap.peligro_id,
                    pc.numero_visual,
                    pc.nombre AS peligro_nombre,
                    app.descripcion_otro AS descripcion_otro,
                    appc.id AS ats_paso_peligro_control_id,
                    appc.control_id,
                    appc.control_aplicado,
                    cc.nombre AS control_nombre
                FROM ats_paso_peligro app
                JOIN ats_peligro ap ON ap.id = app.ats_peligro_id
                JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
                LEFT JOIN ats_paso_peligro_control appc ON appc.ats_paso_peligro_id = app.id
                LEFT JOIN control_catalogo cc ON cc.id = appc.control_id
                JOIN ats_paso p ON p.id = app.ats_paso_id
                WHERE p.ats_id = :ats_id
                ORDER BY p.numero_paso, p.id, app.id, appc.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        by_step_id: dict[int, list[PasoPeligroItem]] = {}
        peligros_index: dict[tuple[int, int], PasoPeligroItem] = {}
        for row in peligro_rows:
            step_id = int(row["ats_paso_id"] or 0)
            if step_id <= 0:
                continue
            rel_id = int(row.get("ats_paso_peligro_id") or 0)
            if rel_id <= 0:
                continue

            key = (step_id, rel_id)
            if key not in peligros_index:
                peligro_item: PasoPeligroItem = {
                    "uid": f"db-step-p-{rel_id}",
                    "id": rel_id,
                    "peligro_id": int(row.get("peligro_id") or 0),
                    "peligro_numero": int(row.get("numero_visual") or 0),
                    "peligro_nombre": str(row.get("peligro_nombre") or ""),
                    "descripcion_otro": str(row.get("descripcion_otro") or ""),
                    "controls": [],
                }
                peligros_index[key] = peligro_item
                by_step_id.setdefault(step_id, []).append(peligro_item)

            control_id = int(row.get("control_id") or 0)
            control_aplicado = str(row.get("control_aplicado") or "").strip()
            if control_id > 0 or control_aplicado:
                control_row_id = int(row.get("ats_paso_peligro_control_id") or 0)
                peligros_index[key]["controls"].append(
                    {
                        "uid": f"db-step-c-{control_row_id}" if control_row_id > 0 else f"tmp-step-c-{uuid.uuid4().hex[:10]}",
                        "id": control_row_id,
                        "control_id": control_id,
                        "control_nombre": str(row.get("control_nombre") or ""),
                        "control_aplicado": control_aplicado,
                    }
                )

        loaded_steps: list[PasoActividadItem] = []
        for row in pasos_rows:
            step_id = int(row["id"] or 0)
            loaded_peligros: list[PasoPeligroItem] = [dict(rel) for rel in by_step_id.get(step_id, [])]

            loaded_steps.append(
                {
                    "uid": f"db-step-{step_id}",
                    "id": step_id,
                    "numero_paso": int(row["numero_paso"] or 0),
                    "descripcion_paso": str(row["descripcion_paso"] or ""),
                    "peligros": loaded_peligros,
                }
            )

        self.pasos_actividad = loaded_steps
        self._reindex_pasos()

    def load_pasos_for_current_ats(self):
        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.pasos_actividad = []
            return

        try:
            with rx.session() as session:
                self._assert_ats_access(session, ats_id, for_edit=False)
                self._load_pasos_for_current_ats_with_session(session, ats_id)
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self.pasos_actividad = []

    def _build_trabajador_from_catalog_row(self, row: dict, numero_orden: int) -> TrabajadorActividadItem:
        return {
            "uid": f"tmp-t-{uuid.uuid4().hex[:10]}",
            "id": 0,
            "numero_orden": int(numero_orden),
            "trabajador_id": int(row.get("id") or 0),
            "nombre_trabajador": str(row.get("nombre_completo") or ""),
            "numero_documento": str(row.get("numero_documento") or ""),
            "cargo_trabajador": str(row.get("cargo") or ""),
            "firma_base64": "",
        }

    def _reindex_trabajadores(self):
        reindexed: list[TrabajadorActividadItem] = []
        for idx, trabajador in enumerate(self.trabajadores_actividad, start=1):
            current = dict(trabajador)
            current["numero_orden"] = idx
            reindexed.append(current)
        self.trabajadores_actividad = reindexed

    def _load_trabajadores_for_current_ats_with_session(self, session, ats_id: int):
        if ats_id <= 0:
            self.trabajadores_actividad = []
            return

        rows = session.exec(
            select(AtsTrabajador)
            .where(AtsTrabajador.ats_id == ats_id)
            .order_by(AtsTrabajador.numero_orden, AtsTrabajador.id)
        ).all()

        loaded_rows: list[TrabajadorActividadItem] = []
        for row in rows:
            nombre = str(row.nombre_snapshot or row.nombre_trabajador or "")
            documento = str(row.documento_snapshot or row.numero_documento or "")
            cargo = str(row.cargo_snapshot or row.cargo_trabajador or "")
            trabajador_id = int(row.trabajador_id or 0)
            if trabajador_id <= 0 and documento:
                matched = session.exec(
                    select(Trabajador).where(Trabajador.numero_documento == documento)
                ).first()
                trabajador_id = int(matched.id or 0) if matched else 0
            loaded_rows.append(
                {
                    "uid": f"db-t-{int(row.id or 0)}",
                    "id": int(row.id or 0),
                    "numero_orden": int(row.numero_orden or 0),
                    "trabajador_id": trabajador_id,
                    "nombre_trabajador": nombre,
                    "numero_documento": documento,
                    "cargo_trabajador": cargo,
                    "firma_base64": str(row.firma_base64 or ""),
                }
            )
        self.trabajadores_actividad = loaded_rows
        self._reindex_trabajadores()

    def load_trabajadores_for_current_ats(self):
        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.trabajadores_actividad = []
            return

        try:
            with rx.session() as session:
                self._assert_ats_access(session, ats_id, for_edit=False)
                self._load_trabajadores_for_current_ats_with_session(session, ats_id)
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self.trabajadores_actividad = []

    def open_trabajador_import_modal(self):
        self.trabajador_import_modal_open = True
        self.trabajador_import_search = ""
        self.trabajador_import_selected_ids = []

    def set_trabajador_import_modal_open(self, value: bool):
        self.trabajador_import_modal_open = bool(value)
        if not self.trabajador_import_modal_open:
            self.trabajador_import_search = ""
            self.trabajador_import_selected_ids = []

    def close_trabajador_import_modal(self):
        self.trabajador_import_modal_open = False
        self.trabajador_import_search = ""
        self.trabajador_import_selected_ids = []

    def set_trabajador_import_search(self, value: str):
        self.trabajador_import_search = value

    def toggle_trabajador_import_selection(self, trabajador_id: int, checked: bool):
        current = {int(value) for value in self.trabajador_import_selected_ids}
        if checked:
            current.add(int(trabajador_id))
        else:
            current.discard(int(trabajador_id))
        self.trabajador_import_selected_ids = sorted([value for value in current if value > 0])

    def import_trabajadores_seleccionados(self):
        selected_ids = {int(value) for value in self.trabajador_import_selected_ids if int(value) > 0}
        if not selected_ids:
            self.close_trabajador_import_modal()
            return

        imported_ids = {
            int(item.get("trabajador_id") or 0)
            for item in self.trabajadores_actividad
            if int(item.get("trabajador_id") or 0) > 0
        }
        to_add: list[dict] = []
        for row in self.trabajadores_catalogo:
            trabajador_id = int(row.get("id") or 0)
            if trabajador_id in selected_ids and trabajador_id not in imported_ids:
                to_add.append(dict(row))

        current = [dict(item) for item in self.trabajadores_actividad]
        for row in to_add:
            current.append(self._build_trabajador_from_catalog_row(row, len(current) + 1))

        self.trabajadores_actividad = current
        self._reindex_trabajadores()
        self.close_trabajador_import_modal()

    def remove_trabajador_actividad(self, trabajador_uid: str):
        self.trabajadores_actividad = [
            dict(item)
            for item in self.trabajadores_actividad
            if str(item.get("uid")) != str(trabajador_uid)
        ]
        self._reindex_trabajadores()

    def set_trabajador_firma(self, trabajador_uid: str, value: str):
        updated: list[TrabajadorActividadItem] = []
        for item in self.trabajadores_actividad:
            current = dict(item)
            if str(current.get("uid")) == str(trabajador_uid):
                current["firma_base64"] = value
            updated.append(current)
        self.trabajadores_actividad = updated

    def set_trabajadores_firmas_from_json(self, value: str):
        raw = (value or "").strip()
        if not raw:
            return

        try:
            parsed = json.loads(raw)
        except Exception:
            return

        if not isinstance(parsed, list):
            return

        firmas_by_uid: dict[str, str] = {}
        for row in parsed:
            if not isinstance(row, dict):
                continue
            uid = str(row.get("uid") or "").strip()
            firma = str(row.get("firma_base64") or "")
            if uid:
                firmas_by_uid[uid] = firma

        if not firmas_by_uid:
            return

        updated: list[TrabajadorActividadItem] = []
        for item in self.trabajadores_actividad:
            current = dict(item)
            uid = str(current.get("uid") or "")
            if uid in firmas_by_uid:
                current["firma_base64"] = firmas_by_uid[uid]
            updated.append(current)
        self.trabajadores_actividad = updated

    async def save_trabajadores_actividad_with_signatures(self, firmas_json: str):
        self.set_trabajadores_firmas_from_json(firmas_json)
        await self.save_trabajadores_actividad()

    async def save_trabajadores_actividad_with_signatures_y_continuar(self, firmas_json: str):
        self.set_trabajadores_firmas_from_json(firmas_json)
        await self.save_trabajadores_actividad_y_continuar()

    def _load_firma_tipos_catalogo_with_session(self, session):
        rows = session.exec(
            select(FirmaTipoCatalogo)
            .where(FirmaTipoCatalogo.activo.is_(True))
            .order_by(FirmaTipoCatalogo.orden, FirmaTipoCatalogo.id)
        ).all()
        self.firma_tipos_catalogo = [
            {
                "id": int(row.id or 0),
                "codigo": str(row.codigo or ""),
                "nombre": str(row.nombre or ""),
                "orden": int(row.orden or 0),
            }
            for row in rows
        ]

    def _build_firma_final_item(self, firma_tipo: dict, saved_map: dict[int, dict] | None = None) -> FirmaFinalItem:
        saved_map = saved_map or {}
        firma_tipo_id = int(firma_tipo.get("id") or 0)
        saved = saved_map.get(firma_tipo_id, {})
        return {
            "uid": f"ff-{firma_tipo_id}",
            "id": int(saved.get("id") or 0),
            "firma_tipo_id": firma_tipo_id,
            "firma_tipo_codigo": str(firma_tipo.get("codigo") or ""),
            "firma_tipo_nombre": str(firma_tipo.get("nombre") or ""),
            "nombre_completo": str(saved.get("nombre_completo") or ""),
            "cargo": str(saved.get("cargo") or ""),
            "firma_base64": str(saved.get("firma_base64") or ""),
        }

    def _rebuild_firmas_finales(self, saved_map: dict[int, dict] | None = None):
        self.firmas_finales = [
            self._build_firma_final_item(firma_tipo, saved_map)
            for firma_tipo in self.firma_tipos_catalogo
            if int(firma_tipo.get("id") or 0) > 0
        ]

    def _load_firmas_finales_for_current_ats_with_session(self, session, ats_id: int):
        if not self.firma_tipos_catalogo:
            self._load_firma_tipos_catalogo_with_session(session)

        if ats_id <= 0:
            self._rebuild_firmas_finales({})
            return

        rows = session.exec(
            select(AtsFirmaFinal)
            .where(AtsFirmaFinal.ats_id == ats_id)
            .order_by(AtsFirmaFinal.firma_tipo_id, AtsFirmaFinal.id)
        ).all()

        saved_map: dict[int, dict] = {}
        for row in rows:
            firma_tipo_id = int(row.firma_tipo_id or 0)
            if firma_tipo_id <= 0 or firma_tipo_id in saved_map:
                continue
            saved_map[firma_tipo_id] = {
                "id": int(row.id or 0),
                "nombre_completo": str(row.nombre_completo or ""),
                "cargo": str(row.cargo or ""),
                "firma_base64": str(row.firma_base64 or ""),
            }

        self._rebuild_firmas_finales(saved_map)

    def load_firmas_finales_for_current_ats(self):
        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            with rx.session() as session:
                self._load_firma_tipos_catalogo_with_session(session)
            self._rebuild_firmas_finales({})
            return

        try:
            with rx.session() as session:
                self._assert_ats_access(session, ats_id, for_edit=False)
                self._load_firmas_finales_for_current_ats_with_session(session, ats_id)
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self._rebuild_firmas_finales({})

    def set_firma_final_nombre(self, firma_uid: str, value: str):
        updated: list[FirmaFinalItem] = []
        for item in self.firmas_finales:
            current = dict(item)
            if str(current.get("uid")) == str(firma_uid):
                current["nombre_completo"] = value
            updated.append(current)
        self.firmas_finales = updated

    def set_firma_final_cargo(self, firma_uid: str, value: str):
        updated: list[FirmaFinalItem] = []
        for item in self.firmas_finales:
            current = dict(item)
            if str(current.get("uid")) == str(firma_uid):
                current["cargo"] = value
            updated.append(current)
        self.firmas_finales = updated

    def set_firmas_finales_from_json(self, value: str):
        raw = (value or "").strip()
        if not raw:
            return

        try:
            parsed = json.loads(raw)
        except Exception:
            return

        if not isinstance(parsed, list):
            return

        firmas_by_uid: dict[str, str] = {}
        for row in parsed:
            if not isinstance(row, dict):
                continue
            uid = str(row.get("uid") or "").strip()
            firma = str(row.get("firma_base64") or "")
            if uid:
                firmas_by_uid[uid] = firma

        if not firmas_by_uid:
            return

        updated: list[FirmaFinalItem] = []
        for item in self.firmas_finales:
            current = dict(item)
            uid = str(current.get("uid") or "")
            if uid in firmas_by_uid:
                current["firma_base64"] = firmas_by_uid[uid]
            updated.append(current)
        self.firmas_finales = updated

    async def save_firmas_finales_with_signatures(self, firmas_json: str):
        self.set_firmas_finales_from_json(firmas_json)
        await self.save_firmas_finales()

    async def save_firmas_finales_with_signatures_y_continuar(self, firmas_json: str):
        self.set_firmas_finales_from_json(firmas_json)
        await self.save_firmas_finales_y_continuar()

    def _asset_url_from_path(self, file_path: str) -> str:
        normalized = str(file_path or "").replace("\\", "/").strip()
        if normalized.startswith("assets/"):
            return "/" + normalized[len("assets/"):]
        if normalized.startswith("/"):
            return normalized
        return "/" + normalized

    @staticmethod
    def _safe_document_code(value: str, fallback: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(value or "")).strip("_")
        return safe if safe else fallback

    @staticmethod
    def _is_postgres_session(session) -> bool:
        try:
            bind = session.get_bind()
            dialect_name = str(getattr(getattr(bind, "dialect", None), "name", "")).lower()
            return "postgres" in dialect_name
        except Exception:
            return False

    def _lock_ats_row_for_document_generation(self, session, ats_id: int):
        if not self._is_postgres_session(session):
            return
        session.execute(
            text("SELECT id FROM ats WHERE id = :ats_id FOR UPDATE"),
            {"ats_id": int(ats_id)},
        ).first()

    @staticmethod
    def _next_document_version_with_session(session, ats_id: int) -> int:
        max_version = session.execute(
            text(
                """
                SELECT COALESCE(MAX(version), 0) AS max_version
                FROM ats_documento
                WHERE ats_id = :ats_id AND tipo_documento = 'PDF'
                """
            ),
            {"ats_id": int(ats_id)},
        ).scalar_one()
        return int(max_version or 0) + 1

    def _build_storage_target_for_document(self, ats_id: int, codigo_publico: str, version: int) -> tuple[str, str]:
        safe_code = self._safe_document_code(codigo_publico, fallback=f"ATS_{int(ats_id)}")
        file_name = f"{safe_code}_v{int(version)}.pdf"
        storage_path = f"{safe_code}/v{int(version)}/{file_name}"
        return file_name, storage_path

    def _is_legacy_local_document_path(self, file_path: str) -> bool:
        normalized = str(file_path or "").replace("\\", "/").strip()
        return normalized.startswith("assets/") or normalized.startswith("documentos/") or normalized.startswith("/documentos/")

    @staticmethod
    def _resolve_document_codigo_label(numero_ats: str, codigo_publico: str, ats_id: int) -> str:
        numero_clean = str(numero_ats or "").strip()
        codigo_clean = str(codigo_publico or "").strip()
        if numero_clean and codigo_clean and numero_clean.lower() != codigo_clean.lower():
            return f"{numero_clean} ({codigo_clean})"
        if numero_clean:
            return numero_clean
        if codigo_clean:
            return codigo_clean
        return f"ATS-{int(ats_id)}"

    def _resolve_document_file_url(self, storage_path: str, file_name: str) -> tuple[str, str]:
        normalized = str(storage_path or "").replace("\\", "/").strip()
        if normalized == "":
            return "", ""
        if self._is_legacy_local_document_path(normalized):
            return self._asset_url_from_path(normalized), ""
        try:
            return (
                create_signed_file_url(
                    storage_path=normalized,
                    expires_in_seconds=get_supabase_signed_url_ttl_seconds(),
                    download_name=str(file_name or "").strip() or None,
                ),
                "",
            )
        except Exception as exc:
            return "", f"No se pudo generar URL firmada para el historial de documentos: {exc}"

    def _load_documentos_ats_options_with_session(self, session, search_query: str = ""):
        user_id, role_code = self._require_ats_role_context()
        scope_condition, scope_params = self._ats_scope_condition_sql(
            alias="a",
            current_user_id=user_id,
            role_code=role_code,
        )
        query_value = str(search_query or "").strip().lower()
        where_clauses: list[str] = [scope_condition]
        params: dict[str, int | str] = dict(scope_params)
        if len(query_value) >= 2:
            params["search_term"] = f"%{query_value}%"
            where_clauses.append(
                """
                (
                    lower(CAST(a.fecha_elaboracion AS TEXT)) LIKE :search_term
                    OR lower(COALESCE(a.numero_ats, '')) LIKE :search_term
                    OR lower(COALESCE(a.codigo_publico, '')) LIKE :search_term
                    OR lower(COALESCE(a.empresa_persona_ejecuta, '')) LIKE :search_term
                )
                """
            )

        where_sql = " AND ".join(where_clauses)
        rows = session.execute(
            text(
                f"""
                SELECT a.id, a.codigo_publico, a.numero_ats, a.empresa_persona_ejecuta, a.fecha_elaboracion
                FROM ats a
                WHERE {where_sql}
                ORDER BY a.id DESC
                LIMIT 300
                """
            ),
            params,
        ).mappings().all()

        self.documentos_ats_options = [
            {
                "id": int(row["id"]),
                "id_str": str(int(row["id"])),
                "codigo_publico": str(row["codigo_publico"] or ""),
                "numero_ats": str(row["numero_ats"] or ""),
                "label": (
                    f"{self._resolve_document_codigo_label(str(row['numero_ats'] or ''), str(row['codigo_publico'] or ''), int(row['id']))} "
                    f"| {row['fecha_elaboracion']} | {str(row['empresa_persona_ejecuta'] or '')}"
                ),
            }
            for row in rows
        ]

        available_ids = {int(item["id"]) for item in self.documentos_ats_options}
        if int(self.documento_selected_ats_id or 0) not in available_ids:
            self.documento_selected_ats_id = int(self.documentos_ats_options[0]["id"]) if self.documentos_ats_options else 0

        selected = next(
            (
                item
                for item in self.documentos_ats_options
                if int(item["id"]) == int(self.documento_selected_ats_id or 0)
            ),
            None,
        )
        self.documento_selected_codigo = str(selected["codigo_publico"]) if selected else ""

    def _load_documentos_generados_with_session(self, session, ats_id: int = 0):
        user_id, role_code = self._require_ats_role_context()
        scope_condition, scope_params = self._ats_scope_condition_sql(
            alias="a",
            current_user_id=user_id,
            role_code=role_code,
        )
        params: dict[str, int] = dict(scope_params)
        where_clause = f"WHERE {scope_condition}"
        if ats_id > 0:
            where_clause += " AND d.ats_id = :ats_id"
            params["ats_id"] = int(ats_id)

        rows = session.execute(
            text(
                f"""
                SELECT
                    d.id,
                    d.ats_id,
                    a.codigo_publico,
                    d.tipo_documento,
                    d.nombre_archivo,
                    d.ruta_archivo,
                    d.mime_type,
                    d.version,
                    d.created_at
                FROM ats_documento d
                JOIN ats a ON a.id = d.ats_id
                {where_clause}
                ORDER BY d.id DESC
                LIMIT 100
                """
            ),
            params,
        ).mappings().all()

        resolved_rows: list[dict] = []
        first_signed_url_error = ""
        for row in rows:
            file_name = str(row["nombre_archivo"] or "")
            file_path = str(row["ruta_archivo"] or "")
            file_url, url_error = self._resolve_document_file_url(file_path, file_name)
            if url_error and first_signed_url_error == "":
                first_signed_url_error = url_error

            resolved_rows.append(
                {
                    "id": int(row["id"]),
                    "ats_id": int(row["ats_id"]),
                    "codigo_publico": str(row["codigo_publico"] or ""),
                    "tipo_documento": str(row["tipo_documento"] or ""),
                    "nombre_archivo": file_name,
                    "ruta_archivo": file_path,
                    "archivo_url": file_url,
                    "mime_type": str(row["mime_type"] or ""),
                    "version": int(row["version"] or 1),
                    "version_str": str(int(row["version"] or 1)),
                    "created_at": str(row["created_at"] or ""),
                }
            )

        self.documentos_generados = resolved_rows
        if first_signed_url_error and self.documento_error == "":
            self.documento_error = first_signed_url_error

    async def set_documento_search_query(self, value: str):
        self.documento_error = ""
        self.documento_search_query = str(value or "")

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.documento_error = str(exc)
            self.documentos_ats_options = []
            self.documentos_generados = []
            self.documento_selected_ats_id = 0
            self.documento_selected_codigo = ""
            return

        with rx.session() as session:
            self._load_documentos_ats_options_with_session(session, self.documento_search_query)
            self._load_documentos_generados_with_session(session, int(self.documento_selected_ats_id or 0))

    async def set_documento_selected_ats_id_from_select(self, value: str):
        clean = (value or "").strip()
        target_id = int(clean) if clean else 0

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.documento_error = str(exc)
            self.documento_selected_ats_id = 0
            self.documento_selected_codigo = ""
            self.documentos_generados = []
            return

        with rx.session() as session:
            if target_id > 0:
                try:
                    assert_can_access_ats(session, target_id, user_id, role_code)
                except AccessDeniedError as exc:
                    self.documento_error = str(exc)
                    self.documento_selected_ats_id = 0
                    self.documento_selected_codigo = ""
                    self.documentos_generados = []
                    return

            self.documento_error = ""
            self.documento_selected_ats_id = target_id
            selected = next(
                (
                    item
                    for item in self.documentos_ats_options
                    if int(item["id"]) == int(self.documento_selected_ats_id or 0)
                ),
                None,
            )
            if selected:
                self.documento_selected_codigo = str(selected["codigo_publico"] or "")
            elif target_id > 0:
                codigo = session.execute(
                    text(
                        """
                        SELECT codigo_publico
                        FROM ats
                        WHERE id = :ats_id
                        """
                    ),
                    {"ats_id": int(target_id)},
                ).scalar_one_or_none()
                self.documento_selected_codigo = str(codigo or "")
            else:
                self.documento_selected_codigo = ""

            self._load_documentos_generados_with_session(session, int(self.documento_selected_ats_id or 0))

    def _build_document_context_with_session(self, session, ats_id: int) -> dict:
        self._assert_ats_access(session, ats_id, for_edit=False)

        ats_row = session.execute(
            text(
                """
                SELECT
                    a.id,
                    a.codigo_publico,
                    a.empresa_persona_ejecuta,
                    a.fecha_elaboracion,
                    a.ciudad,
                    a.area_lugar,
                    a.numero_ats,
                    a.duracion_actividad,
                    a.actividad_alto_riesgo,
                    a.descripcion_actividad,
                    a.observaciones,
                    t.nombre AS tipo_ats,
                    t.codigo AS tipo_ats_codigo
                FROM ats a
                LEFT JOIN ats_tipo t ON t.id = a.tipo_ats_id
                WHERE a.id = :ats_id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().first()

        if ats_row is None:
            return {}

        apoyos = session.execute(
            text(
                """
                SELECT ac.codigo, ac.nombre, aa.descripcion_otro
                FROM ats_apoyo aa
                JOIN apoyo_catalogo ac ON ac.id = aa.apoyo_id
                WHERE aa.ats_id = :ats_id
                ORDER BY ac.orden, ac.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        certificados = session.execute(
            text(
                """
                SELECT cc.codigo, cc.nombre, ac.descripcion_otro
                FROM ats_certificado ac
                JOIN certificado_catalogo cc ON cc.id = ac.certificado_id
                WHERE ac.ats_id = :ats_id
                ORDER BY cc.orden, cc.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        peligros = session.execute(
            text(
                """
                SELECT pc.numero_visual, pc.nombre, ap.descripcion_otro
                FROM ats_peligro ap
                JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
                WHERE ap.ats_id = :ats_id
                ORDER BY pc.orden, pc.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        pasos_rows = session.execute(
            text(
                """
                SELECT
                    p.numero_paso,
                    p.descripcion_paso,
                    app.id AS ats_paso_peligro_id,
                    pc.numero_visual AS peligro_numero,
                    pc.nombre AS peligro_nombre,
                    app.descripcion_otro AS peligro_descripcion_otro,
                    appc.control_aplicado
                FROM ats_paso p
                LEFT JOIN ats_paso_peligro app ON app.ats_paso_id = p.id
                LEFT JOIN ats_peligro ap ON ap.id = app.ats_peligro_id
                LEFT JOIN peligro_catalogo pc ON pc.id = ap.peligro_id
                LEFT JOIN ats_paso_peligro_control appc ON appc.ats_paso_peligro_id = app.id
                WHERE p.ats_id = :ats_id
                ORDER BY p.numero_paso, p.id, pc.numero_visual, app.id, appc.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        trabajadores = session.execute(
            text(
                """
                SELECT
                    COALESCE(NULLIF(TRIM(nombre_snapshot), ''), nombre_trabajador) AS nombre_trabajador,
                    COALESCE(NULLIF(TRIM(documento_snapshot), ''), numero_documento) AS numero_documento,
                    COALESCE(NULLIF(TRIM(cargo_snapshot), ''), cargo_trabajador) AS cargo_trabajador,
                    firma_base64
                FROM ats_trabajador
                WHERE ats_id = :ats_id
                ORDER BY numero_orden, id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        pasos_map: dict[int, dict] = {}
        for row in pasos_rows:
            numero = int(row["numero_paso"] or 0)
            if numero <= 0:
                continue
            paso = pasos_map.setdefault(
                numero,
                {
                    "numero_paso": numero,
                    "descripcion_paso": str(row["descripcion_paso"] or ""),
                    "peligros": [],
                    "_peligros_map": {},
                },
            )

            peligro_numero = row.get("peligro_numero")
            peligro_nombre = str(row.get("peligro_nombre") or "")
            if peligro_numero is not None and peligro_nombre:
                peligro_key = (int(peligro_numero), peligro_nombre)
                if peligro_key not in paso["_peligros_map"]:
                    peligro_item = {
                        "peligro_numero": int(peligro_numero),
                        "peligro_nombre": peligro_nombre,
                        "descripcion_otro": str(row.get("peligro_descripcion_otro") or "").strip(),
                        "controles": [],
                    }
                    paso["_peligros_map"][peligro_key] = peligro_item
                    paso["peligros"].append(peligro_item)

            control_aplicado = str(row.get("control_aplicado") or "").strip()
            if control_aplicado and peligro_numero is not None and peligro_nombre:
                peligro_key = (int(peligro_numero), peligro_nombre)
                peligro_item = paso["_peligros_map"].get(peligro_key)
                if peligro_item is not None and control_aplicado not in peligro_item["controles"]:
                    peligro_item["controles"].append(control_aplicado)

        pasos: list[dict] = []
        for numero in sorted(pasos_map.keys()):
            paso = pasos_map[numero]
            peligros_asociados = " | ".join(
                list(
                    dict.fromkeys(
                        [
                            (
                                f"P{int(item.get('peligro_numero') or 0)} - {str(item.get('peligro_nombre') or '')}"
                                + (
                                    f" (Detalle: {str(item.get('descripcion_otro') or '').strip()})"
                                    if str(item.get("descripcion_otro") or "").strip() != ""
                                    else ""
                                )
                            )
                            for item in paso["peligros"]
                            if int(item.get("peligro_numero") or 0) > 0 and str(item.get("peligro_nombre") or "").strip() != ""
                        ]
                    )
                )
            )
            controles_asociados = " | ".join(
                list(
                    dict.fromkeys(
                        [
                            str(control or "").strip()
                            for item in paso["peligros"]
                            for control in item.get("controles", [])
                            if str(control or "").strip() != ""
                        ]
                    )
                )
            )
            pasos.append(
                {
                    "numero_paso": numero,
                    "descripcion_paso": str(paso["descripcion_paso"] or ""),
                    "peligros": [
                        {
                            "peligro_numero": int(item.get("peligro_numero") or 0),
                            "peligro_nombre": str(item.get("peligro_nombre") or ""),
                            "descripcion_otro": str(item.get("descripcion_otro") or ""),
                            "controles": [str(control or "") for control in item.get("controles", [])],
                        }
                        for item in paso["peligros"]
                    ],
                    "peligros_asociados": peligros_asociados,
                    "controles_aplicados": controles_asociados,
                }
            )

        firmas_finales = session.execute(
            text(
                """
                SELECT
                    ft.codigo AS firma_tipo_codigo,
                    ft.nombre AS firma_tipo_nombre,
                    aff.nombre_completo,
                    aff.cargo,
                    aff.firma_base64
                FROM firma_tipo_catalogo ft
                LEFT JOIN ats_firma_final aff
                    ON aff.firma_tipo_id = ft.id AND aff.ats_id = :ats_id
                WHERE ft.activo IS TRUE
                ORDER BY ft.orden, ft.id
                """
            ),
            {"ats_id": ats_id},
        ).mappings().all()

        return {
            "ats": {
                "id": int(ats_row["id"]),
                "codigo_publico": str(ats_row["codigo_publico"] or ""),
                "empresa_persona_ejecuta": str(ats_row["empresa_persona_ejecuta"] or ""),
                "fecha_elaboracion": str(ats_row["fecha_elaboracion"] or ""),
                "ciudad": str(ats_row["ciudad"] or ""),
                "area_lugar": str(ats_row["area_lugar"] or ""),
                "numero_ats": str(ats_row["numero_ats"] or ""),
                "tipo_ats": str(ats_row["tipo_ats"] or ""),
                "tipo_ats_codigo": str(ats_row["tipo_ats_codigo"] or ""),
                "duracion_actividad": str(ats_row["duracion_actividad"] or ""),
                "actividad_alto_riesgo": "SI" if bool(ats_row["actividad_alto_riesgo"]) else "NO",
                "descripcion_actividad": str(ats_row["descripcion_actividad"] or ""),
            },
            "apoyos": [dict(row) for row in apoyos],
            "certificados": [dict(row) for row in certificados],
            "peligros": [dict(row) for row in peligros],
            "pasos": pasos,
            "trabajadores": [dict(row) for row in trabajadores],
            "observaciones": str(ats_row["observaciones"] or ""),
            "firmas_finales": [dict(row) for row in firmas_finales],
        }

    def _validate_document_context(self, context: dict) -> list[str]:
        if not context:
            return ["No existe informacion del ATS seleccionado."]

        errors: list[str] = []
        ats = context.get("ats", {})
        required_fields = [
            ("codigo_publico", "codigo ATS"),
            ("empresa_persona_ejecuta", "empresa/persona ejecuta"),
            ("fecha_elaboracion", "fecha elaboracion"),
            ("ciudad", "ciudad"),
            ("area_lugar", "area/lugar"),
            ("descripcion_actividad", "descripcion de actividad"),
        ]
        for key, label in required_fields:
            if str(ats.get(key) or "").strip() == "":
                errors.append(f"Falta {label}.")

        if len(context.get("peligros", [])) <= 0:
            errors.append("Debe existir al menos un peligro guardado.")
        if len(context.get("pasos", [])) <= 0:
            errors.append("Debe existir al menos un paso registrado.")
        if len(context.get("trabajadores", [])) <= 0:
            errors.append("Debe existir al menos un trabajador registrado.")

        required_signature_codes = {"AUTORIZA", "SUPERVISA", "EJECUTA"}
        captured_codes = {
            str(item.get("firma_tipo_codigo") or "").upper()
            for item in context.get("firmas_finales", [])
            if str(item.get("nombre_completo") or "").strip() and str(item.get("firma_base64") or "").strip()
        }
        missing_signature_codes = sorted(required_signature_codes - captured_codes)
        if missing_signature_codes:
            errors.append("Faltan firmas finales completas para: " + ", ".join(missing_signature_codes))

        return errors

    async def load_documentos_page_data(self):
        self.documento_error = ""
        self.documento_success = ""
        self.documento_search_query = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.documento_error = str(exc)
            self.documentos_ats_options = []
            self.documentos_generados = []
            self.ats_recientes = []
            return

        with rx.session() as session:
            scope_condition, scope_params = self._ats_scope_condition_sql(
                alias="a",
                current_user_id=user_id,
                role_code=role_code,
            )
            rows = session.execute(
                text(
                    f"""
                    SELECT a.id, a.codigo_publico, e.nombre AS estado, a.empresa_persona_ejecuta, a.fecha_elaboracion
                    FROM ats a
                    JOIN ats_estado e ON e.id = a.estado_id
                    WHERE {scope_condition}
                    ORDER BY a.id DESC
                    LIMIT 50
                    """
                ),
                scope_params,
            ).mappings().all()
            self.ats_recientes = [dict(row) for row in rows]
            self._load_documentos_ats_options_with_session(session, self.documento_search_query)
            self._load_documentos_generados_with_session(session, int(self.documento_selected_ats_id or 0))

    async def generar_documento_pdf(self):
        self.documento_error = ""
        self.documento_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.documento_error = str(exc)
            return

        ats_id = int(self.documento_selected_ats_id or 0)
        if ats_id <= 0:
            self.documento_error = "Selecciona un ATS para generar el PDF."
            return

        template_path = Path.cwd() / "assets" / "templates" / "ats_template.docx"
        if not template_path.exists():
            self.documento_error = (
                "No existe la plantilla Word requerida en assets/templates/ats_template.docx."
            )
            return

        try:
            pdf_engine = get_ats_pdf_engine()
        except RuntimeError as exc:
            self.documento_error = str(exc)
            return

        with rx.session() as session:
            try:
                assert_can_access_ats(session, ats_id, user_id, role_code)
                context = self._build_document_context_with_session(session, ats_id)
            except AccessDeniedError as exc:
                self.documento_error = str(exc)
                return

            validation_errors = self._validate_document_context(context)
            if validation_errors:
                self.documento_error = "No se puede generar el PDF: " + " ".join(validation_errors)
                return

            try:
                pdf_bytes = generate_pdf_bytes_from_template(
                    context=context,
                    template_path=template_path,
                    engine=pdf_engine,
                )
            except Exception as exc:
                self.documento_error = (
                    "Error al generar el PDF desde plantilla DOCX: "
                    f"{exc}"
                )
                return

            uploaded_storage_path = ""
            try:
                self._lock_ats_row_for_document_generation(session, ats_id)
                next_version = self._next_document_version_with_session(session, ats_id)
            except Exception as exc:
                session.rollback()
                self.documento_error = f"Error calculando version del documento: {exc}"
                return

            code = str(context.get("ats", {}).get("codigo_publico") or f"ATS_{ats_id}")
            file_name, storage_path = self._build_storage_target_for_document(
                ats_id=ats_id,
                codigo_publico=code,
                version=next_version,
            )

            try:
                upload_pdf_bytes(storage_path=storage_path, pdf_bytes=pdf_bytes)
                uploaded_storage_path = storage_path
            except Exception as exc:
                session.rollback()
                self.documento_error = f"Error subiendo PDF a Storage: {exc}"
                return

            row = AtsDocumento(
                ats_id=ats_id,
                tipo_documento="PDF",
                nombre_archivo=file_name,
                ruta_archivo=storage_path,
                mime_type="application/pdf",
                version=next_version,
                generado_por_usuario_id=int(user_id or 0) or None,
                created_at=datetime.utcnow(),
            )
            session.add(row)
            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_DOCUMENTO_GENERADO,
                    user_id=user_id,
                    role_code=role_code,
                )
                session.commit()
            except (AccessDeniedError, RuntimeError) as exc:
                self.documento_error = str(exc)
                session.rollback()
                if uploaded_storage_path:
                    delete_file_if_exists(uploaded_storage_path)
                return
            except Exception as exc:
                self.documento_error = f"Error guardando registro de documento ATS: {exc}"
                session.rollback()
                if uploaded_storage_path:
                    delete_file_if_exists(uploaded_storage_path)
                return

            self.documento_generado_nombre = file_name
            self.documento_generado_url = ""
            try:
                self.documento_generado_url = create_signed_file_url(
                    storage_path=storage_path,
                    expires_in_seconds=get_supabase_signed_url_ttl_seconds(),
                    download_name=file_name,
                )
            except Exception as exc:
                self.documento_error = f"Documento generado, pero fallo la URL firmada: {exc}"

            self.documento_success = (
                f"Documento generado correctamente (v{next_version}, motor {pdf_engine}): {file_name}"
            )
            self._load_documentos_generados_with_session(session, ats_id)
            return rx.download(
                data=pdf_bytes,
                filename=file_name,
                mime_type="application/pdf",
            )

    async def load_ats_by_codigo(self, codigo: str):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        codigo_raw = str(codigo or "").strip()
        if codigo_raw == "":
            self.form_error = "Ingresa un codigo ATS para cargar."
            return

        with rx.session() as session:
            ats_id = resolve_ats_id_by_codigo(session, codigo_raw, user_id, role_code)
            if ats_id <= 0:
                ats_id = resolve_ats_id_by_uuid(session, codigo_raw, user_id, role_code)
            ats = session.get(Ats, ats_id) if ats_id > 0 else None
            if ats:
                self.ats_id = int(ats.id or 0)
                self.ats_uuid = ats.uuid
                self.codigo_publico = ats.codigo_publico
                self.empresa_persona_ejecuta = ats.empresa_persona_ejecuta
                self.fecha_elaboracion = str(ats.fecha_elaboracion or "")
                self.ciudad = ats.ciudad
                self.area_lugar = ats.area_lugar
                self.numero_ats = ats.numero_ats or ""
                self.tipo_ats_id = int(ats.tipo_ats_id or 0)
                self.duracion_actividad = ats.duracion_actividad
                self.actividad_alto_riesgo = bool(ats.actividad_alto_riesgo)
                self.descripcion_actividad = ats.descripcion_actividad
                self.observaciones = ats.observaciones or ""

                self._load_apoyos_selection_with_session(session, int(ats.id or 0))
                self._load_certificados_selection_with_session(session, int(ats.id or 0))
                self._load_peligros_selection_with_session(session, int(ats.id or 0))
                self._load_pasos_for_current_ats_with_session(session, int(ats.id or 0))
                self._load_trabajadores_for_current_ats_with_session(session, int(ats.id or 0))
                self._load_firmas_finales_for_current_ats_with_session(session, int(ats.id or 0))

                self.form_success = f"ATS {self.codigo_publico} cargado para edicion."
            else:
                self._apply_apoyos_selection({})
                self._apply_certificados_selection({})
                self._apply_peligros_selection({})
                self.pasos_actividad = []
                self.trabajadores_actividad = []
                self._rebuild_firmas_finales({})
                self.form_error = "No se encontro un ATS accesible con ese codigo."

    async def load_initial_data(self):
        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self.ats_recientes = []
            return

        with rx.session() as session:
            tipos = session.exec(select(AtsTipo).where(AtsTipo.activo.is_(True))).all()
            apoyos = session.exec(select(ApoyoCatalogo).where(ApoyoCatalogo.activo.is_(True))).all()
            certificados = session.exec(
                select(CertificadoCatalogo).where(CertificadoCatalogo.activo.is_(True))
            ).all()
            peligros = session.exec(
                select(PeligroCatalogo).where(PeligroCatalogo.activo.is_(True)).order_by(PeligroCatalogo.orden)
            ).all()
            controles = session.exec(
                select(ControlCatalogo).where(ControlCatalogo.activo.is_(True)).order_by(ControlCatalogo.id)
            ).all()
            trabajadores = session.exec(
                select(Trabajador).where(Trabajador.activo.is_(True)).order_by(Trabajador.nombre_completo, Trabajador.id)
            ).all()
            firma_tipos = session.exec(
                select(FirmaTipoCatalogo).where(FirmaTipoCatalogo.activo.is_(True)).order_by(FirmaTipoCatalogo.orden)
            ).all()

            self.tipos_ats = [
                {"id": int(item.id or 0), "nombre": item.nombre, "codigo": item.codigo}
                for item in tipos
            ]
            self.apoyos_catalogo = [
                {
                    "id": int(item.id or 0),
                    "codigo": str(item.codigo or ""),
                    "nombre": str(item.nombre or ""),
                    "permite_descripcion_libre": bool(item.permite_descripcion_libre),
                    "seleccionado": False,
                    "descripcion_otro": "",
                }
                for item in apoyos
            ]
            self.certificados_catalogo = [
                {
                    "id": int(item.id or 0),
                    "codigo": str(item.codigo or ""),
                    "nombre": str(item.nombre or ""),
                    "permite_descripcion_libre": bool(item.permite_descripcion_libre),
                    "seleccionado": False,
                    "descripcion_otro": "",
                }
                for item in certificados
            ]
            self.peligros_catalogo = [
                {
                    "id": int(item.id or 0),
                    "codigo": str(item.codigo or ""),
                    "numero": item.numero_visual,
                    "nombre": item.nombre,
                    "permite_descripcion_libre": bool(item.permite_descripcion_libre),
                    "seleccionado": False,
                    "descripcion_otro": "",
                }
                for item in peligros
            ]
            self.controles_catalogo = [
                {
                    "id": int(item.id or 0),
                    "codigo": str(item.codigo or ""),
                    "nombre": str(item.nombre or ""),
                    "descripcion": str(item.descripcion or ""),
                    "tipo_control": str(item.tipo_control or ""),
                    "permite_descripcion_libre": bool(item.permite_descripcion_libre),
                }
                for item in controles
            ]
            self.trabajadores_catalogo = [
                {
                    "id": int(item.id or 0),
                    "nombre_completo": str(item.nombre_completo or ""),
                    "numero_documento": str(item.numero_documento or ""),
                    "cargo": str(item.cargo or ""),
                }
                for item in trabajadores
            ]
            self.firma_tipos_catalogo = [
                {"id": int(item.id or 0), "codigo": str(item.codigo or ""), "nombre": str(item.nombre or ""), "orden": int(item.orden or 0)}
                for item in firma_tipos
            ]

            scope_condition, scope_params = self._ats_scope_condition_sql(
                alias="a",
                current_user_id=user_id,
                role_code=role_code,
            )
            rows = session.execute(
                text(
                    f"""
                    SELECT a.id, a.codigo_publico, e.nombre AS estado, a.empresa_persona_ejecuta, a.fecha_elaboracion
                    FROM ats a
                    JOIN ats_estado e ON e.id = a.estado_id
                    WHERE {scope_condition}
                    ORDER BY a.id DESC
                    LIMIT 10
                    """
                ),
                scope_params,
            ).mappings().all()
            self.ats_recientes = [dict(row) for row in rows]

            current_ats_id = int(self.ats_id or 0)
            if current_ats_id > 0:
                try:
                    assert_can_access_ats(session, current_ats_id, user_id, role_code)
                    self._load_apoyos_selection_with_session(session, current_ats_id)
                    self._load_certificados_selection_with_session(session, current_ats_id)
                    self._load_peligros_selection_with_session(session, current_ats_id)
                    self._load_pasos_for_current_ats_with_session(session, current_ats_id)
                    self._load_trabajadores_for_current_ats_with_session(session, current_ats_id)
                    self._load_firmas_finales_for_current_ats_with_session(session, current_ats_id)
                except AccessDeniedError:
                    self.ats_id = 0
                    self.ats_uuid = ""
                    self.codigo_publico = ""
                    self._apply_apoyos_selection({})
                    self._apply_certificados_selection({})
                    self._apply_peligros_selection({})
                    self.pasos_actividad = []
                    self.trabajadores_actividad = []
                    self._rebuild_firmas_finales({})

    async def save_identificacion_general(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        required = [
            self.empresa_persona_ejecuta,
            self.fecha_elaboracion,
            self.ciudad,
            self.area_lugar,
            self.duracion_actividad,
            self.descripcion_actividad,
        ]
        if not all(value and str(value).strip() for value in required):
            self.form_error = "Completa los campos obligatorios de Identificación General."
            return

        is_edit_mode = self.ats_id > 0
        now_ts = datetime.utcnow()
        estado_aplicado = self.ATS_ESTADO_BORRADOR

        with rx.session() as session:
            try:
                estado_borrador_id = self._resolve_estado_id_by_codigo_with_session(
                    session,
                    self.ATS_ESTADO_BORRADOR,
                )
            except RuntimeError as exc:
                self.form_error = str(exc)
                return

            tipo_ats_id = self.tipo_ats_id
            if not tipo_ats_id:
                tipo_default = session.exec(select(AtsTipo).order_by(AtsTipo.id)).first()
                if tipo_default is None:
                    self.form_error = "No existe un tipo ATS configurado."
                    return
                tipo_ats_id = int(tipo_default.id or 0)

            if is_edit_mode:
                # Editar ATS existente
                ats = session.get(Ats, self.ats_id)
                if not ats:
                    self.form_error = "ATS no encontrado para edicion."
                    return
                try:
                    assert_can_edit_ats(session, int(self.ats_id or 0), user_id, role_code)
                except AccessDeniedError as exc:
                    self.form_error = str(exc)
                    return
                ats.empresa_persona_ejecuta = self.empresa_persona_ejecuta.strip()
                ats.fecha_elaboracion = self._parse_iso_date(self.fecha_elaboracion)
                ats.ciudad = self.ciudad.strip()
                ats.area_lugar = self.area_lugar.strip()
                ats.numero_ats = self.numero_ats.strip() or None
                ats.tipo_ats_id = tipo_ats_id
                ats.duracion_actividad = self.duracion_actividad.strip()
                ats.actividad_alto_riesgo = bool(self.actividad_alto_riesgo)
                ats.descripcion_actividad = self.descripcion_actividad.strip()
                ats.observaciones = self.observaciones.strip() or None

                # Eliminar apoyos y certificados existentes
                session.exec(delete(AtsApoyo).where(AtsApoyo.ats_id == self.ats_id))
                session.exec(delete(AtsCertificado).where(AtsCertificado.ats_id == self.ats_id))
            else:
                # Crear ATS nuevo
                ats_uuid = str(uuid.uuid4())
                codigo_publico = f"ATS-{str(uuid.uuid4())[:8].upper()}"

                ats = Ats(
                    uuid=ats_uuid,
                    codigo_publico=codigo_publico,
                    estado_id=int(estado_borrador_id),
                    tipo_ats_id=int(tipo_ats_id),
                    creado_por_usuario_id=user_id,
                    empresa_persona_ejecuta=self.empresa_persona_ejecuta.strip(),
                    fecha_elaboracion=self._parse_iso_date(self.fecha_elaboracion),
                    ciudad=self.ciudad.strip(),
                    area_lugar=self.area_lugar.strip(),
                    numero_ats=self.numero_ats.strip() or None,
                    duracion_actividad=self.duracion_actividad.strip(),
                    actividad_alto_riesgo=bool(self.actividad_alto_riesgo),
                    descripcion_actividad=self.descripcion_actividad.strip(),
                    observaciones=self.observaciones.strip() or None,
                    created_at=now_ts,
                    updated_at=now_ts,
                )
                session.add(ats)
                session.flush()

            ats_id = int(ats.id or 0)
            if ats_id <= 0:
                self.form_error = "No se pudo generar el identificador del ATS."
                session.rollback()
                return

            apoyo_desc_map: dict[int, str] = {
                int(item.get("id") or 0): str(item.get("descripcion_otro") or "").strip()
                for item in self.apoyos_catalogo
                if bool(item.get("permite_descripcion_libre"))
            }
            certificado_desc_map: dict[int, str] = {
                int(item.get("id") or 0): str(item.get("descripcion_otro") or "").strip()
                for item in self.certificados_catalogo
                if bool(item.get("permite_descripcion_libre"))
            }

            # Guardar apoyos seleccionados
            for apoyo_id in self.apoyos_seleccionados:
                descripcion_otro = apoyo_desc_map.get(int(apoyo_id), "")
                session.add(
                    AtsApoyo(
                        ats_id=ats_id,
                        apoyo_id=apoyo_id,
                        descripcion_otro=descripcion_otro or None,
                        created_at=now_ts,
                    )
                )

            # Guardar certificados seleccionados
            for certificado_id in self.certificados_seleccionados:
                descripcion_otro = certificado_desc_map.get(int(certificado_id), "")
                session.add(
                    AtsCertificado(
                        ats_id=ats_id,
                        certificado_id=certificado_id,
                        descripcion_otro=descripcion_otro or None,
                        created_at=now_ts,
                    )
                )

            try:
                estado_aplicado = self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_BORRADOR,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return

            session.commit()
            session.refresh(ats)

            self.ats_id = ats_id
            self.ats_uuid = ats.uuid
            self.codigo_publico = ats.codigo_publico
            action = "actualizado" if is_edit_mode else "guardado"
            self.form_success = (
                f"ATS {action}: {self.codigo_publico} "
                f"(estado: {estado_aplicado})"
            )

        await self.load_initial_data()
        self.load_peligros_for_current_ats()
        self.current_step = 2

    async def save_peligros_riesgos(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.form_error = "Primero guarda la identificación general del ATS."
            return

        with rx.session() as session:
            try:
                assert_can_edit_ats(session, ats_id, user_id, role_code)
            except AccessDeniedError as exc:
                self.form_error = str(exc)
                return

            ats = session.get(Ats, ats_id)
            if not ats:
                self.form_error = "ATS no encontrado para guardar peligros."
                return

            session.exec(delete(AtsPeligro).where(AtsPeligro.ats_id == ats_id))

            seen: set[int] = set()
            now_ts = datetime.utcnow()
            for item in self.peligros_catalogo:
                if not bool(item.get("seleccionado")):
                    continue

                peligro_id = int(item.get("id") or 0)
                if peligro_id <= 0 or peligro_id in seen:
                    continue
                seen.add(peligro_id)

                allows_free_text = bool(item.get("permite_descripcion_libre"))
                descripcion_otro = (item.get("descripcion_otro") or "").strip() if allows_free_text else ""

                session.add(
                    AtsPeligro(
                        ats_id=ats_id,
                        peligro_id=peligro_id,
                        descripcion_otro=descripcion_otro or None,
                        created_at=now_ts,
                    )
                )

            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_EN_PROCESO,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return

            session.commit()
            self.form_success = "Peligros y riesgos guardados correctamente."

        self.load_peligros_for_current_ats()
        self.load_pasos_for_current_ats()

    async def save_peligros_riesgos_y_continuar(self):
        await self.save_peligros_riesgos()
        if self.form_error == "":
            self.load_pasos_for_current_ats()
            self.next_step()

    async def save_pasos_actividad(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.form_error = "Primero guarda la identificacion general del ATS."
            return

        payload = [dict(item) for item in self.pasos_actividad]
        if not payload:
            self.form_error = "Agrega al menos un paso en la actividad."
            return

        with rx.session() as session:
            try:
                assert_can_edit_ats(session, ats_id, user_id, role_code)
            except AccessDeniedError as exc:
                self.form_error = str(exc)
                return

            ats = session.get(Ats, ats_id)
            if not ats:
                self.form_error = "ATS no encontrado para guardar pasos."
                return

            control_rows = session.exec(
                select(ControlCatalogo).where(ControlCatalogo.activo.is_(True))
            ).all()
            control_map = {int(item.id or 0): item for item in control_rows if int(item.id or 0) > 0}
            if not control_map:
                self.form_error = "No hay controles activos en el catalogo."
                return

            otro_control_id = self._otro_control_id()
            if otro_control_id <= 0:
                self.form_error = "No existe el control OTROS en el catalogo."
                return

            cleaned_steps: list[dict] = []
            used_peligro_ids: set[int] = set()

            for idx, paso in enumerate(payload, start=1):
                descripcion = str(paso.get("descripcion_paso") or "").strip()
                if not descripcion:
                    self.form_error = f"Completa la descripcion del paso {idx}."
                    return

                peligros = [dict(item) for item in paso.get("peligros", [])]
                if not peligros:
                    self.form_error = f"Agrega al menos un peligro en el paso {idx}."
                    return

                seen_in_step: set[int] = set()
                cleaned_peligros: list[dict] = []
                for peligro in peligros:
                    peligro_id = int(peligro.get("peligro_id") or 0)
                    if peligro_id <= 0:
                        self.form_error = f"El paso {idx} contiene un peligro no valido."
                        return
                    if peligro_id in seen_in_step:
                        self.form_error = f"El paso {idx} tiene peligros duplicados."
                        return
                    seen_in_step.add(peligro_id)

                    descripcion_otro = str(peligro.get("descripcion_otro") or "").strip()
                    if self._is_peligro_otro(peligro_id):
                        if not descripcion_otro:
                            self.form_error = f"Cuando uses OTRO_PELIGRO, debes escribir la descripcion en el paso {idx}."
                            return
                    else:
                        descripcion_otro = ""

                    controls = [dict(item) for item in peligro.get("controls", [])]
                    if not controls:
                        self.form_error = f"Agrega al menos un control para cada peligro del paso {idx}."
                        return

                    seen_controls: set[int] = set()
                    cleaned_controls: list[dict] = []
                    for control in controls:
                        control_id = int(control.get("control_id") or 0)
                        if control_id <= 0:
                            self.form_error = f"Selecciona un control valido para todos los peligros del paso {idx}."
                            return

                        if control_id in seen_controls:
                            self.form_error = f"No repitas controles en el mismo peligro del paso {idx}."
                            return
                        seen_controls.add(control_id)

                        control_row = control_map.get(control_id)
                        if control_row is None:
                            self.form_error = f"Selecciona un control valido para todos los peligros del paso {idx}."
                            return

                        if control_id == otro_control_id:
                            control_aplicado = str(control.get("control_aplicado") or "").strip()
                            if not control_aplicado:
                                self.form_error = f"Cuando uses OTROS, debes escribir el control aplicado en el paso {idx}."
                                return
                        else:
                            control_aplicado = str(control_row.nombre or "").strip()
                            if not control_aplicado:
                                self.form_error = f"El control seleccionado en el paso {idx} no tiene nombre."
                                return

                        cleaned_controls.append(
                            {
                                "control_id": control_id,
                                "control_aplicado": control_aplicado,
                            }
                        )

                    cleaned_peligros.append(
                        {
                            "peligro_id": peligro_id,
                            "descripcion_otro": descripcion_otro,
                            "controls": cleaned_controls,
                        }
                    )
                    used_peligro_ids.add(peligro_id)

                cleaned_steps.append(
                    {
                        "numero_paso": idx,
                        "descripcion_paso": descripcion,
                        "peligros": cleaned_peligros,
                    }
                )

            if not used_peligro_ids:
                self.form_error = "No hay peligros asociados en los pasos."
                return

            now_ts = datetime.utcnow()
            current_ats_peligros = session.exec(
                select(AtsPeligro).where(AtsPeligro.ats_id == ats_id)
            ).all()
            ats_peligro_map = {
                int(row.peligro_id or 0): int(row.id or 0)
                for row in current_ats_peligros
                if int(row.peligro_id or 0) > 0 and int(row.id or 0) > 0
            }

            for peligro_id in sorted(used_peligro_ids):
                if peligro_id in ats_peligro_map:
                    continue
                new_row = AtsPeligro(
                    ats_id=ats_id,
                    peligro_id=peligro_id,
                    descripcion_otro=None,
                    created_at=now_ts,
                )
                session.add(new_row)
                session.flush()
                ats_peligro_map[peligro_id] = int(new_row.id or 0)

            session.execute(
                text(
                    """
                    DELETE FROM ats_paso_peligro_control
                    WHERE ats_paso_peligro_id IN (
                        SELECT app.id
                        FROM ats_paso_peligro app
                        JOIN ats_paso p ON p.id = app.ats_paso_id
                        WHERE p.ats_id = :ats_id
                    )
                    """
                ),
                {"ats_id": ats_id},
            )
            session.execute(
                text(
                    """
                    DELETE FROM ats_paso_peligro
                    WHERE ats_paso_id IN (
                        SELECT id FROM ats_paso WHERE ats_id = :ats_id
                    )
                    """
                ),
                {"ats_id": ats_id},
            )
            session.exec(delete(AtsPaso).where(AtsPaso.ats_id == ats_id))

            for paso in cleaned_steps:
                row = AtsPaso(
                    ats_id=ats_id,
                    numero_paso=int(paso["numero_paso"]),
                    descripcion_paso=str(paso["descripcion_paso"]),
                    created_at=now_ts,
                    updated_at=now_ts,
                )
                session.add(row)
                session.flush()

                paso_id = int(row.id or 0)
                if paso_id <= 0:
                    self.form_error = "No fue posible generar el id de un paso."
                    session.rollback()
                    return

                for peligro in paso["peligros"]:
                    ats_peligro_id = int(ats_peligro_map.get(int(peligro["peligro_id"])) or 0)
                    if ats_peligro_id <= 0:
                        self.form_error = "No fue posible vincular un peligro con el ATS."
                        session.rollback()
                        return

                    paso_peligro_row = AtsPasoPeligro(
                        ats_paso_id=paso_id,
                        ats_peligro_id=ats_peligro_id,
                        descripcion_otro=str(peligro.get("descripcion_otro") or "").strip() or None,
                    )
                    session.add(paso_peligro_row)
                    session.flush()

                    paso_peligro_id = int(paso_peligro_row.id or 0)
                    if paso_peligro_id <= 0:
                        self.form_error = "No fue posible vincular un peligro con un paso."
                        session.rollback()
                        return

                    for control in peligro["controls"]:
                        session.add(
                            AtsPasoPeligroControl(
                                ats_paso_peligro_id=paso_peligro_id,
                                control_id=int(control["control_id"]),
                                control_aplicado=str(control["control_aplicado"]),
                                created_at=now_ts,
                                updated_at=now_ts,
                            )
                        )

            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_EN_PROCESO,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return

            session.commit()
            self.form_success = "Paso a paso guardado correctamente."

            self._load_pasos_for_current_ats_with_session(session, ats_id)

    async def save_pasos_actividad_y_continuar(self):
        await self.save_pasos_actividad()
        if self.form_error == "":
            self.load_trabajadores_for_current_ats()
            self.next_step()

    async def save_trabajadores_actividad(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.form_error = "Primero guarda la identificacion general del ATS."
            return

        payload = [dict(item) for item in self.trabajadores_actividad]
        if not payload:
            self.form_error = "Importa al menos un trabajador."
            return

        seen_worker_ids: set[int] = set()
        for idx, trabajador in enumerate(payload, start=1):
            trabajador_id = int(trabajador.get("trabajador_id") or 0)
            nombre = str(trabajador.get("nombre_trabajador") or "").strip()
            documento = str(trabajador.get("numero_documento") or "").strip()
            cargo = str(trabajador.get("cargo_trabajador") or "").strip()
            firma = str(trabajador.get("firma_base64") or "").strip()

            if trabajador_id <= 0:
                self.form_error = f"El trabajador {idx} no tiene referencia valida en el catalogo."
                return
            if not nombre or not documento:
                self.form_error = f"Completa nombre y documento del trabajador {idx}."
                return
            if not firma:
                self.form_error = f"Guarda la firma del trabajador {idx}."
                return
            if trabajador_id in seen_worker_ids:
                self.form_error = "No puedes importar el mismo trabajador mas de una vez."
                return
            seen_worker_ids.add(trabajador_id)

            trabajador["numero_orden"] = idx
            trabajador["trabajador_id"] = trabajador_id
            trabajador["nombre_trabajador"] = nombre
            trabajador["numero_documento"] = documento
            trabajador["cargo_trabajador"] = cargo
            trabajador["firma_base64"] = firma

        with rx.session() as session:
            try:
                assert_can_edit_ats(session, ats_id, user_id, role_code)
            except AccessDeniedError as exc:
                self.form_error = str(exc)
                return

            ats = session.get(Ats, ats_id)
            if not ats:
                self.form_error = "ATS no encontrado para guardar trabajadores."
                return

            valid_worker_ids = {
                int(row.id or 0)
                for row in session.exec(select(Trabajador).where(Trabajador.activo.is_(True))).all()
                if int(row.id or 0) > 0
            }
            invalid_rows = [
                str(item.get("numero_orden") or "?")
                for item in payload
                if int(item.get("trabajador_id") or 0) not in valid_worker_ids
            ]
            if invalid_rows:
                self.form_error = "Uno o mas trabajadores ya no existen en catalogo. Reimporta antes de guardar."
                return

            session.exec(delete(AtsTrabajador).where(AtsTrabajador.ats_id == ats_id))

            for trabajador in payload:
                session.add(
                    AtsTrabajador(
                        ats_id=ats_id,
                        numero_orden=int(trabajador["numero_orden"]),
                        trabajador_id=int(trabajador["trabajador_id"]),
                        nombre_trabajador=str(trabajador["nombre_trabajador"]),
                        numero_documento=str(trabajador["numero_documento"]),
                        cargo_trabajador=str(trabajador["cargo_trabajador"]) or None,
                        nombre_snapshot=str(trabajador["nombre_trabajador"]),
                        documento_snapshot=str(trabajador["numero_documento"]),
                        cargo_snapshot=str(trabajador["cargo_trabajador"]) or None,
                        firma_base64=str(trabajador["firma_base64"]),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                )

            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_EN_PROCESO,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return

            session.commit()
            self.form_success = "Trabajadores y firmas guardados correctamente."
            self._load_trabajadores_for_current_ats_with_session(session, ats_id)

    async def save_trabajadores_actividad_y_continuar(self):
        await self.save_trabajadores_actividad()
        if self.form_error == "":
            self.load_observaciones_for_current_ats()
            self.next_step()

    def load_observaciones_for_current_ats(self):
        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.observaciones = ""
            return

        try:
            with rx.session() as session:
                self._assert_ats_access(session, ats_id, for_edit=False)
                ats = session.get(Ats, ats_id)
                if not ats:
                    self.form_error = "ATS no encontrado para cargar observaciones."
                    return
                self.observaciones = str(ats.observaciones or "")
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            self.observaciones = ""

    async def save_observaciones(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.form_error = "Primero guarda la identificacion general del ATS."
            return

        with rx.session() as session:
            try:
                assert_can_edit_ats(session, ats_id, user_id, role_code)
            except AccessDeniedError as exc:
                self.form_error = str(exc)
                return

            ats = session.get(Ats, ats_id)
            if not ats:
                self.form_error = "ATS no encontrado para guardar observaciones."
                return

            ats.observaciones = str(self.observaciones or "").strip() or None
            ats.updated_at = datetime.utcnow()

            session.add(ats)
            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_EN_PROCESO,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return
            session.commit()
            session.refresh(ats)

            self.observaciones = str(ats.observaciones or "")
            self.form_success = "Observaciones guardadas correctamente."

    async def save_observaciones_y_continuar(self):
        await self.save_observaciones()
        if self.form_error == "":
            self.load_firmas_finales_for_current_ats()
            self.next_step()

    async def save_firmas_finales(self):
        self.form_error = ""
        self.form_success = ""

        session_state = await self.get_state(SessionState)
        if not session_state.is_authenticated:
            return rx.redirect("/login")

        self._sync_auth_context(session_state)
        try:
            user_id, role_code = self._require_ats_role_context()
        except AccessDeniedError as exc:
            self.form_error = str(exc)
            return

        ats_id = int(self.ats_id or 0)
        if ats_id <= 0:
            self.form_error = "Primero guarda la identificacion general del ATS."
            return

        payload = [dict(item) for item in self.firmas_finales]
        if not payload:
            self.form_error = "No hay tipos de firma configurados."
            return

        cleaned_payload: list[dict] = []
        seen_tipo_ids: set[int] = set()
        for item in payload:
            firma_tipo_id = int(item.get("firma_tipo_id") or 0)
            if firma_tipo_id <= 0 or firma_tipo_id in seen_tipo_ids:
                continue
            seen_tipo_ids.add(firma_tipo_id)

            nombre = str(item.get("nombre_completo") or "").strip()
            cargo = str(item.get("cargo") or "").strip()
            firma = str(item.get("firma_base64") or "").strip()
            firma_tipo_nombre = str(item.get("firma_tipo_nombre") or "firma").strip()

            if not nombre:
                self.form_error = f"Completa el nombre en {firma_tipo_nombre}."
                return
            if not firma:
                self.form_error = f"Captura la firma en {firma_tipo_nombre}."
                return

            cleaned_payload.append(
                {
                    "firma_tipo_id": firma_tipo_id,
                    "nombre_completo": nombre,
                    "cargo": cargo,
                    "firma_base64": firma,
                }
            )

        with rx.session() as session:
            try:
                assert_can_edit_ats(session, ats_id, user_id, role_code)
            except AccessDeniedError as exc:
                self.form_error = str(exc)
                return

            ats = session.get(Ats, ats_id)
            if not ats:
                self.form_error = "ATS no encontrado para guardar firmas finales."
                return

            session.exec(delete(AtsFirmaFinal).where(AtsFirmaFinal.ats_id == ats_id))

            now_ts = datetime.utcnow()
            for item in cleaned_payload:
                session.add(
                    AtsFirmaFinal(
                        ats_id=ats_id,
                        firma_tipo_id=int(item["firma_tipo_id"]),
                        nombre_completo=str(item["nombre_completo"]),
                        cargo=str(item["cargo"]) or None,
                        firma_base64=str(item["firma_base64"]),
                        created_at=now_ts,
                        updated_at=now_ts,
                    )
                )

            try:
                self._set_ats_status_with_session(
                    session=session,
                    ats_id=ats_id,
                    target_estado_codigo=self.ATS_ESTADO_FINALIZADO,
                    user_id=user_id,
                    role_code=role_code,
                )
            except (AccessDeniedError, RuntimeError) as exc:
                self.form_error = str(exc)
                session.rollback()
                return

            session.commit()
            self.form_success = "Firmas finales guardadas correctamente."
            self._load_firmas_finales_for_current_ats_with_session(session, ats_id)

    async def save_firmas_finales_y_continuar(self):
        await self.save_firmas_finales()
        if self.form_error == "":
            self.next_step()

    def reset_form(self):
        self.current_step = 1
        self.ats_id = 0
        self.ats_uuid = ""
        self.codigo_publico = ""
        self.empresa_persona_ejecuta = ""
        self.fecha_elaboracion = str(date.today())
        self.ciudad = ""
        self.area_lugar = ""
        self.numero_ats = ""
        self.tipo_ats_id = 0
        self.duracion_actividad = ""
        self.actividad_alto_riesgo = False
        self.descripcion_actividad = ""
        self.observaciones = ""
        self.apoyos_seleccionados = []
        self.certificados_seleccionados = []
        self._apply_apoyos_selection({})
        self._apply_certificados_selection({})
        self._apply_peligros_selection({})
        self.paso3_peligro_modal_open = False
        self.paso3_peligro_modal_step_uid = ""
        self.paso3_peligro_search = ""
        self.pasos_actividad = []
        self.trabajador_import_modal_open = False
        self.trabajador_import_search = ""
        self.trabajador_import_selected_ids = []
        self.trabajadores_actividad = []
        self._rebuild_firmas_finales({})
        self.documentos_ats_options = []
        self.documentos_generados = []
        self.load_codigo_input = ""
        self.documento_search_query = ""
        self.documento_selected_ats_id = 0
        self.documento_selected_codigo = ""
        self.documento_generado_url = ""
        self.documento_generado_nombre = ""
        self.documento_error = ""
        self.documento_success = ""
        self.form_error = ""
        self.form_success = ""

    def set_empresa_persona_ejecuta(self, value: str):
        self.empresa_persona_ejecuta = value

    def set_fecha_elaboracion(self, value: str):
        self.fecha_elaboracion = value

    def set_ciudad(self, value: str):
        self.ciudad = value

    def set_area_lugar(self, value: str):
        self.area_lugar = value

    def set_numero_ats(self, value: str):
        self.numero_ats = value

    def set_duracion_actividad(self, value: str):
        self.duracion_actividad = value

    def set_descripcion_actividad(self, value: str):
        self.descripcion_actividad = value

    def set_actividad_alto_riesgo(self, value: bool):
        self.actividad_alto_riesgo = value

    def set_observaciones(self, value: str):
        self.observaciones = value
