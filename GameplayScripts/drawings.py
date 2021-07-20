from winstealer import *
from time import time
from commons.skills import *
from commons.items import *
from commons.utils import *
import itertools, math
from copy import copy
import array
import commons.damage_calculator as damage_calculator
from win32api import GetSystemMetrics

winstealer_script_info = {
    "script": "Visuals",
    "author": "bckd00r // TopZoozle",
    "description": "Draw indicators for different things",
}

turret_ranges = False
enemy_ranges = False
attack_range = False
minion_last_hit = False
draw_spell_range = False

skillshots = False
skillshots_predict = False
skillshots_min_range = 0
skillshots_max_speed = 0
skillshots_show_ally = False
skillshots_show_enemy = False

colors = {
    0: Color.YELLOW,
    1: Color.GREEN,
    2: Color.PURPLE,
    3: Color.WHITE,
    4: Color.CYAN,
    5: Color.RED,
    6: Color.ORANGE,
}
selectedColor = 0


def winstealer_load_cfg(cfg):
    global colors
    global turret_ranges, enemy_ranges, attack_range, draw_spell_range
    global skillshots, skillshots_predict, skillshots_min_range, minion_last_hit, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
    turret_ranges = cfg.get_bool("turret_ranges", True)
    enemy_ranges = cfg.get_bool("enemy_ranges", True)
    minion_last_hit = cfg.get_bool("minion_last_hit", True)
    draw_spell_range = cfg.get_bool("draw_spell_range", True)
    attack_range = cfg.get_bool("attack_range", True)

    skillshots = cfg.get_bool("skillshots", True)
    skillshots_show_ally = cfg.get_bool("skillshots_show_ally", True)
    skillshots_show_enemy = cfg.get_bool("skillshots_show_enemy", True)
    skillshots_predict = cfg.get_bool("skillshots_predict", True)
    skillshots_min_range = cfg.get_float("skillshots_min_range", 500)
    skillshots_max_speed = cfg.get_float("skillshots_max_speed", 2500)


def winstealer_save_cfg(cfg):
    global turret_ranges, enemy_ranges, attack_range, draw_spell_range
    global skillshots, skillshots_predict, skillshots_min_range, minion_last_hit, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
    cfg.set_bool("turret_ranges", turret_ranges)
    cfg.set_bool("enemy_ranges", enemy_ranges)
    cfg.set_bool("minion_last_hit", minion_last_hit)
    cfg.set_bool("draw_spell_range", draw_spell_range)
    cfg.set_bool("attack_range", attack_range)

    cfg.set_bool("skillshots", skillshots)
    cfg.set_bool("skillshots_show_ally", skillshots_show_ally)
    cfg.set_bool("skillshots_show_enemy", skillshots_show_enemy)
    cfg.set_bool("skillshots_predict", skillshots_predict)
    cfg.set_float("skillshots_min_range", skillshots_min_range)
    cfg.set_float("skillshots_max_speed", skillshots_max_speed)


def winstealer_draw_settings(game, ui):
    global turret_ranges, enemy_ranges, attack_range, minion_last_hit, draw_spell_range
    global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy
    global selectedColor, colors

    selectedColor = ui.listbox(
        "Drawings color",
        ["YELLOW", "GREEN", "PURPLE", "RED", "WHITE", "ORANGE", "CYAN", "BLUE"],
        selectedColor,
    )

    turret_ranges = ui.checkbox("Turret ranges", turret_ranges)
    enemy_ranges = ui.checkbox("Draw enemy ranges", enemy_ranges)
    minion_last_hit = ui.checkbox("Minion last hit", minion_last_hit)
    draw_spell_range = ui.checkbox("Champion spell range", draw_spell_range)
    attack_range = ui.checkbox("Champion attack range", attack_range)

    ui.separator()
    ui.text("Skillshots (Experimental)")
    skillshots = ui.checkbox("Draw skillshots", skillshots)
    skillshots_show_ally = ui.checkbox("Show for allies", skillshots_show_ally)
    skillshots_show_enemy = ui.checkbox("Show for enemies", skillshots_show_enemy)
    skillshots_predict = ui.checkbox("Show prediction", skillshots_predict)
    skillshots_min_range = ui.dragfloat(
        "Minimum skillshot range", skillshots_min_range, 100, 0, 3000
    )
    skillshots_max_speed = ui.dragfloat(
        "Maximum skillshot speed", skillshots_max_speed, 100, 1000, 5000
    )


