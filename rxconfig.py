import reflex as rx

config = rx.Config(
    app_name="ats_reflex_app",
    db_url="sqlite:///data/ats_app.db",
    env_file=".env",
)
