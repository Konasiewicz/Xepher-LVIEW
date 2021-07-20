from winstealer import *
from commons.skills import *
from commons.utils import *

clones = {
    "shaco": [0, False, False, "shaco_square"],
    "leblanc": [0, False, False, "leblanc_square"],
    "monkeyking": [0, False, False, "monkeyking_square"],
    "neeko": [0, False, False, "neeko_square"],
    "fiddlesticks": [0, False, False, "fiddlesticks_square"],
}


def GetBestTargetsInRange(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius
    for champ in game.champs:
        if champ.name in clones and champ.R.name == champ.D.name:
            continue
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue
        # if num < champ.health:
        #     num = champ.health
        #     target = champ
        if num >= champ.health:
            num = champ.health
            target = champ
        if IsImmobileTarget(champ):
            target = champ
        if is_last_hitable(game, game.player, champ):
            target = champ
    if target:
        return target


def GetBestMinionsInRange(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for minion in game.minions:
        if (
            not minion.is_alive
            or not minion.is_visible
            or not minion.isTargetable
            or minion.is_ally_to(game.player)
            or game.player.pos.distance(minion.pos) > atk_range
        ):
            continue
        hpPercent = minion.health / minion.max_health * 100
        if is_last_hitable(game, game.player, minion) or num >= minion.health:
            num = minion.health
            target = minion
    if target:
        return target


def GetBestJungleInRange(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for jungle in game.jungle:
        if (
            not jungle.is_alive
            or not jungle.is_visible
            or not jungle.isTargetable
            or jungle.is_ally_to(game.player)
            or game.player.pos.distance(jungle.pos) > atk_range
        ):
            continue
        if num >= jungle.health:
            num = jungle.health
            target = jungle
        if is_last_hitable(game, game.player, jungle):
            target = jungle
    return target


def GetBestTurretInRange(game, atk_range=0):
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for turret in game.turrets:
        if (
            not turret.is_alive
            or not turret.is_visible
            or not turret.isTargetable
            or turret.is_ally_to(game.player)
            or game.player.pos.distance(turret.pos) > atk_range
        ):
            continue
        return turret


def LastHitMinions(game, atk_range=0):
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for minion in game.minions:
        if (
            not minion.is_alive
            or not minion.is_visible
            or not minion.isTargetable
            or minion.is_ally_to(game.player)
            or game.player.pos.distance(minion.pos) >= atk_range
        ):
            continue
        if is_last_hitable(game, game.player, minion):
            target = minion
    return target


def GetAllyMinionsInRange(game, atk_range=0):
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for minion in game.minions:
        if (
            not minion.is_alive
            or not minion.is_visible
            or not minion.isTargetable
            or minion.is_enemy_to(game.player)
            or game.player.pos.distance(minion.pos) >= atk_range
        ):
            continue
        target = minion
    if target:
        return target


def GetAllyChampsInRange(game, atk_range=0):
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius + 25
    for champ in game.champs:
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_enemy_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue
        target = champ
    if target:
        return target
