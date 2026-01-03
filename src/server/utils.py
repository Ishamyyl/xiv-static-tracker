from enum import ReprEnum


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


class UpgradeItem(str, ReprEnum):
    SHINE = "✨"
    TWINE = "🧵"
    SOLVENT = "🧪"
    TOMESTONE = "📱"
