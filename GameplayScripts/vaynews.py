from winstealer import *
from commons.items import *
from commons.targeting import *
from commons.utils import *
import json, time, math


winstealer_script_info = {
    "script": "WS+ Vayne",
    "author": "bckd00r",
    "description": "WS+ Vayne",
    "target_champ": "vayne",
}

lastQ = 0
lastE = 0

combo_key = 57
harass_key = 46

use_q_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

randomize_q_pos = True

anti_gap_q = True
anti_gap_e = True

use_q_on_evade = False

draw_q_range = False
draw_e_range = False

MaxRCountForUse = 0

e_range = 475

q = {"Range": 325}
e = {"Speed": 999, "Range": 650, "delay": 0.75, "radius": 120}


use_q_with_harass = True
use_e_with_harass = False


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range
    global randomize_q_pos
    global MaxRCountForUse
    global use_q_with_harass, use_e_with_harass
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    use_q_with_harass = cfg.get_bool("use_q_with_harass", True)
    use_e_with_harass = cfg.get_bool("use_e_with_harass", False)

    randomize_q_pos = cfg.get_bool("randomize_q_pos", True)

    anti_gap_q = cfg.get_bool("anti_gap_q", True)
    anti_gap_e = cfg.get_bool("anti_gap_e", True)

    use_q_on_evade = cfg.get_bool("use_q_on_evade", False)

    e_range = cfg.get_int("e_range", 475)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)

    MaxRCountForUse = cfg.get_float("MaxRCountForUse", 1)


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range
    global randomize_q_pos
    global MaxRCountForUse
    global use_q_with_harass, use_e_with_harass

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("use_q_with_harass", use_q_with_harass)
    cfg.set_bool("use_e_with_harass", use_e_with_harass)

    cfg.set_bool("randomize_q_pos", randomize_q_pos)

    cfg.set_bool("anti_gap_q", anti_gap_q)
    cfg.set_bool("anti_gap_e", anti_gap_e)

    cfg.set_bool("use_q_on_evade", use_q_on_evade)

    cfg.set_int("e_range", e_range)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_e_range", draw_e_range)

    cfg.set_float("MaxRCountForUse", MaxRCountForUse)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    global anti_gap_q, anti_gap_e, use_q_on_evade
    global e_range
    global randomize_q_pos
    global MaxRCountForUse
    global use_q_with_harass, use_e_with_harass

    ui.begin("WS+ Vayne")
    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)

    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        randomize_q_pos = ui.checkbox("[Q] Randomize pos", randomize_q_pos)
        use_q_with_harass = ui.checkbox("Use Q with Harass", use_q_with_harass)
        use_q_on_evade = ui.checkbox("Use Q on Evade", use_q_on_evade)
        anti_gap_q = ui.checkbox("[Q] Anti-Gap closer", anti_gap_q)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        e_range = ui.dragfloat("[E] Range", e_range, 10, 100, 475)
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        use_e_with_harass = ui.checkbox("Use E with Harass", use_e_with_harass)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        anti_gap_e = ui.checkbox("[E] Anti-Gap closer", anti_gap_e)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        MaxRCountForUse = ui.sliderint(
            "Max targets use for R", MaxRCountForUse, 1, 1, 5
        )
        ui.treepop()

    ui.end()


def CheckWallStun(game, unit, PredictedE):
    global e_range
    PredictedPos = unit.pos
    Direction = PredictedPos.sub(game.player.pos)
    if PredictedE == True:
        # Time = (mesafe(unit.pos, game.player.pos) / 2000) + 0.25
        PredictedPos = unit.pos
        Direction = PredictedPos.sub(game.player.pos)
    for i in range(1, 11):
        ESpot = PredictedPos.add(Direction.normalize().scale(40 * i))
        game.draw_line(
            game.world_to_screen(unit.pos), game.world_to_screen(ESpot), 1, Color.GREEN
        )
        if SRinWall(game, ESpot):
            return ESpot
    return None


# def Evade(game):
#     global lastQ
#     q_spell = getSkill(game, 'Q')
#     for missile in game.missiles:
#         end_pos = missile.end_pos.clone()
#         start_pos = missile.start_pos.clone()
#         curr_pos = missile.pos.clone()
#         bounding = game.player.gameplay_radius
#         if not game.player.is_alive or missile.is_ally_to(game.player):
#             continue
#         if not is_skillshot(missile.name):
#             continue
#         spell = get_missile_parent_spell(missile.name)
#         if not spell:
#             continue
#         if (
#             game.point_on_line(
#                 game.world_to_screen(start_pos),
#                 game.world_to_screen(end_pos),
#                 game.world_to_screen(game.player.pos),
#                 bounding,
#             )
#             and game.is_point_on_screen(curr_pos)
#         ):
#             pos = getEvadePos(game, game.player.pos, bounding, missile, spell)
#             if pos:
#                 if IsReady(game, q_spell) and lastQ + 2 < game.time and GetDistanceSqr(pos, game.player.pos) < 600 * 600 and not IsDanger(game, pos):
#                     q_spell.move_and_trigger(game.world_to_screen(pos))

