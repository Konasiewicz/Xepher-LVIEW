from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
from evade import checkEvade
import json, time, math

winstealer_script_info = {
    "script": "WS+ Kogmaw",
    "author": "bckd00r",
    "description": "WS+ Kogmaw",
    "target_champ": "kogmaw",
}

# formula of w 610 + (20 * game.player.W.level) + game.player.gameplay_radius - 35
# formula of r damage baseRDmg = 60 + (40 * game.player.R.level) + (game.player.bonus_atk * 0.65) + (get_onhit_magical(game.player, target) * 0.25)

combo_key = 57
harass_key = 45
laneclear_key = 47
killsteal_key = 46

use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

steal_kill_with_q = False
steal_kill_with_e = False
steal_kill_with_r = False

lane_clear_with_q = False

draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

max_mana_with_r = 40

lastQ = 0
lastE = 0
lastR = 0

q = {"Range": 1175}
e = {"Range": 1280}
r = {"Range": 0}


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q
    global max_mana_with_r
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    killsteal_key = cfg.get_int("killsteal_key", 46)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)

    steal_kill_with_q = cfg.get_bool("steal_kill_with_q", False)
    steal_kill_with_e = cfg.get_bool("steal_kill_with_e", False)
    steal_kill_with_r = cfg.get_bool("steal_kill_with_r", False)

    max_mana_with_r = cfg.get_float("max_mana_with_r", 40)

    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", False)
    lasthit_with_q = cfg.get_bool("lasthit_with_q", False)


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q
    global max_mana_with_r
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("killsteal_key", killsteal_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_w_range)
    cfg.set_bool("draw_e_range", draw_e_range)
    cfg.set_bool("draw_r_range", draw_r_range)

    cfg.set_bool("steal_kill_with_q", steal_kill_with_q)
    cfg.set_bool("steal_kill_with_e", steal_kill_with_e)
    cfg.set_bool("steal_kill_with_r", steal_kill_with_r)

    cfg.set_float("max_mana_with_r", max_mana_with_r)

    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, harass_key, laneclear_key, killsteal_key
    global steal_kill_with_q, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q
    global max_mana_with_r

    ui.begin("WS+ Kogmaw")
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
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        draw_w_range = ui.checkbox("Draw W Range", draw_w_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        steal_kill_with_e = ui.checkbox("Steal kill with E", steal_kill_with_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        steal_kill_with_r = ui.checkbox("Steal kill with R", steal_kill_with_r)
        draw_r_range = ui.checkbox("Draw R Range", draw_r_range)
        max_mana_with_r = ui.sliderfloat("Minimum Mana %", max_mana_with_r, 40, 400)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        ui.treepop()
    ui.end()


def Combo(game):
    global q, e, r
    global max_mana_with_r
    global lastQ, lastE, lastR
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    e_spell = getSkill(game, "E")
    r_spell = getSkill(game, "R")

    before_cpos = game.get_cursor()

    if use_w_in_combo and game.player.mana > 40 + 40 and IsReady(game, w_spell):
        target = GetBestTargetsInRange(
            game,
            610.0
            + (20.0 * game.player.W.level)
            + game.player.gameplay_radius * 2
            - 35.0,
        )
        if target:
            w_spell.trigger(False)
    if (
        use_q_in_combo
        and game.player.mana > 40
        and IsReady(game, q_spell)
        and lastQ + 3 < game.time
    ):
        target = GetBestTargetsInRange(game, q["Range"])
        if target and not IsCollisioned(game, target):
            lastQ = game.time
            if target.isMoving:
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )
            else:
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )
    if (
        use_e_in_combo
        and game.player.mana > 120 + 40 + 40
        and IsReady(game, e_spell)
        and lastE + 1 < game.time
    ):
        target = GetBestTargetsInRange(game, e["Range"])
        if target:
            lastE = game.time
            if target.isMoving:
                e_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, e_spell, game.player, target)
                    )
                )
            else:
                e_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, e_spell, game.player, target)
                    )
                )
    if (
        use_r_in_combo
        and game.player.mana > 200 + 40
        and IsReady(game, r_spell)
        and lastR + 1.5 < game.time
    ):
        target = GetBestTargetsInRange(game, 900 + 300 * game.player.R.level)
        if target:
            baseRDmg = (
                60
                + (40 * game.player.R.level)
                + (game.player.bonus_atk * 0.65)
                + (
                    get_onhit_magical(game.player, target)
                    + get_onhit_physical(game.player, target) * 0.25
                )
            )
            if baseRDmg >= target.health:
                lastR = game.time
                if target.isMoving:
                    r_spell.move_and_trigger(
                        game.world_to_screen(
                            castpoint_for_collision(game, r_spell, game.player, target)
                        )
                    )
                else:
                    r_spell.move_and_trigger(
                        game.world_to_screen(
                            castpoint_for_collision(game, r_spell, game.player, target)
                        )
                    )


def Laneclear(game):
    global q
    global lastQ
    q_spell = getSkill(game, "Q")

    if (
        lane_clear_with_q
        and game.player.mana > 40 + 40
        and IsReady(game, q_spell)
        and lastQ + 3 < game.time
    ):
        target = GetBestMinionsInRange(game, q["Range"]) or GetBestJungleInRange(
            game, q["Range"]
        )
        if target:
            lastQ = game.time
            if target.isMoving:
                q_spell.move_and_trigger(
                    game.world_to_screen(
                        castpoint_for_collision(game, q_spell, game.player, target)
                    )
                )
            else:
                q_spell.move_and_trigger(game.world_to_screen(target.pos))


def winstealer_update(game, ui):
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global combo_key, laneclear_key
    self = game.player

    if self.is_alive and not game.isChatOpen and not checkEvade():
        if draw_q_range:
            game.draw_circle_world(game.player.pos, q["Range"], 100, 2, Color.WHITE)
        if draw_w_range:
            game.draw_circle_world(
                game.player.pos,
                610.0
                + (20.0 * game.player.W.level)
                + game.player.gameplay_radius
                - 35.0,
                100,
                2,
                Color.WHITE,
            )
        if draw_e_range:
            game.draw_circle_world(game.player.pos, e["Range"], 100, 2, Color.WHITE)
        if draw_r_range:
            game.draw_circle_world(
                game.player.pos, 900 + 300 * game.player.R.level, 100, 2, Color.WHITE
            )

        if game.is_key_down(laneclear_key):
            Laneclear(game)
        if game.is_key_down(combo_key):
            Combo(game)
