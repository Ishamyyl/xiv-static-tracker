import logging
from contextlib import asynccontextmanager
from os import environ

from aerich import Command
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_303_SEE_OTHER, HTTP_404_NOT_FOUND
from starlette.templating import Jinja2Templates
from tortoise import Tortoise
from tortoise.transactions import in_transaction

from database import Gear, Group, Job, Player, Quality, Slot, needs_color_mapping

templates = Jinja2Templates(directory="templates")
templates.env.globals["Quality"] = Quality
templates.env.globals["Job"] = Job
templates.env.globals["Slot"] = Slot
templates.env.globals["needs_color_mapping"] = needs_color_mapping


DATABASE_URL = environ.get("DATABASE_URL", "sqlite://app.db").replace("postgres", "asyncpg")


async def index(req: Request):
    gs = await Group.all()
    return templates.TemplateResponse("pages/index.html", {"request": req, "groups": gs})


class Gears(HTTPEndpoint):
    async def get(self, req: Request):
        if not (g := await Gear.filter(id=req.path_params["gear_id"]).first()):
            raise HTTPException(HTTP_404_NOT_FOUND)
        return templates.TemplateResponse("pages/gear.html", {"request": req, "gear": g})

    async def patch(self, req: Request):
        data = await req.form()

        # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
        q = Gear.filter(id=req.path_params["gear_id"]).update(**data).sql() + " RETURNING *"
        async with in_transaction() as conn:
            r = (await conn.execute_query_dict(q, list(data.values())))[0]

        if not r:
            raise HTTPException(HTTP_404_NOT_FOUND)

        g = Gear(**r)  # hydrate from raw cursor
        return templates.TemplateResponse(
            "components/gear/details.html",
            {"request": req, "gear": g},
            headers={"HX-Trigger": f"reload-needs-{g.player_id}"},
        )


class Players(HTTPEndpoint):
    async def get(self, req: Request):
        if not (p := await Player.filter(id=req.path_params["player_id"]).prefetch_related("gearset", "group").first()):
            raise HTTPException(HTTP_404_NOT_FOUND)
        return templates.TemplateResponse("pages/player.html", {"request": req, "player": p})

    async def post(self, req: Request):
        data = await req.form()
        p = Player(group_id=data["group_id"])

        # TODO: database failure handling
        await p.save()
        await Gear.bulk_create([Gear(slot=s, player=p) for s in Slot])
        await p.fetch_related("gearset")

        return templates.TemplateResponse("components/player/index.html", {"request": req, "player": p})

    async def patch(self, req: Request):
        data = await req.form()

        # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
        q = Player.filter(id=req.path_params["player_id"]).update(**data).sql() + " RETURNING *"
        async with in_transaction() as conn:
            r = (await conn.execute_query_dict(q, list(data.values())))[0]

        if not r:
            raise HTTPException(HTTP_404_NOT_FOUND)
        p = Player(**r)  # hydrate from raw cursor
        return templates.TemplateResponse("components/player/details.html", {"request": req, "player": p})


async def needs(req: Request):
    if not (p := await Player.filter(id=req.path_params["player_id"]).prefetch_related("gearset").first()):
        raise HTTPException(HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("components/player/needs.html", {"request": req, "player": p})


class Groups(HTTPEndpoint):
    async def get(self, req: Request):
        if not (g := await Group.filter(id=req.path_params["group_id"]).prefetch_related("players", "players__gearset", "players__group").first()):
            raise HTTPException(HTTP_404_NOT_FOUND)
        return templates.TemplateResponse("pages/group.html", {"request": req, "group": g})

    async def post(self, req: Request):
        g = Group()
        # TODO: handle database failures
        await g.save()
        return RedirectResponse(req.url_for("groups", group_id=g.id), status_code=HTTP_303_SEE_OTHER)

    async def patch(self, req: Request):
        data = await req.form()

        # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
        q = Group.filter(id=req.path_params["group_id"]).update(**data).sql() + " RETURNING *"
        async with in_transaction() as conn:
            r = (await conn.execute_query_dict(q, list(data.values())))[0]

        if not r:
            raise HTTPException(HTTP_404_NOT_FOUND)

        g = Group(**r)  # hydrate from raw cursor
        return templates.TemplateResponse("components/group/details.html", {"request": req, "group": g})


async def test(req: Request):
    return HTMLResponse("<p>test</p>")


TORTOISE_CONFIG = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "app": {
            "models": ["database", "aerich.models"],
        },
    },
}


@asynccontextmanager
async def lifespan(app: Starlette):
    await Tortoise.init(config=TORTOISE_CONFIG)
    command = Command(tortoise_config=TORTOISE_CONFIG, app="app")
    await command.init()
    await command.upgrade(run_in_transaction=True)
    yield
    await Tortoise.close_connections()


logger_db_client = logging.getLogger("tortoise.db_client")
logger_db_client.addHandler(logging.StreamHandler())
logger_db_client.setLevel(logging.DEBUG)

app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/test", test),
        Mount("/static", StaticFiles(directory="static"), name="static"),
        Route("/groups/{group_id:int}", Groups, name="groups"),
        Route("/players/{player_id:int}", Players, name="players"),
        Route("/gears/{gear_id:int}", Gears, name="gears"),
        Route("/needs/{player_id:int}", needs, name="needs"),
        Route("/", index),
    ],
)
