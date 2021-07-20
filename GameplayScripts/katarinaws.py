from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math

winstealer_script_info = {
    "script": "WS+ Katarina",
    "author": "bckd00r",
    "description": "WS+ Katarina",
    "target_champ": "katarina",
}

combo_key = 57
harass_key = 45
laneclear_key = 47
killsteal_key = 46

use_q_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

use_w_on_evade = True

steal_kill_with_q = False
steal_kill_with_e = False
steal_kill_with_r = False

lane_clear_with_q = False
lasthit_with_q = False
lane_clear_with_eq = False
lane_clear_with_e = False

draw_q_range = False
draw_e_range = False
draw_r_range = False
draw_dagger_range = False

q = {"Range": 625}
w = {"Range": 2500.0}
e = {"Range": 725}
r = {"Range": 550}

lastDaggerPos = None
lastDagger = 0
Dagger = {"Radius": 225.0}
daggers = list()


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q, lane_clear_with_eq, lane_clear_with_e
    global use_w_on_evade
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    killsteal_key = cfg.get_int("killsteal_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)

    steal_kill_with_q = cfg.get_bool("steal_kill_with_q", False)
    steal_kill_with_e = cfg.get_bool("steal_kill_with_e", False)
    steal_kill_with_r = cfg.get_bool("steal_kill_with_r", False)

    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", False)
    lasthit_with_q = cfg.get_bool("lasthit_with_q", False)
    lane_clear_with_eq = cfg.get_bool("lane_clear_with_eq", False)
    lane_clear_with_e = cfg.get_bool("lane_clear_with_e", False)

    use_w_on_evade = cfg.get_bool("use_w_on_evade", False)


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q, lane_clear_with_eq, lane_clear_with_e
    global use_w_on_evade

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("killsteal_key", killsteal_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("steal_kill_with_q", steal_kill_with_q)
    cfg.set_bool("steal_kill_with_e", steal_kill_with_e)
    cfg.set_bool("steal_kill_with_r", steal_kill_with_r)

    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)
    cfg.set_bool("lasthit_with_q", lasthit_with_q)
    cfg.set_bool("lane_clear_with_eq", lane_clear_with_eq)
    cfg.set_bool("lane_clear_with_e", lane_clear_with_e)

    cfg.set_bool("use_w_on_evade", use_w_on_evade)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q, lane_clear_with_eq, lane_clear_with_e
    global use_w_on_evade

    ui.begin("WS+ Katarina")
    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    killsteal_key = ui.keyselect("Killsteal key", killsteal_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        steal_kill_with_q = ui.checkbox("Steal kill with Q", steal_kill_with_q)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_on_evade = ui.checkbox("Use W on Evade", use_w_on_evade)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        steal_kill_with_e = ui.checkbox("Steal kill with E", steal_kill_with_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        steal_kill_with_r = ui.checkbox("Steal kill with R", steal_kill_with_r)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lasthit_with_q = ui.checkbox("Lasthit with Q", lasthit_with_q)
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        lane_clear_with_eq = ui.checkbox("Lasthit with EQ", lane_clear_with_eq)
        lane_clear_with_e = ui.checkbox("Laneclear with E", lane_clear_with_e)
        ui.treepop()
    ui.end()


# def GetClosestMobToEnemyForGap(game):
#     global e
#     closestMinionDistance = 9999
#     target = GetBestTargetsInRange(game, e['Range'])
#     minion = GetBestMinionsInRange(game, e['Range'])
#     if minion:
#         turret = GetBestTurretInRange(game, minion.gameplay_radius * 2)
#         if turret:
#             return
#         if target:
#             minionDistanceToMouse = minion.pos.distance(target.pos)
#             if minion and minionDistanceToMouse < closestMinionDistance and game.player.pos.distance(target.pos) > e['Range']:
#                 return minion


# def GetClosestMobToEnemyForGap(game):
#     global e
#     closestMinionDistance = 9999
#     enemy = GetBestTargetsInRange(game, q["Range"])
#     if enemy:
#         minion = GetBestMinionsInRange(game, e["Range"])
#         if minion:
#             minionDistanceToMouse = minion.pos.distance(enemy.pos)
#             if minionDistanceToMouse < closestMinionDistance:
#                 return minion


def QDamage(game, target):
    damage = 0
    if game.player.Q.level == 1:
        damage = 75 + (get_onhit_magical(game.player, target))
    elif game.player.Q.level == 2:
        damage = 105 + (get_onhit_magical(game.player, target))
    elif game.player.Q.level == 3:
        damage = 135 + (get_onhit_magical(game.player, target))
    elif game.player.Q.level == 4:
        damage = 165 + (get_onhit_magical(game.player, target))
    elif game.player.Q.level == 5:
        damage = 195 + (get_onhit_magical(game.player, target))
    return damage


def EDamage(game, target):
    damage = 0
    if game.player.Q.level == 1:
        damage = (
            15
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 2:
        damage = (
            30
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 3:
        damage = (
            45
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 4:
        damage = (
            65
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 5:
        damage = (
            75
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    return damage


def RDamage(game, target):
    damage = 0
    if game.player.Q.level == 1:
        damage = (
            200
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 2:
        damage = (
            375
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    elif game.player.Q.level == 3:
        damage = (
            500
            + (get_onhit_physical(game.player, target))
            + (get_onhit_magical(game.player, target))
        )
    return damage


def CheckDaggers(game):
    global daggers, lastDaggerPos, lastDagger
    # daggers = list()
    for missile in game.missiles:
        if missile.name == "katarinawdaggerarc" or missile.name == "katarinaqdaggerarc":
            lastDagger = game.time
            lastDaggerPos = missile.pos
            # daggers.append({"pos": missile.pos, "last": game.time})


def Combo(game):
    global q, e, r
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    if use_e_in_combo and IsReady(game, e_spell):
        target = GetBestTargetsInRange(game, e["Range"])
        if target and EDamage(game, target) >= target.health:
            if lastDaggerPos and lastDaggerPos.distance(target.pos) <= Dagger["Radius"]:
                print(lastDaggerPos)
                e_spell.move_and_trigger(game.world_to_screen(lastDaggerPos))
            # e_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_q_in_combo and IsReady(game, q_spell):
        target = GetBestTargetsInRange(game, q["Range"])
        if target:
            q_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_r_in_combo and IsReady(game, r_spell):
        target = GetBestTargetsInRange(game, r["Range"])
        if target and RDamage(game, target) >= target.health:
            r_spell.trigger(False)


def winstealer_update(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q, lane_clear_with_eq, lane_clear_with_e
    global use_w_on_evade
    global lastDaggerPos, lastDagger, Dagger

    self = game.player

    if (
        self.is_alive
        and game.is_point_on_screen(game.player.pos)
        and not game.isChatOpen
    ):
        if draw_q_range:
            game.draw_circle_world(game.player.pos, q["Range"], 100, 2, Color.WHITE)
        if draw_e_range:
            game.draw_circle_world(game.player.pos, e["Range"], 100, 2, Color.WHITE)
        if draw_r_range:
            game.draw_circle_world(game.player.pos, r["Range"], 100, 2, Color.WHITE)

        CheckDaggers(game)

        # for dagger in daggers:
        # if dagger['last'] + 4.25 > game.time:
        if lastDagger + 4 > game.time:
            game.draw_circle_world(lastDaggerPos, Dagger["Radius"], 80, 3, Color.WHITE)

        if game.is_key_down(combo_key):
            Combo(game)
        # if use_w_on_evade:
        #     Evade(game)
