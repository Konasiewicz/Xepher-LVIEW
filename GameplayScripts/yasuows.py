from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math

winstealer_script_info = {
    "script": "WS+ Yasuo",
    "author": "bckd00r",
    "description": "WS+ Yasuo",
    "target_champ": "yasuo",
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

q = {"Range": 450}
w = {"Range": 2500.0}
e = {"Range": 475}
r = {"Range": 1800}


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

    ui.begin("WS+ Yasuo")
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


def GetClosestMobToEnemyForGap(game):
    closestMinionDistance = float("inf")
    closestMinion = None
    enemy = GetBestTargetsInRange(game, 1500)
    if enemy:
        for minion in game.minions:
            if (
                minion
                and ValidTarget(minion)
                and game.is_point_on_screen(minion.pos)
                and minion.pos.distance(game.player.pos) <= 475
                and not getBuff(minion, "yasuoe")
            ):
                if minion.pos.distance(enemy.pos) <= e[
                    "Range"
                ] and not IsUnderTurretEnemy(game, minion):
                    minionDistanceToMouse = minion.pos.distance(enemy.pos)
                    if minionDistanceToMouse <= closestMinionDistance:
                        closestMinion = minion
                        closestMinionDistance = minionDistanceToMouse
    return closestMinion


def QDamage(game, target):
    damage = 0
    if game.player.Q.level == 1:
        damage = 20 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 2:
        damage = 45 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 3:
        damage = 70 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 4:
        damage = 95 + (get_onhit_physical(game.player, target))
    elif game.player.Q.level == 5:
        damage = 120 + (get_onhit_physical(game.player, target))
    return damage


def EDamage(game, target):
    damage = 0
    if game.player.E.level == 1:
        damage = 60 + (get_onhit_magical(game.player, target))
    elif game.player.E.level == 2:
        damage = 70 + (get_onhit_magical(game.player, target))
    elif game.player.E.level == 3:
        damage = 80 + (get_onhit_magical(game.player, target))
    elif game.player.E.level == 4:
        damage = 90 + (get_onhit_magical(game.player, target))
    elif game.player.E.level == 5:
        damage = 100 + (get_onhit_magical(game.player, target))
    return damage


def RDamage(game, target):
    damage = 0
    if game.player.R.level == 1:
        damage = 200 + (get_onhit_physical(game.player, target))
    elif game.player.R.level == 2:
        damage = 350 + (get_onhit_physical(game.player, target))
    elif game.player.R.level == 3:
        damage = 500 + (get_onhit_physical(game.player, target))
    return damage


lastW = 0


def Evade(game):
    global e, lastW
    e_spell = getSkill(game, "E")
    w_spell = getSkill(game, "W")
    for missile in game.missiles:
        br = game.player.gameplay_radius
        if not game.player.is_alive or missile.is_ally_to(game.player):
            continue
        if not is_skillshot(missile.name):
            continue
        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue
        if InSkillShot(
            game, game.player.pos, missile, spell, game.player.gameplay_radius * 2
        ) and game.is_point_on_screen(missile.pos):
            minion = GetBestMinionsInRange(game, e["Range"]) or GetBestJungleInRange(
                game, e["Range"]
            )
            if (
                minion
                and not InSkillShot(
                    game, minion.pos, missile, spell, minion.gameplay_radius * 2
                )
                and game.is_point_on_screen(missile.pos)
                and not IsUnderTurretEnemy(game, minion)
            ):
                if getBuff(minion, "yasuoe"):
                    continue
                if not IsDanger(game, minion.pos):
                    e_spell.move_and_trigger(game.world_to_screen(minion.pos))
            elif IsReady(game, w_spell) and lastW + 1 < game.time:
                w_spell.move_and_trigger(game.world_to_screen(missile.pos))


lastE = 0
lastQ = 0
lastR = 0


def Combo(game):
    global q, e, r
    global lastE, lastQ, lastR
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    if (
        use_q_in_combo
        and lastQ + 0.2 < game.time
        and IsReady(game, q_spell)
        and q_spell.name == "yasuoq3wrapper"
    ):
        target = GetBestTargetsInRange(game, 1060)
        if target:
            lastQ = game.time
            q_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, q_spell, game.player, target)
                )
            )
    if use_q_in_combo and lastQ + 0.2 < game.time and IsReady(game, q_spell):
        target = GetBestTargetsInRange(game, q["Range"])
        if target:
            lastQ = game.time
            q_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, q_spell, game.player, target)
                )
            )
    if (
        use_e_in_combo
        and lastE + 0.3 < game.time
        and IsReady(game, e_spell)
        and IsReady(game, q_spell)
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if (
            target
            and not getBuff(target, "yasuoe")
            and not IsUnderTurretEnemy(game, target)
        ):
            lastE = game.time
            e_spell.move_and_trigger(game.world_to_screen(target.pos))
            q_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, q_spell, game.player, target)
                )
            )
            game.press_key(61)
    if use_r_in_combo and lastR + 1 < game.time and IsReady(game, r_spell):
        target = GetBestTargetsInRange(game, r["Range"])
        minion = GetBestMinionsInRange(game, e["Range"])
        if target:
            if IsKnock(game, target):
                if minion:
                    lastQ = game.time
                    lastE = game.time
                    e_spell.move_and_trigger(game.world_to_screen(minion.pos))
                    q_spell.move_and_trigger(game.world_to_screen(minion.pos))
                lastR = game.time
                r_spell.trigger(False)
    if use_e_in_combo and lastE + 0.3 < game.time and IsReady(game, e_spell):
        target = GetBestTargetsInRange(game, 1800)
        if target and not getBuff(target, "yasuoe"):
            minion = GetClosestMobToEnemyForGap(game)
            if minion:
                lastE = game.time
                e_spell.move_and_trigger(game.world_to_screen(minion.pos))


