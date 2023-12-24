import modules
from ships import Ship, ShipLevelHolder


class Level:
    def __init__(self, number, money, enemys, bg=None, player_pos=(500, 0)):
        self.number = number
        self.money = money
        self.enemys = enemys
        self.bg = bg
        self.player_pos = player_pos


def init_levels():
    levels = []
    for _ in range(12):
        levels.append(Level(1, 500, [
            ([ShipLevelHolder(name='enemy ship', weight=20, max_speed=2, max_shield=1500, max_armor=800, max_hull=350,
                              img='textures/ships/test_enemy.png', pos=(300, 0),
                              team='enemy', scale=3,
                              high_modules=[modules.StatisWebfier() for _ in range(3)],
                              mid_modules=[modules.SmallShieldBooster() for _ in range(4)],
                              high_module_slots=[(50, 0), (-63, 50), (-63, -50)])], (2000, 0))]))
    return levels
