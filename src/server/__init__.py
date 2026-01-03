from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.config.csrf import CSRFConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.plugins.htmx import HTMXPlugin
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from pydantic_settings import BaseSettings, SettingsConfigDict

from server.routes import Index
from server.routes import Group


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="sgt_", env_file=".env", env_file_encoding="utf-8")

    secret: str


settings = Settings()  # type: ignore


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    yield


template_config = TemplateConfig(
    directory=[Path("templates"), Path("../client/dist")],
    engine=JinjaTemplateEngine,
)

app = Litestar(
    route_handlers=[
        Index,
        Group,
        create_static_files_router(path="/", directories=["public", "../client/dist"]),
    ],
    lifespan=[lifespan],
    plugins=[HTMXPlugin()],
    template_config=template_config,
    compression_config=CompressionConfig("brotli"),
    csrf_config=CSRFConfig(secret=settings.secret),
    debug=True,
    # pdb_on_exception=True,
)
