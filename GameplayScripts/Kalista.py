from winstealer import *
from evade import checkEvade
from commons.items import *
from commons.skills import *
from commons.utils import *
from commons.targeting import *

winstealer_script_info = {
    "script": "WS+ Kalista",
    "author": "Wees",
    "description": "WS+ Kalista",
    "target_champ": "kalista",
}

lasthit_key = 45
harass_key = 46
key_orbwalk = 57
laneclear_key = 47

## Combo
use_q_in_combo = True
use_w_in_combo = True
use_e_in_combo = True
use_r_in_combo = True

# Evade
use_q_on_evade = True
use_w_on_evade = True
use_e_on_evade = True
use_r_on_evade = True

# KS
steal_kill_with_q = False
steal_kill_with_w = False
steal_kill_with_e = False
steal_kill_with_r = False

# Laneclear
lane_clear_with_q = False
lane_clear_with_w = False
lane_clear_with_e = False
lane_clear_with_r = False

# Drawings
draw_q_range = False
draw_w_range = False
draw_e_range = False
draw_r_range = False

draw_e_dmg = False

q = {"Range": 1150}
w = {"Range": 5000}
e = {"Range": 1000}
r = {"Range": 1000}


def winstealer_load_cfg(cfg):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q_on_evade, use_w_on_evade, use_e_on_evade, use_r_on_evade
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lane_clear_with_w, lane_clear_with_e, lane_clear_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global draw_e_dmg

    ## Keys
    lasthit_key = cfg.get_int("lasthit_key", 46)
    harass_key = cfg.get_int("harass_key", 45)
    key_orbwalk = cfg.get_int("key_orbwalk", 57)
    laneclear_key = cfg.get_int("laneclear_key", 47)

    ## Combo
    use_q_in_combo = cfg.get_bool("use_q_in_combo", True)
    use_w_in_combo = cfg.get_bool("use_w_in_combo", True)
    use_e_in_combo = cfg.get_bool("use_e_in_combo", True)
    use_r_in_combo = cfg.get_bool("use_r_in_combo", True)

    ## Evade
    use_q_on_evade = cfg.get_bool("use_q_on_evade", True)
    use_w_on_evade = cfg.get_bool("use_w_on_evade", True)
    use_e_on_evade = cfg.get_bool("use_e_on_evade", True)
    use_r_on_evade = cfg.get_bool("use_r_on_evade", True)

    ## KS
    steal_kill_with_q = cfg.get_bool("steal_kill_with_q", False)
    steal_kill_with_w = cfg.get_bool("steal_kill_with_w", False)
    steal_kill_with_e = cfg.get_bool("steal_kill_with_e", False)
    steal_kill_with_r = cfg.get_bool("steal_kill_with_r", False)

    ## Laneclear
    lane_clear_with_q = cfg.get_bool("lane_clear_with_q", False)
    lane_clear_with_w = cfg.get_bool("lane_clear_with_w", False)
    lane_clear_with_e = cfg.get_bool("lane_clear_with_e", False)
    lane_clear_with_r = cfg.get_bool("lane_clear_with_r", False)

    ## Drawings
    draw_q_range = cfg.get_bool("draw_q_range", False)
    draw_w_range = cfg.get_bool("draw_w_range", False)
    draw_e_range = cfg.get_bool("draw_e_range", False)
    draw_r_range = cfg.get_bool("draw_r_range", False)
    draw_e_dmg = cfg.get_bool("draw_e_dmg", False)


def winstealer_save_cfg(cfg):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q_on_evade, use_w_on_evade, use_e_on_evade, use_r_on_evade
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lane_clear_with_w, lane_clear_with_e, lane_clear_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global draw_e_dmg
    ## Keys
    cfg.set_int("lasthit_key", lasthit_key)
    cfg.set_int("harass_key", harass_key)
    cfg.set_int("laneclear_key", laneclear_key)
    cfg.set_int("key_orbwalk", key_orbwalk)

    ## Combo
    cfg.set_bool("use_q_in_combo", use_q_in_combo)
    cfg.set_bool("use_w_in_combo", use_w_in_combo)
    cfg.set_bool("use_e_in_combo", use_e_in_combo)
    cfg.set_bool("use_r_in_combo", use_r_in_combo)

    ## Evade
    cfg.set_bool("use_q_on_evade", use_q_on_evade)
    cfg.set_bool("use_w_on_evade", use_w_on_evade)
    cfg.set_bool("use_e_on_evade", use_e_on_evade)
    cfg.set_bool("use_r_on_evade", use_r_on_evade)

    ## KS
    cfg.set_bool("steal_kill_with_q", steal_kill_with_q)
    cfg.set_bool("steal_kill_with_w", steal_kill_with_w)
    cfg.set_bool("steal_kill_with_e", steal_kill_with_e)
    cfg.set_bool("steal_kill_with_r", steal_kill_with_r)

    ## Laneclear
    cfg.set_bool("lane_clear_with_q", lane_clear_with_q)
    cfg.set_bool("lane_clear_with_w", lane_clear_with_w)
    cfg.set_bool("lane_clear_with_e", lane_clear_with_e)
    cfg.set_bool("lane_clear_with_r", lane_clear_with_r)

    ## Drawings
    cfg.set_bool("draw_q_range", draw_q_range)
    cfg.set_bool("draw_w_range", draw_e_range)
    cfg.set_bool("draw_e_range", draw_w_range)
    cfg.set_bool("draw_r_range", draw_r_range)
    cfg.set_bool("draw_e_dmg", draw_e_dmg)

