from __future__ import annotations

import reflex as rx
from sqlmodel import select

from ..models import Usuario, Rol
from ..security import verify_password


class SessionState(rx.State):
    username: str = ""
    password: str = ""
    login_error: str = ""

    user_id: int = 0
    nombre_usuario: str = ""
    rol_codigo: str = ""
    is_authenticated: bool = False

    @rx.var
    def is_admin(self) -> bool:
        return self.is_authenticated and self.rol_codigo == "ADMIN"

    @rx.var
    def is_siso(self) -> bool:
        return self.is_authenticated and self.rol_codigo == "SISO"

    def clear_login_form(self):
        self.username = ""
        self.password = ""
        self.login_error = ""

    def logout(self):
        self.user_id = 0
        self.nombre_usuario = ""
        self.rol_codigo = ""
        self.is_authenticated = False
        self.clear_login_form()
        return rx.redirect("/login")
    
    def set_username(self, username: str):
        self.username = username

    def set_password(self, password: str):
        self.password = password

    def login(self):
        self.login_error = ""
        with rx.session() as session:
            user = session.exec(
                select(Usuario).where(Usuario.username == self.username)
            ).first()
            if user is None or int(user.activo or 0) != 1:
                self.login_error = "Usuario no encontrado o inactivo."
                return

            if not verify_password(self.password, user.password_hash):
                self.login_error = "Credenciales inválidas."
                return

            role = session.exec(select(Rol).where(Rol.id == user.rol_id)).first()
            if role is None:
                self.login_error = "El usuario no tiene rol válido."
                return

            self.user_id = int(user.id or 0)
            self.nombre_usuario = user.nombre_completo
            self.rol_codigo = role.codigo
            self.is_authenticated = True
            self.password = ""

        if self.rol_codigo == "ADMIN":
            return rx.redirect("/admin/dashboard")
        return rx.redirect("/ats/formato")
