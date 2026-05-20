import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

from ats_reflex_app.config import get_database_url

config = rx.Config(
    app_name="ats_reflex_app",
    db_url=get_database_url(),
    env_file=".env",
    disable_plugins=[SitemapPlugin],
)