def winstealer_draw_settings(game, ui):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q_on_evade, use_w_on_evade, use_e_on_evade, use_r_on_evade
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lane_clear_with_w, lane_clear_with_e, lane_clear_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global draw_e_dmg

    ui.begin("WS+ Kalista")
    key_orbwalk = ui.keyselect("Combo key", key_orbwalk)
    #harass_key = ui.keyselect("Harass key", harass_key)
    laneclear_key = ui.keyselect("Laneclear key", laneclear_key)
    lasthit_key = ui.keyselect("LastHit key", lasthit_key)
    if ui.treenode("Setting [Q]"):
        use_q_in_combo = ui.checkbox("Use Q in Combo", use_q_in_combo)
        #steal_kill_with_q = ui.checkbox("Steal kill with Q", steal_kill_with_q)
        draw_q_range = ui.checkbox("Draw Q Range", draw_q_range)
        ui.treepop()

    if ui.treenode("Setting [W]"):
        use_w_in_combo = ui.checkbox("Use W in Combo", use_w_in_combo)
        #steal_kill_with_w = ui.checkbox("Steal kill with W", steal_kill_with_w)
        draw_w_range = ui.checkbox("Draw W Range", draw_w_range)
        ui.treepop()

    if ui.treenode("Setting [E]"):
        use_e_in_combo = ui.checkbox("Use E in Combo", use_e_in_combo)
        #steal_kill_with_e = ui.checkbox("Steal kill with E", steal_kill_with_e)
        draw_e_range = ui.checkbox("Draw E Range", draw_e_range)
        draw_e_dmg = ui.checkbox("Draw When is Killeable By E DMG", draw_e_dmg)
        ui.treepop()

    if ui.treenode("Setting [R]"):
        use_r_in_combo = ui.checkbox("Use R in Combo", use_r_in_combo)
        #steal_kill_with_r = ui.checkbox("Steal kill with R", steal_kill_with_r)
        draw_r_range = ui.checkbox("Draw R Range", draw_r_range)
        ui.treepop()

    if ui.treenode("Laneclear"):
        lane_clear_with_q = ui.checkbox("Laneclear with Q", lane_clear_with_q)
        lane_clear_with_e = ui.checkbox("Laneclear with E", lane_clear_with_e)
        ui.treepop()
    ui.end()

eBaseDamage = [20, 30, 40, 50, 60]
qLvLDamage = [50, 55, 60, 65, 70]
eStackDamage = [10.0, 16.0, 22.0, 28.0, 34.0]
eStackDamageMulti = [0.20, 0.2375, 0.275, 0.3125, 0.35]


def EDamage(game, target):
    global eBaseDamage
    
    # Calculate resistance
    resistance_melee = 0.0
    resistance_magic = 0.0

    penetration_melee_percent = 0.0
    penetration_melee_flat = 0.0
    penetration_melee_lethality = 0.0

    penetration_magic_percent = 0.0
    penetration_magic_flat = 0.0
    penetration_magic_lethality = 0.0

    resistance_melee = target.armour
    penetration_percent = 0.0  # TODO
    penetration_flat = 0.0  # TODO
    penetration_lethality = 0.0  # TODO

    resistance_magic = target.magic_resist
    penetration_percent = 0.0  # TODO
    penetration_flat = 0.0  # TODO
    penetration_lethality = 0.0  # TODO

    # Lethality calculation
    # penetration_flat += penetration_lethality * (0.6 + 0.4 * source.lvl / 18.0)
    damage_mul_melee = 0.0
    damage_mul_magic = 0.0

    if resistance_melee >= 0.0:
        damage_mul_melee = 100.0 / (100.0 + resistance_melee)
    else:
        damage_mul_melee = 2.0 - 100.0 / (100.0 - resistance_melee)

    if resistance_magic >= 0.0:
        damage_mul_magic = 100.0 / (100.0 + resistance_magic)
    else:
        damage_mul_magic = 2.0 - 100.0 / (100.0 - resistance_magic)

    ecount = 0
    if getBuff(target, "kalistaexpungemarker"):
        ecount = getBuff(target, "kalistaexpungemarker").countAlt -1
    else: count = -1

    #damage_melee =  (( game.player.bonus_atk * 0.60 ) + eBaseDamage[game.player.E.level - 1]) + ((( game.player.bonus_atk * eStackDamageMulti[game.player.E.level - 1] ) + eStackDamage[game.player.E.level - 1]) * ecount)
    total_atk = game.player.base_atk + game.player.bonus_atk
    damage_melee = (eBaseDamage[game.player.E.level - 1] + (total_atk * 0.6)) 
    damage_melee += ((eStackDamage[game.player.E.level - 1] + ((total_atk) *eStackDamageMulti[game.player.E.level - 1])) * ecount)
    return (damage_melee * damage_mul_melee)

