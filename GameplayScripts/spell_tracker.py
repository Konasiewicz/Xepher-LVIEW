from winstealer import *

show_local_champ = False
show_allies = False
show_enemies = False

winstealer_script_info = {
    "script": "Skill Tracker",
    "author": "bckd00r",
    "description": "Tracks spell cooldowns and levels",
}


def get_color_for_cooldown(cooldown):
    if cooldown > 0.0:
        return Color.GRAY
    else:
        return Color(1, 1, 1, 1)


def draw_spell(game, spell, pos, size, show_lvl=True, show_cd=True):

    cooldown = spell.get_current_cooldown(game.time)
    color = get_color_for_cooldown(cooldown) if spell.level > 0 else Color.GRAY

    game.draw_image(spell.icon, pos, pos.add(Vec2(size, size)), color)
    if show_cd and cooldown > 0.0:
        game.draw_text(pos.add(Vec2(4, 5)), str(int(cooldown)), Color.WHITE)


def draw_overlay_on_champ(game, champ):

    p = game.hp_bar_pos(champ)
    p.x -= 70
    if not game.is_point_on_screen(p):
        return

    p.x += 25
    draw_spell(game, champ.Q, p, 24)
    p.x += 25
    draw_spell(game, champ.W, p, 24)
    p.x += 25
    draw_spell(game, champ.E, p, 24)
    p.x += 25
    draw_spell(game, champ.R, p, 24)

    p.x += 34
    p.y -= 28
    draw_spell(game, champ.D, p, 20)
    p.x += 20
    p.y += 0
    draw_spell(game, champ.F, p, 20)


def winstealer_update(game, ui):
    global show_allies, show_enemies, show_local_champ

    for champ in game.champs:
        if (
            not champ.is_visible
            or not champ.is_alive
            or champ.has_tags(UnitTag.Unit_Champion_Clone)
            or champ.has_tags(UnitTag.Unit_Special)
            or champ.has_tags(UnitTag.Unit_Special_Peaceful)
        ):
            continue
        if champ == game.player and show_local_champ:
            draw_overlay_on_champ(game, champ)
        elif champ != game.player:
            if champ.is_ally_to(game.player) and show_allies:
                draw_overlay_on_champ(game, champ)
            elif champ.is_enemy_to(game.player) and show_enemies:
                draw_overlay_on_champ(game, champ)


def winstealer_load_cfg(cfg):
    global show_allies, show_enemies, show_local_champ

    show_allies = cfg.get_bool("show_allies", False)
    show_enemies = cfg.get_bool("show_enemies", True)
    show_local_champ = cfg.get_bool("show_local_champ", False)


def winstealer_save_cfg(cfg):
    global show_allies, show_enemies, show_local_champ

    cfg.set_bool("show_allies", show_allies)
    cfg.set_bool("show_enemies", show_enemies)
    cfg.set_bool("show_local_champ", show_local_champ)


def winstealer_draw_settings(game, ui):
    global show_allies, show_enemies, show_local_champ

    show_allies = ui.checkbox("Show overlay on allies", show_allies)
    show_enemies = ui.checkbox("Show overlay on enemies", show_enemies)
    show_local_champ = ui.checkbox("Show overlay on self", show_local_champ)