def draw_atk_range(game, player):
    if player.is_alive and player.is_visible and game.is_point_on_screen(player.pos):
        game.draw_circle_world(
            player.pos, player.atkRange + player.gameplay_radius, 100, 1, Color.WHITE
        )


def draw_recall_states(game, player):
    i = 0
    x = 5
    y = GetSystemMetrics(1) / 2 - 300
    color_back = Color(102, 1, 1, 0.1)
    color_line = Color.ORANGE
    color_line.a = 0.5
    endTime = 0
    for champ in game.champs:
        if champ.is_alive and champ.isRecalling == 6:
            buff = getBuff(champ, "recall")
            if buff:
                remaining = buff.end_time - game.time
                game.draw_text(
                    Vec2(x + 30, y + i - 30), str(champ.name).capitalize(), Color.GREEN
                )
                game.draw_rect(Vec4(x, y + i - 5, x + 200, y + i + 5), Color.BLUE, 0, 2)
                game.draw_line(Vec2(x, y + i), Vec2(x + 200, y + i), 9, color_back)
                game.draw_line(
                    Vec2(x, y + i),
                    Vec2(x + (200 * (round(remaining / 8 * 100) / 100)), y + i),
                    10,
                    color_line,
                )
                game.draw_image(
                    champ.name.lower() + "_square",
                    Vec2(x, y + i - 40),
                    Vec2(x, y + i - 40).add(Vec2(30, 30)),
                    Color.WHITE,
                )
                i += 50

def draw_turret_ranges(game, player):
    for turret in game.turrets:
        if turret.is_alive and turret.is_enemy_to(player):
            range = turret.gameplay_radius + 750
            game.draw_circle_world(turret.pos, range, 100, 2, Color(1, 0, 1, 0.3))


def draw_minion_last_hit(game, player):
    color = Color.WHITE
    for minion in game.minions:
        if (
            minion.is_visible
            and minion.is_alive
            and minion.is_enemy_to(player)
            and game.is_point_on_screen(minion.pos)
        ):
            if is_last_hitable(game, player, minion):
                p = game.hp_bar_pos(minion)
                game.draw_rect(Vec4(p.x - 34, p.y - 9, p.x + 32, p.y + 1), color, 0, 2)


def draw_champ_ranges(game, player):
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
            and champ.movement_speed > 0
        ):
            game.draw_circle_world(
                champ.pos,
                champ.base_atk_range + champ.gameplay_radius,
                100,
                1,
                Color.WHITE,
            )


def draw_predictions(game, player):
    damage_spec = damage_calculator.get_damage_specification(game, game.player)
    if damage_spec is None:
        damage_spec = False
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
        ):
            dmg = 0
            if damage_spec != False:
                dmg = damage_spec.calculate_damage(game, game.player, champ)
            p = game.hp_bar_pos(champ)

            barWidth = 103
            xWidth = 45

            percentHealthAfterDamage = (
                max(0, champ.health - get_onhit_physical(game.player, champ) - dmg)
                / champ.max_health
            )
            xPosEnd = (
                p.x
                + barWidth
                * (champ.health + (champ.health_regen * 3))
                / champ.max_health
            )
            xPosStart = p.x + percentHealthAfterDamage * 100

            game.draw_rect_filled(
                Vec4(xPosStart - xWidth, p.y - 25, xPosEnd - xWidth, p.y - 12),
                Color.ORANGE,
            )