def Harass(game):
    global q, e, r
    global lastE, lastQ, lastR
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    if (
        use_e_in_combo
        and lastE + 0.5 < game.time
        and IsReady(game, e_spell)
        and IsReady(game, q_spell)
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if target and not buffIsAlive(game, getBuff(target, "yasuoe")):
            turret = GetBestTurretInRange(game, target.gameplay_radius * 2)
            if turret:
                return
            lastE = game.time
            e_spell.move_and_trigger(game.world_to_screen(target.pos))
            q_spell.move_and_trigger(game.world_to_screen(target.pos))
    if use_e_in_combo and lastE + 0.5 < game.time and IsReady(game, e_spell):
        target = GetBestTargetsInRange(game, r["Range"])
        if target:
            if target.pos.distance(game.player.pos) > q["Range"]:
                minion = GetClosestMobToEnemyForGap(game)
                if (
                    minion
                    and game.distance(minion, target) < e["Range"]
                    and not IsUnderTurretEnemy(game, minion)
                ):
                    lastE = game.time
                    e_spell.move_and_trigger(game.world_to_screen(minion.pos))
    if use_q_in_combo and IsReady(game, q_spell):
        target = GetBestTargetsInRange(game, q["Range"])
        if target:
            q_spell.move_and_trigger(game.world_to_screen(target.pos))


def Laneclear(game):
    global q, e, r
    global lastE, lastQ, lastR
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    if (
        lane_clear_with_q
        and IsReady(game, q_spell)
        and q_spell.name == "yasuoq3wrapper"
    ):
        minion = GetBestMinionsInRange(game, 1060) or GetBestJungleInRange(
            game, e["Range"]
        )
        if minion:
            q_spell.move_and_trigger(game.world_to_screen(minion.pos))
    if lane_clear_with_q and lastQ + 1 < game.time and IsReady(game, q_spell):
        minion = GetBestMinionsInRange(game, q["Range"]) or GetBestJungleInRange(
            game, e["Range"]
        )
        if minion:
            lastQ = game.time
            q_spell.move_and_trigger(game.world_to_screen(minion.pos))
    if lane_clear_with_e and lastE + 0.5 < game.time and IsReady(game, e_spell):
        minion = GetBestMinionsInRange(game, e["Range"]) or GetBestJungleInRange(
            game, e["Range"]
        )
        if (
            minion
            and EDamage(game, minion) >= minion.health
            and not IsUnderTurretEnemy(game, minion)
        ):
            e_spell.move_and_trigger(game.world_to_screen(minion.pos))
            lastE = game.time
    if (
        lane_clear_with_eq
        and lastE + 0.5 < game.time
        and IsReady(game, e_spell)
        and IsReady(game, q_spell)
    ):
        minion = GetBestMinionsInRange(game, e["Range"]) or GetBestJungleInRange(
            game, e["Range"]
        )
        if (
            minion
            and (
                EDamage(game, minion) >= minion.health
                or QDamage(game, minion) >= minion.health
            )
            and not IsUnderTurretEnemy(game, minion)
        ):
            e_spell.move_and_trigger(game.world_to_screen(minion.pos))
            q_spell.move_and_trigger(game.world_to_screen(minion.pos))


def winstealer_update(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lasthit_with_q, lane_clear_with_eq, lane_clear_with_e
    global use_w_on_evade

    self = game.player

    if self.is_alive and game.is_point_on_screen(self.pos) and not game.isChatOpen:
        if draw_q_range:
            game.draw_circle_world(game.player.pos, q["Range"], 100, 2, Color.WHITE)
        if draw_e_range:
            game.draw_circle_world(game.player.pos, e["Range"], 100, 2, Color.WHITE)
        if draw_r_range:
            game.draw_circle_world(game.player.pos, r["Range"], 100, 2, Color.WHITE)

        if game.is_key_down(combo_key):
            Combo(game)
        if game.is_key_down(laneclear_key):
            Laneclear(game)
        if game.is_key_down(harass_key):
            Harass(game)
        if use_w_on_evade:
            Evade(game)
