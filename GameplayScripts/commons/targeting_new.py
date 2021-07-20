from winstealer import *
from enum import Enum
from commons import skills


class Target(Enum):
    ClosestToPlayer = 0
    LowestHealth = 1
    MostFed = 2


class TargetingConfig:
    targets = [Target.ClosestToPlayer, Target.LowestHealth, Target.MostFed]
    targeting_lambdas = {
        Target.ClosestToPlayer: (lambda player, enemy: player.pos.distance(enemy.pos)),
        Target.LowestHealth: (lambda player, enemy: enemy.health),
        Target.MostFed: (
            lambda player, enemy: -sum([item.cost for item in enemy.items])
        ),
    }

    selected = 0
    target_minions = False
    target_jungle = False

    def draw(self, ui):
        ui.separator()
        self.selected = ui.listbox(
            "Target", [str(target)[7:] for target in self.targets], self.selected
        )

    def get_target(self, game, range):
        player = game.player

        target_info = self.targets[self.selected]
        target = self.find_target(
            game, game.champs, range, self.targeting_lambdas[target_info]
        )
        return target

    def find_target(self, game, array, range, value_extractor):
        target = None
        min = 99999999
        val = 0
        for obj in array:
            if (
                not obj.is_alive
                or not obj.is_visible
                or obj.is_ally_to(game.player)
                or game.isChatOpen
                or obj.isTargetable
            ):
                continue

            range_calc = (
                game.distance(game.player, obj)
                - game.player.gameplay_radius
                - obj.gameplay_radius
            )

            val = value_extractor(game.player, obj)

            if val < min:
                min = val
                target = obj

        return target

    def load_from_cfg(self, cfg):
        self.selected = cfg.get_int("targeting_target", 0)

    def save_to_cfg(self, cfg):
        cfg.set_int("targeting_target", self.selected)
