import logging
from contextlib import asynccontextmanager
from os import environ

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


DATABASE_URL = environ.get("DATABASE_URL", "sqlite://app.db").replace(
    "postgres", "asyncpg"
)


async def index(req: Request):
    gs = await Group.all()
    return templates.TemplateResponse(
        "pages/index.html", {"request": req, "groups": gs}
    )


class Gears(HTTPEndpoint):
    async def get(self, req: Request):
        if g := await Gear.filter(id=req.query_params["gear_id"]).first():
            return templates.TemplateResponse(
                "pages/gear.html", {"request": req, "gear": g}
            )
        raise HTTPException(HTTP_404_NOT_FOUND)

    async def patch(self, req: Request):
        async with req.form() as data:
            data = dict(data)
            gs_id = data.pop("gear_id")

            # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
            q = Gear.filter(id=gs_id).update(**data).sql() + " RETURNING *"
            async with in_transaction() as conn:
                r = (await conn.execute_query_dict(q, list(data.values())))[0]

            if r:
                g = Gear(**r)  # hydrate from raw cursor
                return templates.TemplateResponse(
                    "components/gear_details.html",
                    {"request": req, "gear": g},
                    headers={"HX-Trigger": f"reload-needs-{g.player_id}"},
                )
            raise HTTPException(HTTP_404_NOT_FOUND)


class Players(HTTPEndpoint):
    async def get(self, req: Request):
        if (
            p := await Player.filter(id=req.query_params["player_id"])
            .prefetch_related("gearset")
            .first()
        ):
            return templates.TemplateResponse(
                "pages/player.html", {"request": req, "player": p}
            )
        raise HTTPException(HTTP_404_NOT_FOUND)

    async def post(self, req: Request):
        async with req.form() as data:
            p = Player(group_id=data["group_id"])

            # TODO: database failure handling
            await p.save()
            await Gear.bulk_create([Gear(slot=s, player=p) for s in Slot])
            await p.fetch_related("gearset")

            return templates.TemplateResponse(
                "partials/player.html", {"request": req, "player": p}
            )

    async def patch(self, req: Request):
        async with req.form() as data:
            data = dict(data)
            p_id = str(data.pop("player_id"))

            # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
            q = Player.filter(id=p_id).update(**data).sql() + " RETURNING *"
            async with in_transaction() as conn:
                r = (await conn.execute_query_dict(q, list(data.values())))[0]

            if r:
                p = Player(**r)  # hydrate from raw cursor
                return templates.TemplateResponse(
                    "components/player_details.html", {"request": req, "player": p}
                )
            raise HTTPException(HTTP_404_NOT_FOUND)


async def needs(req: Request):
    if (
        p := await Player.filter(id=req.query_params["player_id"])
        .prefetch_related("gearset")
        .first()
    ):
        return templates.TemplateResponse(
            "components/player_needs.html", {"request": req, "player": p}
        )
    raise HTTPException(HTTP_404_NOT_FOUND)


class Groups(HTTPEndpoint):
    async def get(self, req: Request):
        if (
            g := await Group.filter(id=req.query_params["group_id"])
            .prefetch_related("players", "players__gearset")
            .first()
        ):
            return templates.TemplateResponse(
                "pages/group.html", {"request": req, "group": g}
            )
        raise HTTPException(HTTP_404_NOT_FOUND)

    async def post(self, req: Request):
        g = Group()
        # TODO: handle database failures
        await g.save()
        return RedirectResponse(
            f'{req.url_for("groups")}?group_id={g.id}',
            status_code=HTTP_303_SEE_OTHER,
        )

    async def patch(self, req: Request):
        async with req.form() as data:
            data = dict(data)
            g_id = data.pop("group_id")

            # scuffed RETURNING, see https://github.com/tortoise/tortoise-orm/pull/1357
            q = Group.filter(id=g_id).update(**data).sql() + " RETURNING *"
            async with in_transaction() as conn:
                r = (await conn.execute_query_dict(q, list(data.values())))[0]

            if r:
                g = Group(**r)  # hydrate from raw cursor
                return templates.TemplateResponse(
                    "components/group_details.html", {"request": req, "group": g}
                )
            raise HTTPException(HTTP_404_NOT_FOUND)


async def test(req: Request):
    return HTMLResponse("<p>test</p>")


@asynccontextmanager
async def lifespan(app: Starlette):
    await Tortoise.init(db_url=DATABASE_URL, modules={"app": ["database"]})
    await Tortoise.generate_schemas()
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
        Route("/groups", Groups, name="groups"),
        Route("/players", Players, name="players"),
        Route("/gears", Gears, name="gears"),
        Route("/needs", needs, name="needs"),
        Route("/", index),
    ],
)