RTargetCount = 0


def getCountR(game, dist):
    global RTargetCount, MaxRCountForUse
    RTargetCount = 0
    for champ in game.champs:
        if (
            champ
            and champ.is_visible
            and champ.is_enemy_to(game.player)
            and champ.isTargetable
            and champ.is_alive
            and game.is_point_on_screen(champ.pos)
            and game.distance(game.player, champ) < dist
        ):
            RTargetCount = RTargetCount + 1
    if int(RTargetCount) >= MaxRCountForUse:
        return True
    else:
        return False


def Combo(game):
    global lastQ, lastE
    global e_range
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    isPressE = False

    g_time = game.time
    if (
        use_r_in_combo
        and getCountR(game, game.player.atkRange)
        and IsReady(game, r_spell)
        and game.player.mana > 80
    ):
        target = GetBestTargetsInRange(game)
        if target:
            r_spell.trigger(False)
    if (
        use_q_in_combo
        # and lastQ + 2 < g_time
        and not getBuff(game.player, "vaynetumblebonus")
        and IsReady(game, q_spell)
        and game.player.mana > 30
    ):
        target = GetBestTargetsInRange(game)
        if (
            target
            and game.get_cursor().distance(game.world_to_screen(target.pos)) < 250
        ):
            lastQ = game.time
            kitePos = GetKitePosition(game, target)
            if randomize_q_pos:
                q_spell.move_and_trigger(game.world_to_screen(kitePos))
            else:
                q_spell.trigger(False)
    if (
        use_e_in_combo
        and lastE + 1 < g_time
        and IsReady(game, e_spell)
        and game.player.mana > 90
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if target:
            # for buff in target.buffs:
            #     if buff.name == "VayneSilveredDebuff" and buff.countAlt > 1:
            #         isPressE = True
            if CheckWallStun(game, target, True):
                lastE = game.time
                e_spell.move_and_trigger(game.world_to_screen(target.pos))


def Harass(game):
    global use_q_with_harass, use_e_with_harass
    global lastQ, lastE
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")

    if (
        use_q_with_harass
        and lastQ + 2 < game.time
        and IsReady(game, q_spell)
        and game.player.mana > 30
    ):
        target = GetBestTargetsInRange(game)
        if target:
            lastQ = game.time
            q_spell.move_and_trigger(game.world_to_screen(target.pos))
    if (
        use_e_with_harass
        and lastE < game.time
        and IsReady(game, e_spell)
        and game.player.mana > 90
    ):
        if CheckWallStun(game, target, True):
            lastE = game.time
            e_spell.move_and_trigger(game.world_to_screen(target.pos))


def AntiGap(game):
    global anti_gap_q, anti_gap_e
    global lastQ, lastE
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    target = GetBestTargetsInRange(game, 375)
    if target and target.atkRange < 375:
        if (
            anti_gap_e
            and lastE + 1 < game.time
            and IsReady(game, e_spell)
            and game.player.mana > 90
        ):
            lastE = game.time
            e_spell.move_and_trigger(game.world_to_screen(target.pos))
        # if (
        #     anti_gap_q
        #     and lastQ + 2 < game.time
        #     and IsReady(game, q_spell)
        #     and game.player.mana > 30
        # ):
        #     kitePos = GetKitePosition(game, target)
        #     lastQ = game.time
        #     q_spell.move_and_trigger(game.world_to_screen(kitePos))


def winstealer_update(game, ui):
    global draw_q_range, draw_e_range
    global combo_key, harass_key
    self = game.player

    if self.is_alive and game.is_point_on_screen(self.pos) and not game.isChatOpen:
        if draw_q_range:
            game.draw_circle_world(game.player.pos, q["Range"], 100, 2, Color.WHITE)
        if draw_e_range:
            game.draw_circle_world(game.player.pos, e["Range"], 100, 2, Color.WHITE)

        game.draw_circle(game.get_cursor(), 250, 10, 2, Color.GREEN)

        target = GetBestTargetsInRange(game, e["Range"])
        if target:
            CheckWallStun(game, target, True)

        if anti_gap_e and anti_gap_q:
            AntiGap(game)

        # if use_q_on_evade:
        #     Evade(game)

        if game.is_key_down(combo_key):
            Combo(game)
        if game.is_key_down(harass_key):
            Harass(game)