def DrawEDMG(game, player):
    color = Color.GREEN
    player = game.player
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
        ):
            if EDamage(game, champ) >= champ.health:
                p = game.hp_bar_pos(champ)
                color.a = 5.0
                game.draw_rect(
                    Vec4(p.x - 47, p.y - 27, p.x + 61, p.y - 12), color, 0, 2
                )

def QDamage(game, target):
    global qLvLDamage
    return (qLvLDamage[game.player.Q.level - 1] + (get_onhit_physical(game.player, target)))

#def EDamage(game, target):
#    global eLvLDamage
#    return (eLvLDamage[game.player.E.level - 1] + (get_onhit_physical(game.player, target)))

def Combo(game):
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    if use_q_in_combo and IsReady(game, q_spell):
        target = GetBestTargetsInRange(game, q["Range"])
        if ValidTarget(target) and target:
            if target and not IsCollisioned(game, target):
                #if QDamage(game, target) > target.health:
                if target.isMoving:
                    q_spell.move_and_trigger(game.world_to_screen(castpoint_for_collision(game, q_spell, game.player, target)))
                else:
                    q_spell.move_and_trigger(game.world_to_screen(castpoint_for_collision(game, q_spell, game.player, target)))
    if use_e_in_combo and IsReady(game, e_spell):  # and getBuff(game.player, "TwitchDeadlyVenom")
        target = GetBestTargetsInRange(game, e["Range"])
        if target and getBuff(target, "kalistaexpungemarker"):
            if (EDamage(game, target) >= target.health):
                e_spell.trigger(False)
def Laneclear(game):
    q_spell = getSkill(game, "Q")
    e_spell = getSkill(game, "E")
    if lane_clear_with_q and IsReady(game, q_spell):
        minion = GetBestMinionsInRange(game, q["Range"])
        if ValidTarget(minion) and minion:
            if QDamage(game, minion) > minion.health:
                q_spell.move_and_trigger(game.world_to_screen(minion.pos))
    if lane_clear_with_e and IsReady(game, e_spell):  # and getBuff(game.player, "TwitchDeadlyVenom")
        minion = GetBestMinionsInRange(game, e["Range"]) or GetBestJungleInRange(game, e["Range"])
        #if minion and getBuff(minion, "kalistaexpungemarker"):
        if (EDamage(game, minion) >= minion.health):
            e_spell.trigger(False)

def winstealer_update(game, ui):
    global key_orbwalk, lasthit_key, harass_key, laneclear_key
    global use_q_in_combo, use_w_in_combo, use_e_in_combo, use_r_in_combo
    global use_q_on_evade, use_w_on_evade, use_e_on_evade, use_r_on_evade
    global steal_kill_with_q, steal_kill_with_w, steal_kill_with_e, steal_kill_with_r
    global lane_clear_with_q, lane_clear_with_w, lane_clear_with_e, lane_clear_with_r
    global draw_q_range, draw_w_range, draw_e_range, draw_r_range
    global draw_e_dmg

    self = game.player
    #player = game.player
    if draw_e_dmg:
        DrawEDMG(game, self)
    if (
        self.is_alive
        and game.is_point_on_screen(game.player.pos)
        and not game.isChatOpen
    ):
        if draw_q_range:
            game.draw_circle_world(game.player.pos, q["Range"], 100, 1, Color.WHITE)
        if draw_w_range:
            game.draw_circle_world(game.player.pos, w["Range"], 100, 1, Color.WHITE)
        if draw_e_range:
            game.draw_circle_world(game.player.pos, e["Range"], 100, 1, Color.WHITE)
        if draw_r_range:
            game.draw_circle_world(game.player.pos, r["Range"], 100, 1, Color.WHITE)
        if game.is_key_down(laneclear_key):
            Laneclear(game)
        if game.is_key_down(key_orbwalk):
            Combo(game)