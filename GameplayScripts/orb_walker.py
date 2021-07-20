from winstealer import *
from evade import checkEvade
from commons.items import *
from commons.skills import *
from commons.utils import *
from commons.targeting import *
from commons.timer import Timer
import time, json, random
from API.summoner import *

winstealer_script_info = {
    "script": "WS+ Orbwalker",
    "author": "bckd00r // fixed by TopZoozle",
    "description": "Sub Optimal at best",
}

lasthit_key = 45
harass_key = 46
key_orbwalk = 57
laneclear_key = 47

randomize_movement = False

draw_killable_minion = False
draw_killable_minion_fade = False

click_speed = 0
kite_ping = 0


def winstealer_load_cfg(cfg):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global randomize_movement
    global click_speed, kite_ping
    global draw_killable_minion, draw_killable_minion_fade

    lasthit_key = cfg.get_int("lasthit_key", 46)
    harass_key = cfg.get_int("harass_key", 45)
    key_orbwalk = cfg.get_int("key_orbwalk", 57)
    laneclear_key = cfg.get_int("laneclear_key", 47)
    draw_killable_minion = cfg.get_bool("draw_killable_minion", False)
    randomize_movement = cfg.get_bool("randomize_movement", False)
    draw_killable_minion_fade = cfg.get_bool("draw_killable_minion_fade", False)
    click_speed = cfg.get_int("click_speed", 7)
    kite_ping = cfg.get_int("kite_ping", 20)


def winstealer_save_cfg(cfg):
    global key_orbwalk, harass_key, lasthit_key, laneclear_key
    global randomize_movement
    global click_speed, kite_ping
    global draw_killable_minion, draw_killable_minion_fade

    cfg.set_int("lasthit_key", lasthit_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("key_orbwalk", key_orbwalk)
    cfg.set_bool("draw_killable_minion", draw_killable_minion)
    cfg.set_bool("randomize_movement", randomize_movement)
    cfg.set_bool("draw_killable_minion_fade", draw_killable_minion_fade)
    cfg.set_float("click_speed", click_speed)
    cfg.set_float("kite_ping", kite_ping)


def winstealer_draw_settings(game, ui):
    global key_orbwalk, harass_key, lasthit_key, laneclear_key
    global randomize_movement
    global click_speed, kite_ping
    global draw_killable_minion, draw_killable_minion_fade

    if ui.treenode("Key settings"):
        lasthit_key = ui.keyselect("Last hit key", lasthit_key)
        harass_key = ui.keyselect("Harass key", harass_key)
        laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
        key_orbwalk = ui.keyselect("Orbwalk activate key", key_orbwalk)
        ui.treepop()
    click_speed = ui.sliderint("Click speed", int(click_speed), 50, 100)
    kite_ping = ui.sliderint("Kite ping", int(kite_ping), 0, 100)
    randomize_movement = ui.checkbox("Randomize movement pos", randomize_movement)
    draw_killable_minion = ui.checkbox("Draw killable minions", draw_killable_minion)
    draw_killable_minion_fade = ui.checkbox(
        "Draw killable minions fade effect", draw_killable_minion_fade
    )


def drawKillableMinions(game, fade_effect):
    minion = game.GetBestTarget(
        UnitTag.Unit_Minion_Lane, game.player.atkRange + game.player.gameplay_radius
    )
    if minion:
        if fade_effect:
            percentHealth = (minion.health / minion.max_health) * 100
            value = 255 - (minion.health * 2)
            game.draw_circle_world(
                minion.pos,
                minion.gameplay_radius * 2,
                100,
                1,
                Color(0.0, 1.0, 1.0 - value, 1.0),
            )
        if not fade_effect:
            game.draw_circle_world(
                minion.pos, minion.gameplay_radius * 2, 100, 2, Color.ORANGE
            )


attackTimer = Timer()
moveTimer = Timer()
humanizer = Timer()

last = 0
atk_speed = 0


def winstealer_update(game, ui):
    global key_orbwalk, lasthit_key, laneclear_key
    global randomize_movement
    global click_speed, kite_ping
    global draw_killable_minion, draw_killable_minion_fade
    global attackTimer, moveTimer, humanizer
    global last
    if draw_killable_minion_fade:
        drawKillableMinions(game, True)
    elif draw_killable_minion:
        drawKillableMinions(game, False)

    self = game.player

    if (
        self.is_alive
        and game.is_point_on_screen(self.pos)
        and not game.isChatOpen
        and not checkEvade()
    ):
        # if last + 0.2 < game.time:
        #     last = game.time
        atk_speed = GetAttackSpeed()
        c_atk_time = max(1.0 / atk_speed, kite_ping / 100)
        b_windup_time = (1.0 / atk_speed) * (
            self.basic_atk_windup / self.atk_speed_ratio
        )
        if game.is_key_down(key_orbwalk):
            target = game.GetBestTarget(
                UnitTag.Unit_Champion,
                game.player.atkRange + game.player.gameplay_radius,
            )
            if attackTimer.Timer() and target:
                game.click_at(False, game.world_to_screen(target.pos))
                attackTimer.SetTimer(c_atk_time)
                moveTimer.SetTimer(b_windup_time)
            else:
                if humanizer.Timer():
                    if moveTimer.Timer():
                        if randomize_movement and target:
                            game.click_at(
                                False,
                                game.world_to_screen(GetKitePosition(game, target)),
                            )
                        else:
                            game.press_right_click()
                    humanizer.SetTimer(click_speed / 1000)
        if game.is_key_down(lasthit_key):
            target = LastHitMinions(game)
            if attackTimer.Timer() and target:
                game.click_at(False, game.world_to_screen(target.pos))
                attackTimer.SetTimer(c_atk_time)
                moveTimer.SetTimer(b_windup_time)
            else:
                if humanizer.Timer():
                    if moveTimer.Timer():
                        if randomize_movement and target:
                            game.click_at(
                                False,
                                game.world_to_screen(GetKitePosition(game, target)),
                            )
                        else:
                            game.press_right_click()
                    humanizer.SetTimer(click_speed / 1000)
        if game.is_key_down(laneclear_key):
            oldPos = game.get_cursor
            game.DEBUG_target_pos(game.world_to_screen(game.player.pos))
            target = (
                game.GetBestTarget(
                    UnitTag.Unit_Structure_Turret,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                or game.GetBestTarget(
                    UnitTag.Unit_Minion_Lane,
                    game.player.atkRange + game.player.gameplay_radius,
                )
                or game.GetBestTarget(
                    UnitTag.Unit_Monster,
                    game.player.atkRange + game.player.gameplay_radius,
                )
            )
            if attackTimer.Timer() and target:
                game.click_at(False, game.world_to_screen(target.pos))
                attackTimer.SetTimer(c_atk_time)
                moveTimer.SetTimer(b_windup_time)
            else:
                if humanizer.Timer():
                    if moveTimer.Timer():
                        if randomize_movement and target:
                            game.click_at(
                                False,
                                game.world_to_screen(GetKitePosition(game, target)),
                            )
                        else:
                            game.press_right_click()
                    humanizer.SetTimer(click_speed / 1000)
