from enum import ReprEnum

from tortoise.fields import (
    CharEnumField,
    CharField,
    ForeignKeyField,
    ForeignKeyRelation,
    ReverseRelation,
    IntField,
    SmallIntField,
)
from tortoise.models import Model


class Job(str, ReprEnum):
    TANK = "Tank"
    HEALER = "Healer"
    MELEE = "Melee"
    RANGED = "Ranged"
    CASTER = "Caster"
    PLD = "PLD"
    WAR = "WAR"
    DRK = "DRK"
    GNB = "GNB"
    DRG = "DRG"
    RPR = "RPR"
    MNK = "MNK"
    SAM = "SAM"
    NIN = "NIN"
    VPR = "VPR"
    BRD = "BRD"
    MCH = "MCH"
    DNC = "DNC"
    BLM = "BLM"
    SMN = "SMN"
    RDM = "RDM"
    PCT = "PCT"
    WHM = "WHM"
    SCH = "SCH"
    AST = "AST"
    SGE = "SGE"


class Slot(str, ReprEnum):
    WEAPON = "⚔"
    # SHIELD = "🛡"
    HEAD = "🎩"
    BODY = "🥼"
    HANDS = "🧤"
    LEGS = "🦵"
    FEET = "👢"
    EARRINGS = "👂"
    NECKLACE = "👔"
    BRACELETS = "✋"
    RING_1 = "💍"
    RING_2 = "⭕"


class Quality(str, ReprEnum):
    # SAVAGE_WEAPON = "Savage Wep"
    SAVAGE = "Savage"
    TOME_UP = "Tome Up"
    CATCHUP = "Catch-up"
    TOME = "Tome"
    RELIC = "Relic"
    EXTREME = "Extreme"
    CRAFTED = "Crafted"
    NORMAL = "Normal"
    PREVIOUS = "Previous"


needs_color_mapping = {
    Quality.SAVAGE: "bg-purple-200",
    Quality.TOME_UP: "bg-blue-200",
    Quality.CATCHUP: "bg-green-200",
    Quality.TOME: "bg-blue-300",
    Quality.RELIC: "bg-purple-300",
    Quality.EXTREME: "bg-blue-400",
    Quality.CRAFTED: "bg-green-300",
    Quality.NORMAL: "bg-orange-200",
    Quality.PREVIOUS: "bg-orange-300",
}


class UpgradeItem(str, ReprEnum):
    SHINE = "✨"
    TWINE = "🧵"
    SOLVENT = "🧪"
    TOMESTONE = "📱"


class IntIdBase(Model):
    id = IntField(pk=True)

    class Meta:
        abstract = True


class NameMixin:
    name = CharField(64, default="")


class Group(NameMixin, IntIdBase):
    description = CharField(64, default="")

    players: ReverseRelation["Player"]

    def __str__(self) -> str:
        return f"<Group {self.id}>"

    class Meta:
        table = "groups"


class Player(NameMixin, IntIdBase):
    group: ForeignKeyRelation[Group] = ForeignKeyField("app.Group", related_name="players")
    job = CharEnumField(Job, default=Job.TANK)
    books_1 = SmallIntField(default=0)
    books_2 = SmallIntField(default=0)
    books_3 = SmallIntField(default=0)
    books_4 = SmallIntField(default=0)

    gearset: ReverseRelation["Gear"]

    def __str__(self) -> str:
        return f"<Player {self.name} ({self.job})>"

    class Meta:
        table = "players"

    def needed_items(self) -> dict:
        # async def needed_items(self) -> dict:
        r = {
            1: {"gear": [], "upgrades": []},
            2: {"gear": [], "upgrades": []},
            3: {"gear": [], "upgrades": []},
            4: {"gear": [], "upgrades": []},
        }
        # if not self.gearset._fetched:
        #     await self.fetch_related("gearset")
        for s in self.gearset:
            if s.current != s.desired:
                if s.desired == Quality.SAVAGE:
                    match s.slot:
                        case Slot.EARRINGS | Slot.NECKLACE | Slot.BRACELETS | Slot.RING_1 | Slot.RING_2:
                            turn = 1
                        case Slot.HEAD | Slot.HANDS | Slot.FEET:
                            turn = 2
                        case Slot.LEGS | Slot.BODY:
                            turn = 3
                        case Slot.WEAPON:
                            turn = 4
                    r[turn]["gear"].append(s.slot)
                elif s.desired == Quality.TOME_UP:
                    match s.slot:
                        case Slot.EARRINGS | Slot.NECKLACE | Slot.BRACELETS | Slot.RING_1 | Slot.RING_2:
                            r[2]["upgrades"].append(UpgradeItem.SHINE)
                        case Slot.HEAD | Slot.HANDS | Slot.FEET | Slot.LEGS | Slot.BODY:
                            r[3]["upgrades"].append(UpgradeItem.TWINE)
                        case Slot.WEAPON:
                            if s.current != Quality.TOME:
                                r[2]["upgrades"].append(UpgradeItem.TOMESTONE)
                            r[3]["upgrades"].append(UpgradeItem.SOLVENT)
        return r


class Gear(IntIdBase):
    player: ForeignKeyRelation[Player] = ForeignKeyField("app.Player", related_name="gearset")
    slot = CharEnumField(Slot, index=True)
    desired = CharEnumField(Quality, default=Quality.PREVIOUS)
    current = CharEnumField(Quality, default=Quality.PREVIOUS)

    player_id: IntField

    def __str__(self) -> str:
        return f"<Gear {self.slot} ({self.desired} ⇐ {self.current})>"

    class Meta:
        table = "gears"
