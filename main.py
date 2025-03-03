from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from litestar import Litestar, get
from litestar.datastructures import State

if TYPE_CHECKING:
    pass


@get("/", sync_to_thread=False)
async def hello_world(state: State) -> str:
    """Handler function that returns a greeting dictionary."""
    return state.hello


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    yield


state = State({"hello": "world"})

app = Litestar(
    route_handlers=[hello_world],
    lifespan=[lifespan],
    state=state,
)
