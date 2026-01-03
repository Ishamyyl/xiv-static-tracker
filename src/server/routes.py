import json

from litestar.controller import Controller
from litestar.handlers import get
from litestar.enums import MediaType
from litestar.response import Template


class Index(Controller):
    @get(media_type=MediaType.HTML)
    async def index(self) -> Template:
        return Template("index.html")


class Group(Controller):
    path = "/group"

    @get(media_type=MediaType.HTML)
    async def group(self) -> Template:
        return Template(
            "group.html",
            context={
                "props": json.dumps(
                    {
                        "players": [1, 2, 3],
                    }
                )
            },
        )
