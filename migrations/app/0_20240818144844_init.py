from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "groups" (
    "name" VARCHAR(64) NOT NULL  DEFAULT '',
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(64) NOT NULL  DEFAULT '',
    "tier" SMALLINT NOT NULL  DEFAULT 1
);
CREATE TABLE IF NOT EXISTS "players" (
    "name" VARCHAR(64) NOT NULL  DEFAULT '',
    "id" SERIAL NOT NULL PRIMARY KEY,
    "job" VARCHAR(6) NOT NULL  DEFAULT 'Tank',
    "books_1" SMALLINT NOT NULL  DEFAULT 0,
    "books_2" SMALLINT NOT NULL  DEFAULT 0,
    "books_3" SMALLINT NOT NULL  DEFAULT 0,
    "books_4" SMALLINT NOT NULL  DEFAULT 0,
    "group_id" INT NOT NULL REFERENCES "groups" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "players"."job" IS 'TANK: Tank\nHEALER: Healer\nMELEE: Melee\nRANGED: Ranged\nCASTER: Caster\nPLD: PLD\nWAR: WAR\nDRK: DRK\nGNB: GNB\nDRG: DRG\nRPR: RPR\nMNK: MNK\nSAM: SAM\nNIN: NIN\nVPR: VPR\nBRD: BRD\nMCH: MCH\nDNC: DNC\nBLM: BLM\nSMN: SMN\nRDM: RDM\nPCT: PCT\nWHM: WHM\nSCH: SCH\nAST: AST\nSGE: SGE';
CREATE TABLE IF NOT EXISTS "gears" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slot" VARCHAR(1) NOT NULL,
    "desired" VARCHAR(8) NOT NULL  DEFAULT 'Previous',
    "current" VARCHAR(8) NOT NULL  DEFAULT 'Previous',
    "player_id" INT NOT NULL REFERENCES "players" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_gears_slot_927769" ON "gears" ("slot");
COMMENT ON COLUMN "gears"."slot" IS 'WEAPON: ⚔\nHEAD: 🎩\nBODY: 🥼\nHANDS: 🧤\nLEGS: 🦵\nFEET: 👢\nEARRINGS: 👂\nNECKLACE: 👔\nBRACELETS: ✋\nRING_1: 💍\nRING_2: ⭕';
COMMENT ON COLUMN "gears"."desired" IS 'SAVAGE: Savage\nTOME_UP: Tome Up\nCATCHUP: Catch-up\nTOME: Tome\nRELIC: Relic\nEXTREME: Extreme\nCRAFTED: Crafted\nNORMAL: Normal\nPREVIOUS: Previous';
COMMENT ON COLUMN "gears"."current" IS 'SAVAGE: Savage\nTOME_UP: Tome Up\nCATCHUP: Catch-up\nTOME: Tome\nRELIC: Relic\nEXTREME: Extreme\nCRAFTED: Crafted\nNORMAL: Normal\nPREVIOUS: Previous';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
