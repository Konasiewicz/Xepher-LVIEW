from winstealer import *
from commons.utils import *
from commons.skills import *
from commons.items import *
from commons.targeting import *
import json, time, math

winstealer_script_info = {
    "script": "WS+ Ashe",
    "author": "bckd00r",
    "description": "WS+ Ashe",
    "target_champ": "ashe",
}

combo_key = 57
harass_key = 45
laneclear_key = 47
ks_key = 20

use_q_in_combo = True
use_w_in_combo = True
use_r_in_combo = True

auto_e_last_pos = True

lane_clear_with_w = False
lane_clear_with_q = False

harass_with_w = True
harass_with_q = True

draw_w_range = False

ks_w = True
ks_r = True

LastE = 0

w = {"Range": 1200.0, "Mana": 70}
r = {"Range": 0, "Mana": 50}

lastW = 0
lastQ = 0
lastR = 0


def winstealer_load_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_w_range
    global combo_key, harass_key, laneclear_key, ks_key
    global lane_clear_with_w, lane_clear_with_q
    global auto_e_last_pos
    global harass_with_w, harass_with_q
    global ks_w, ks_r
    combo_key = cfg.get_int("combo_key", 57)
    harass_key = cfg.get_int("harass_key", 45)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    ks_key = cfg.get_int("ks_key", 20)

    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    harass_with_w = cfg.get_bool("harass_with_w", True)
    harass_with_q = cfg.get_bool("harass_with_q", True)

    auto_e_last_pos = cfg.get_bool("auto_e_last_pos", True)

    draw_w_range = cfg.get_bool("draw_w_range", False)

    ks_w = cfg.get_bool("ks_w", True)
    ks_r = cfg.get_bool("ks_r", True)

    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", False)
    lane_clear_with_w = cfg.get_bool("lane_clear_with_w", False)


def winstealer_save_cfg(cfg):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_w_range
    global combo_key, harass_key, laneclear_key, ks_key
    global lane_clear_with_q, lane_clear_with_w
    global auto_e_last_pos
    global harass_with_w, harass_with_q
    global ks_w, ks_r

    cfg.set_int("combo_key", combo_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("ks_key", ks_key)

    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    cfg.set_bool("harass_with_w", harass_with_w)
    cfg.set_bool("harass_with_q", harass_with_q)

    cfg.set_bool("auto_e_last_pos", auto_e_last_pos)

    cfg.set_bool("draw_w_range", draw_w_range)

    cfg.set_bool("ks_w", ks_w)
    cfg.set_bool("ks_r", ks_r)

    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)
    cfg.set_bool("lane_clear_with_w", lane_clear_with_w)


