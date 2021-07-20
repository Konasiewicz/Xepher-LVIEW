from winstealer import *
from commons.skills import *
from commons.items import *
from commons.utils import *
import commons.damage_calculator as damage_calculator

supportedChampions = {
    "Ashe": [
        {
            "name": "EnchantedCrystalArrow",
            "missileName": "EnchantedCrystalArrow",
            "range": 25000,
            "speed": 1600,
            "delay": 0.25,
            "width": 125,
            "radius": 0,
            "slot": "R",
            "block": ["hero"],
        },
    ],
    "Corki": [
        {
            "name": "MissileBarrageMissile",
            "missileName": "MissileBarrageMissile",
            "range": 1225,
            "speed": 1950,
            "delay": 0.175,
            "width": 37.5,
            "radius": 75,
            "slot": "R",
            "block": ["hero", "minion"],
        },
        {
            "name": "MissileBarrageMissile2",
            "missileName": "MissileBarrageMissile2",
            "range": 1225,
            "speed": 1950,
            "delay": 0.175,
            "width": 75,
            "radius": 150,
            "slot": "R",
            "block": ["hero", "minion"],
        },
    ],
    "Draven": [
        {
            "name": "DravenRCast",
            "missileName": "DravenR",
            "range": 25000,
            "speed": 2000,
            "delay": 0.5,
            "width": 65,
            "radius": 130,
            "slot": "R",
            "block": [],
        },
    ],
    "Ezreal": [
        {
            "name": "EzrealTrueshotBarrage",
            "missileName": "EzrealTrueshotBarrage",
            "range": 25000,
            "speed": 2000,
            "delay": 1,
            "width": 80,
            "radius": 160,
            "slot": "R",
            "damage": [350, 500, 650],
            "block": [],
        },
    ],
    "Fizz": [
        {
            "name": "FizzR",
            "missileName": "FizzRMissile",
            "range": 1300,
            "speed": 1300,
            "delay": 0.25,
            "width": 60,
            "radius": 120,
            "slot": "R",
            "block": ["hero"],
        },
    ],
    "Jinx": [
        {
            "name": "JinxR",
            "missileName": "JinxR",
            "range": 25000,
            "speed": 1700,
            "maxSpeed": 2500,
            "delay": 0.6,
            "width": 112.5,
            "radius": 225,
            "slot": "R",
            "block": ["hero"],
            "damage": [200, 400, 550],
        },
    ],
    "MissFortune": [
        {
            "name": "MissFortuneBulletTime",
            "range": 1400,
            "speed": 0,
            "delay": 0.1,
            "width": 0,
            "radius": 0,
            "slot": "R",
            "block": [],
        },
    ],
    "Nami": [
        {
            "name": "NamiR",
            "missileName": "NamiRMissile",
            "range": 2750,
            "speed": 850,
            "delay": 0.5,
            "width": 107.5,
            "radius": 215,
            "slot": "R",
            "block": [],
        },
    ],
    "Nidalee": [
        {
            "name": "JavelinToss",
            "missileName": "JavelinToss",
            "range": 1500,
            "speed": 1300,
            "delay": 0.25,
            "width": 20,
            "radius": 0,
            "slot": "W",
            "block": ["hero", "minion"],
        },
    ],
    "Varus": [
        {
            "name": "VarusQ",
            "missileName": "VarusQMissile",
            "range": 1625,
            "speed": 1850,
            "delay": 0.25,
            "width": 20,
            "radius": 40,
            "slot": "Q",
            "block": [],
        },
    ],
}

enemyBasePos = None

winstealer_script_info = {
    "script": "WS+ Baseult",
    "author": "bckd00r",
    "description": "Not very good...",
}


def winstealer_load_cfg(cfg):
    pass


def winstealer_save_cfg(cfg):
    pass


def winstealer_draw_settings(game, ui):
    global supportedChampions
    if game.player.name.capitalize() not in supportedChampions:
        ui.text(
            game.player.name.upper() + " not baseult",
            Color.RED,
        )
    else:
        ui.text(
            game.player.name.upper() + " yes",
            Color.GREEN,
        )


def getEnemyBase(game):
    redBase = Vec3(14355.25, 171.0, 14386.00)
    blueBase = Vec3(414.0, 183.0, 420.0)
    base = None
    for turret in game.turrets:
        if turret.is_enemy_to(game.player) and turret.has_tags(
            UnitTag.Unit_Structure_Turret_Shrine
        ):
            if turret.pos.distance(redBase) <= 600:
                base = redBase
            else:
                base = blueBase
    return base


def calcTravelTimeToBase(game, unit, spell):
    player = supportedChampions.get(game.player.name.capitalize())
    base = getEnemyBase(game)
    dist = unit.pos.distance(base)
    speed = player[0]["speed"]
    delay = player[0]["delay"] + 0.1
    if speed == math.inf and delay != 0:
        return delay
    # if dist > player[0]["range"]:
    #     return 0
    # if speed == 0:
    #     return delay
    print("yes")
    if game.player.name == "jinx" and dist > 1350:
        accelerationrate = 0.3
        acceldifference = dist - 1350
        if acceldifference > 150:
            acceldifference = 150
        difference = dist - 1700
        speed = (
            1350 * speed
            + acceldifference * (speed + accelerationrate * acceldifference)
            + difference * 2700
        ) / dist
    # if player[0]["maxSpeed"]:
    #     return (dist - speed) / player[0]["maxSpeed"] + delay + 1
    time = dist / speed + delay

    return time


lastR = 0


def winstealer_update(game, ui):
    global lastR, supportedChampions
    if game.player.name.capitalize() not in supportedChampions:
        return
    if game.player.is_alive:
        ch = supportedChampions.get(game.player.name.capitalize())
        base = getEnemyBase(game)
        cp = game.player.pos.sub(game.player.pos.sub(base).normalize().scale(300))
        # game.draw_line(
        #     game.world_to_screen(game.player.pos),
        #     game.world_to_screen(cp),
        #     1,
        #     Color.GREEN,
        # )
        for champ in game.champs:
            if champ.is_alive and champ.is_enemy_to(game.player):
                buff = getBuff(champ, "recall")
                if buff:
                    r_spell = getSkill(game, "R")
                    if IsReady(game, r_spell) and game.player.mana > 100:
                        recallTime = int(buff.end_time - game.time)
                        hitTime = calcTravelTimeToBase(game, champ, r_spell)
                        if (
                            hitTime - recallTime >= 0.05
                            and (
                                ch[0]["damage"][game.player.R.level - 1]
                                + get_onhit_physical(game.player, champ)
                            )
                            >= champ.health + (champ.health_regen * 10) + champ.armour
                        ) and lastR + 1 < game.time:
                            r_spell.move_and_trigger(game.world_to_minimap(base))
                            lastR = game.time