def pos_calculator(game, player):
    for champ in game.champs:
        if (
            champ.is_alive
            and champ.is_visible
            and champ.is_enemy_to(player)
            and game.is_point_on_screen(champ.pos)
            and champ.movement_speed > 0
        ):
            champ_dir = champ.pos.sub(champ.prev_pos).normalize()
            if math.isnan(champ_dir.x):
                champ_dir.x = 0.0
            if math.isnan(champ_dir.y):
                champ_dir.y = 0.0
            if math.isnan(champ_dir.z):
                champ_dir.z = 0.0
            champ_future_pos = champ.pos.add(champ_dir.scale(champ.movement_speed))
            t = (
                champ.pos.distance(champ_future_pos)
                / champ_future_pos.distance(champ_dir.scale(champ.movement_speed))
                * 1000
            )
            if t < 1:
                continue
            game.draw_circle_world(
                champ_future_pos.add(champ_dir.scale(t)), 30, 100, 1, Color.RED
            )
            game.draw_text(
                game.world_to_screen(champ_future_pos.add(champ_dir.scale(t))),
                str(int(player.base_ms / player.movement_speed * 100)),
                Color.RED,
            )


def draw_skillshots(game, player):
    global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed, skillshots_show_ally, skillshots_show_enemy

    color = Color.WHITE
    for missile in game.missiles:
        if not skillshots_show_ally and missile.is_ally_to(game.player):
            continue
        if not skillshots_show_enemy and missile.is_enemy_to(game.player):
            continue

        if (
            not is_skillshot(missile.name)
            or missile.speed > skillshots_max_speed
            or missile.start_pos.distance(missile.end_pos) < skillshots_min_range
        ):
            continue

        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue

        end_pos = missile.end_pos.clone()
        start_pos = missile.start_pos.clone()
        curr_pos = missile.pos.clone()

        start_pos.y = game.map.height_at(start_pos.x, start_pos.z) + missile.height
        end_pos.y = start_pos.y
        curr_pos.y = start_pos.y

        # if (
        #     game.point_on_line(
        #         game.world_to_screen(start_pos),
        #         game.world_to_screen(end_pos),
        #         game.world_to_screen(player.pos),
        #         player.gameplay_radius * 2,
        #     )
        #     and game.is_point_on_screen(curr_pos)
        # ):
        pointSegment, pointLine, isOnSegment = VectorPointProjectionOnLineSegment(
            start_pos, end_pos, player.pos
        )
        if (
            isOnSegment
            and pointSegment.distance(player.pos) < 100 + player.gameplay_radius * 2
            and game.is_point_on_screen(curr_pos)
            and start_pos.distance(end_pos) > start_pos.distance(player.pos)
        ):
            if game.is_point_on_screen(curr_pos):
                if spell.flags & SFlag.Line or spell.flags & SFlag.SkillshotLine:
                    draw_rect(game, curr_pos, end_pos, missile.width, color)
                    draw_rect(
                        game, curr_pos, end_pos, player.gameplay_radius * 2, color
                    )
                    game.draw_circle_world(end_pos, missile.width * 2, 100, 1, color)

                elif spell.flags & SFlag.Area:
                    end_pos.y = game.map.height_at(end_pos.x, end_pos.z)

                    game.draw_circle_world(end_pos, missile.cast_radius, 100, 3, color)
                elif spell.flags & SFlag.Cone:
                    game.draw_circle_world(curr_pos, missile.width, 100, 1, color)
                    draw_rect(
                        game, curr_pos, start_pos, player.gameplay_radius * 2, color
                    )
                    draw_rect(game, curr_pos, start_pos, missile.width, color)
                else:
                    end_pos.y = game.map.height_at(end_pos.x, end_pos.z)
                    game.draw_circle_world(
                        start_pos, missile.cast_radius, 100, 1, color
                    )


def winstealer_update(game, ui):
    global turret_ranges, attack_range, skillshots, minion_last_hit, draw_spell_range, skillshots_predict

    player = game.player

    game.draw_text(Vec2(GetSystemMetrics(1) - 150, 0), "__Xepher__", Color.YELLOW)
    game.draw_text(Vec2(GetSystemMetrics(2), 0), "Menu Key [INSERT]", Color.YELLOW)

    draw_recall_states(game, player)
    if attack_range:
        draw_atk_range(game, player)

    if player.is_alive and not game.isChatOpen:
        if skillshots_predict:
            draw_predictions(game, player)

        if turret_ranges:
            draw_turret_ranges(game, player)

        if enemy_ranges:
            draw_champ_ranges(game, player)

        if minion_last_hit:
            draw_minion_last_hit(game, player)

        if skillshots:
            draw_skillshots(game, player)
