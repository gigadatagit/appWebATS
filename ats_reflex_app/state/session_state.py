from __future__ import annotations

import reflex as rx
from sqlmodel import select

from ..auth_supabase import sign_in_with_password
from ..models import Rol, Usuario


class SessionState(rx.State):
    email: str = ""
    password: str = ""
    login_error: str = ""

    current_auth_user_id: str = ""
    current_user_id: int = 0
    current_user_email: str = ""
    current_user_name: str = ""
    current_user_role_codigo: str = ""

    # Legacy aliases to minimize impact across existing states/UI.
    user_id: int = 0
    nombre_usuario: str = ""
    rol_codigo: str = ""

    is_authenticated: bool = False

    @rx.var
    def is_admin(self) -> bool:
        role_code = str(self.current_user_role_codigo or self.rol_codigo or "").upper()
        return self.is_authenticated and role_code == "ADMIN"

    @rx.var
    def is_siso(self) -> bool:
        role_code = str(self.current_user_role_codigo or self.rol_codigo or "").upper()
        return self.is_authenticated and role_code == "SISO"

    def clear_login_form(self):
        self.email = ""
        self.password = ""
        self.login_error = ""

    def _clear_auth_state(self):
        self.current_auth_user_id = ""
        self.current_user_id = 0
        self.current_user_email = ""
        self.current_user_name = ""
        self.current_user_role_codigo = ""

        self.user_id = 0
        self.nombre_usuario = ""
        self.rol_codigo = ""
        self.is_authenticated = False

    def logout(self):
        self._clear_auth_state()
        self.clear_login_form()
        return rx.redirect("/login")

    def _resolve_authenticated_home_route(self) -> str:
        role_code = str(self.current_user_role_codigo or self.rol_codigo or "").strip().upper()
        if role_code == "ADMIN":
            return "/sst/dashboard"
        return "/ats/formato"

    def redirect_authenticated_home(self):
        if not self.is_authenticated:
            return
        return rx.redirect(self._resolve_authenticated_home_route())

    def set_email(self, email: str):
        self.email = email

    def set_username(self, username: str):
        # Legacy alias.
        self.email = username

    def set_password(self, password: str):
        self.password = password

    def login(self):
        self.login_error = ""

        if not str(self.email or "").strip() or not str(self.password or "").strip():
            self.login_error = "Ingresa correo y contrasena."
            return

        try:
            auth_payload = sign_in_with_password(
                email=str(self.email).strip(),
                password=self.password,
            )
        except Exception as exc:
            self.login_error = str(exc)
            return

        auth_user_id = str(auth_payload.get("auth_user_id") or "").strip()
        auth_user_email = str(auth_payload.get("email") or str(self.email or "")).strip()

        if not auth_user_id:
            self.login_error = "No fue posible validar tu usuario en Supabase Auth."
            return

        with rx.session() as session:
            user = session.exec(
                select(Usuario).where(Usuario.auth_user_id == auth_user_id)
            ).first()
            if user is None:
                self.login_error = (
                    "Tu usuario existe en Supabase Auth, pero aun no tiene perfil interno asignado en la plataforma SST."
                )
                return

            if not bool(user.activo):
                self.login_error = "Tu perfil interno en la plataforma SST esta inactivo."
                return

            role = session.exec(select(Rol).where(Rol.id == user.rol_id)).first()
            if role is None or not bool(role.activo):
                self.login_error = "El usuario no tiene rol valido."
                return

            role_code = str(role.codigo or "").strip().upper()
            current_user_id = int(user.id or 0)
            if current_user_id <= 0 or not role_code:
                self.login_error = "No fue posible cargar el perfil interno del usuario."
                return

            self.current_auth_user_id = auth_user_id
            self.current_user_id = current_user_id
            self.current_user_email = auth_user_email
            self.current_user_name = str(user.nombre_completo or auth_user_email or "")
            self.current_user_role_codigo = role_code

            self.user_id = self.current_user_id
            self.nombre_usuario = self.current_user_name
            self.rol_codigo = self.current_user_role_codigo
            self.is_authenticated = True
            self.password = ""

        return rx.redirect(self._resolve_authenticated_home_route())