def winstealer_draw_settings(game, ui):
    global use_q_in_combo, use_w_in_combo, use_r_in_combo
    global draw_w_range
    global combo_key, harass_key, laneclear_key, ks_key
    global lane_clear_with_q, lane_clear_with_w
    global auto_e_last_pos
    global harass_with_w, harass_with_q
    global ks_w, ks_r

    ui.begin("WS+ Ashe")
    combo_key = ui.keyselect("Combo key", combo_key)
    harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    ks_key = ui.keyselect("Killsteal key", ks_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        harass_with_q = ui.checkbox("Harass [Q]", harass_with_q)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        harass_with_w = ui.checkbox("Harass [W]", harass_with_w)
        ks_w = ui.checkbox("Killsteal W", ks_w)
        draw_w_range = ui.checkbox("Draw [W]", draw_w_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        auto_e_last_pos = ui.checkbox(
            "AutoE on invisible Target last pos seen", auto_e_last_pos
        )
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        ks_r = ui.checkbox("Killsteal R", ks_r)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        lane_clear_with_w = ui.checkbox("Laneclear with W", lane_clear_with_w)
        ui.treepop()
    ui.end()


def WDamage(game, target):
    damage = 0
    if game.player.W.level == 1:
        damage = 20 + (get_onhit_physical(game.player, target))
    elif game.player.W.level == 2:
        damage = 35 + (get_onhit_physical(game.player, target))
    elif game.player.W.level == 3:
        damage = 50 + (get_onhit_physical(game.player, target))
    elif game.player.W.level == 4:
        damage = 65 + (get_onhit_physical(game.player, target))
    elif game.player.W.level == 5:
        damage = 80 + (get_onhit_physical(game.player, target))
    return damage


def RDamage(game, target):
    damage = 0
    if game.player.R.level == 1:
        damage = 200 + (get_onhit_magical(game.player, target))
    elif game.player.R.level == 2:
        damage = 400 + (get_onhit_magical(game.player, target))
    elif game.player.R.level == 3:
        damage = 600
    return damage


def Killsteal(game):
    global lastW
    w_spell = getSkill(game, "W")
    r_spell = getSkill(game, "R")
    if (
        ks_w
        and lastW + 3 < game.time
        and IsReady(game, w_spell)
        and game.player.mana > w["Mana"]
    ):
        target = GetBestTargetsInRange(game, w["Range"])
        if target and WDamage(game, target) >= target.health:
            lastW = game.time
            w_spell.move_and_trigger(game.world_to_screen(target.pos))
    if ks_r and IsReady(game, r_spell) and game.player.mana > 100:
        target = GetBestTargetsInRange(game, 25000.0)
        if target and RDamage(game, target) >= target.health:
            r_spell.move_and_trigger(game.world_to_screen(target.pos))


def Harass(game):
    global w
    global lastW, lastQ
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    if (
        harass_with_w
        and lastW + 3 < game.time
        and IsReady(game, w_spell)
        and game.player.mana > w["Mana"]
    ):
        target = GetBestTargetsInRange(game, w["Range"])
        if target:
            lastW = game.time
            w_spell.move_and_trigger(game.world_to_screen(target.pos))
    if (
        harass_with_q
        and lastQ + 0.5 < game.time
        and getBuff(game.player, "asheqcastready")
        and IsReady(game, q_spell)
        and game.player.mana > 50
    ):
        target = GetBestTargetsInRange(game)
        if target:
            lastQ = game.time
            q_spell.trigger(False)


def Combo(game):
    global w, r
    global LastE, lastW, lastQ, lastR
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    r_spell = getSkill(game, "R")

    if (
        use_q_in_combo
        and lastQ + 1 < game.time
        and getBuff(game.player, "asheqcastready")
        and IsReady(game, q_spell)
        and game.player.mana > 50
    ):
        target = GetBestTargetsInRange(game)
        if target:
            lastQ = game.time
            q_spell.trigger(False)
    if (
        use_w_in_combo
        and lastW + 1 < game.time
        and IsReady(game, w_spell)
        and game.player.mana > w["Mana"] + 50
    ):
        target = GetBestTargetsInRange(game, w["Range"])
        if target:
            lastW = game.time
            w_spell.move_and_trigger(game.world_to_screen(target.pos))
    if (
        use_r_in_combo
        and IsReady(game, r_spell)
        and game.player.mana > 100 + w["Mana"]
        and lastR + 1 < game.time
    ):
        target = GetBestTargetsInRange(game, w["Range"])  ## gapcloser
        if target:
            lastR = game.time
            r_spell.move_and_trigger(game.world_to_screen(target.pos))


def AutoVision(game):
    global LastE
    e_spell = getSkill(game, "E")
    if game.time + 10 < lastE and IsReady(game, e_spell):
        for champ in game.champs:
            if (
                champ.is_visible
                or not champ.is_alive
                or game.is_point_on_screen(champ.pos)
            ):
                continue
            LastE = game.time
            e_spell.move_and_trigger(
                game.world_to_screen(
                    castpoint_for_collision(game, e_spell, game.player, champ)
                )
            )


def Laneclear(game):
    global lastW, lastQ
    q_spell = getSkill(game, "Q")
    w_spell = getSkill(game, "W")
    if (
        lane_clear_with_q
        and lastQ + 1 < game.time
        and IsReady(game, q_spell)
        and getBuff(game.player, "asheqcastready")
        and game.player.mana > 50 + w["Mana"] + 30
    ):
        minion = GetBestMinionsInRange(game) or GetBestJungleInRange(game)
        if minion:
            lastQ = game.time
            q_spell.trigger(False)
    if (
        lane_clear_with_w
        and lastW + 2 < game.time
        and IsReady(game, w_spell)
        and game.player.mana > w["Mana"] + 50 + 80
    ):
        minion = GetBestMinionsInRange(game) or GetBestJungleInRange(game)
        if minion:
            lastW = game.time
            w_spell.move_and_trigger(game.world_to_screen(minion.pos))


def winstealer_update(game, ui):
    global combo_key, harass_key, laneclear_key, ks_key
    global draw_w_range

    self = game.player

    if self.is_alive and not game.isChatOpen:

        if draw_w_range:
            game.draw_circle_world(game.player.pos, w["Range"], 100, 2, Color.WHITE)
            game.draw_circle_world(game.player.pos, 800, 100, 2, Color.WHITE)

        if auto_e_last_pos:
            AutoVision(game)

        if game.is_key_down(combo_key):
            Combo(game)
        if game.is_key_down(harass_key):
            Harass(game)
        if game.is_key_down(ks_key):
            Killsteal(game)
        if game.is_key_down(laneclear_key):
            Laneclear(game)
