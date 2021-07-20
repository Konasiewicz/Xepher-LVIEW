from winstealer import *
from commons.skills import *
from commons.ByLib import *
import math


def IsRecalling(game, target) -> bool:
    recall = getBuff(game, "recall")
    if recall and buffIsAlive(game, recall):
        return True
    return False


# def GetDistanceSqr(p1, p2):
#     p2 = p2
#     d = p1.sub(p2)
#     d.z = (p1.z or p1.y) - (p2.z or p2.y)
#     return d.x * d.x + d.z * d.z


def IsUnderTurretEnemy(game, unit) -> bool:
    for turret in game.turrets:
        if turret.is_ally_to(game.player):
            continue
        range = turret.gameplay_radius + 750 + unit.gameplay_radius / 2
        dist = turret.pos.distance(unit.pos) - range
        if dist <= unit.gameplay_radius + 25:
            return True
    return False


def GetDistanceSqr(a, b):
    # if a.z != None and b.z != None:
    #     x = (a.x - b.x)
    #     z = (a.z - b.z)
    #     return x * x + z * z
    # else:
    x = a.x - b.x
    y = a.y - b.y
    return x * x + y * y


def GetDistance(p1, p2):
    squaredDistance = GetDistanceSqr(p1, p2)
    return math.sqrt(squaredDistance)


def isValidTarget(game, target, range):
    return (
        target
        and target.is_visible
        and target.is_alive
        and (not range or GetDistance(target.pos, game.player.pos) <= range)
    )


def ValidTarget(obj):
    return obj and obj.is_alive and obj.is_visible and obj.isTargetable


def getSkill(game, slot):
    skill = getattr(game.player, slot)
    if skill:
        return skill
    return None


def IsReady(game, skill) -> bool:
    return skill and skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0


def getBuff(target, name):
    buff = None
    for cBuff in target.buffs:
        if cBuff and cBuff.name == name:
            buff = cBuff
    return buff


def buffIsAlive(game, buff) -> bool:
    time = game.time
    if not buff or not buff.start_time or not buff.end_time:
        return False
    return buff.end_time > game.time


def RotateAroundPoint(v1, v2, angle):
    cos, sin = math.cos(angle), math.sin(angle)
    x = ((v1.x - v2.x) * cos) - ((v2.z - v1.z) * sin) + v2.x
    z = ((v2.z - v1.z) * cos) + ((v1.x - v2.x) * sin) + v2.z
    return Vec3(x, v1.y, z or 0)


def GetWallPosition(target, t_range):
    t_range = t_range or 400
    for i in range(0, 360, 45):
        angle = i * math.pi / 180
        targetPosition = target.pos
        targetRotated = Vec3(
            targetPosition.x + t_range, targetPosition.y, targetPosition.z
        )
        Wallid = RotateAroundPoint(targetRotated, targetPosition, angle)

        if GetDistance(Wallid, targetRotated) < t_range:
            return Wallid


def GetKitePosition(game, target):
    lastPos = None
    lastDist = float("inf")
    for i in range(0, 360, 22):
        angle = i * (math.pi / 180)

        myPos = game.player.pos
        tPos = target.pos

        rot = RotateAroundPoint(tPos, myPos, angle)
        pos = myPos.sub(myPos.sub(rot))
        game.draw_circle_world(pos, 30, 100, 1, Color.GREEN)
        if ValidTarget(target):
            for champ in game.champs:
                dist = GetDistance(target.pos, pos) / 2
                if target.pos.distance(pos) < lastDist:
                    lastDist = target.pos.distance(pos)
                    return pos
                else:
                    dist = GetDistance(target.pos, pos)
                    if target.pos.distance(pos) > lastDist:
                        lastDist = target.pos.distance(pos)
                        return pos
    return pos


def IsKnock(game, unit) -> bool:
    for buff in unit.buffs:
        bType = buff.type
        if bType == 29 or bType == 30:
            return True
    return False


def IsDanger(game, point) -> bool:
    val = False
    for missile in game.missiles:
        if not game.player.is_alive or missile.is_ally_to(game.player):
            continue
        if not is_skillshot(missile.name):
            continue
        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue
        if (
            game.point_on_line(
                game.world_to_screen(missile.start_pos),
                game.world_to_screen(missile.end_pos),
                game.world_to_screen(point),
                game.player.gameplay_radius * 1,
            )
            and game.is_point_on_screen(missile.pos)
        ):
            val = True
    return val


def draw_rect(game, start_pos, end_pos, radius, color):

    dir = Vec3(end_pos.x - start_pos.x, 0, end_pos.z - start_pos.z).normalize()

    left_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(90).scale(radius)
    right_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(-90).scale(radius)

    p1 = Vec3(
        start_pos.x + left_dir.x, start_pos.y + left_dir.y, start_pos.z + left_dir.z
    )
    p2 = Vec3(end_pos.x + left_dir.x, end_pos.y + left_dir.y, end_pos.z + left_dir.z)
    p3 = Vec3(end_pos.x + right_dir.x, end_pos.y + right_dir.y, end_pos.z + right_dir.z)
    p4 = Vec3(
        start_pos.x + right_dir.x, start_pos.y + right_dir.y, start_pos.z + right_dir.z
    )
    # getGlobalColor()
    # game.draw_triangle_world_filled(p1, p2, p3, color)
    # game.draw_triangle_world_filled(p1, p3, p4, color)
    game.draw_rect_world(p1, p2, p3, p4, 1, color)


def draw_triangle(game, radius, position, color, bold=1):
    a = Vec2(position.x + radius, position.y + radius / 2)
    b = Vec2(position.x - radius, position.y + radius / 2)
    c = Vec2(position.x, position.y - radius)

    game.draw_line(a, b, bold, color)
    game.draw_line(b, c, bold, color)
    game.draw_line(c, a, bold, color)


def VectorPointProjectionOnLineSegment(v1, v2, v):
    cx, cy, ax, ay, bx, by = v.x, v.z, v1.x, v1.z, v2.x, v2.z
    rL = ((cx - ax) * (bx - ax) + (cy - ay) * (by - ay)) / (
        (bx - ax) ** 2 + (by - ay) ** 2
    )
    pointLine = Vec3(ax + rL * (bx - ax), 0, ay + rL * (by - ay))
    rS = rL < 0 and 0 or (rL > 1 and 1 or rL)
    isOnSegment = rS == rL
    pointSegment = (
        isOnSegment and pointLine or Vec3(ax + rS * (bx - ax), 0, ay + rS * (by - ay))
    )
    return pointSegment, pointLine, isOnSegment


def IsImmobileTarget(unit) -> bool:
    for buff in unit.buffs:
        if buff and (
            buff.type == 5
            or buff.type == 11
            or buff.type == 29
            or buff.type == 24
            or buff.name == 10
        ):
            return True
    return False
