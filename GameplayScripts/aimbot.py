from winstealer import *
from evade import checkEvade
from commons.items import *
from commons.skills import *
from commons.utils import *
from commons.targeting import *
import json, time
from pprint import pprint


winstealer_script_info = {
    "script": "Auto Spell",
    "author": "TopZoozle",
    "description": "Automatically directs spells at enemies",
}


cast_keys = {
    'Q':0,
    'W':0,
    'E':0,
    'R':0
}


def winstealer_load_cfg(cfg):
    global cast_keys
    cast_keys = json.loads(cfg.get_str('cast_keys', json.dumps(cast_keys)))

def winstealer_save_cfg(cfg):
    global cast_keys
    cfg.set_str('cast_keys', json.dumps(cast_keys))


def winstealer_draw_settings(game, ui):
    global cast_keys
    for slot, key in cast_keys.items():
        cast_keys[slot] = ui.keyselect(f"Key to cast {slot}", key)

def winstealer_update(game, ui):
    global cast_keys
    if game.player.is_alive and game.player.is_visible and not game.isChatOpen:
        for slot, key in cast_keys.items():
            if game.was_key_pressed(key):
                skill = getattr(game.player, slot)
                target = GetBestTargetsInRange(game, skill.cast_range)
                cursor = game.get_cursor()
                if IsReady(game, skill):
                    if target:
                        game.draw_circle_world(target.pos, 200, 100, 1, Color.RED)
                        cast_point = castpoint_for_collision(
                            game, skill, game.player, target
                        )
                        skill.move_and_trigger(game.world_to_screen(cast_point))
