import modules
import ships


class Level:
    def __init__(self, number, money, enemys, bg=None, player_pos=(500, 0)):
        self.number = number
        self.money = money
        self.enemys = enemys
        self.bg = bg
        self.player_pos = player_pos


def init_levels():
    levels = []
    for i in range(12):
        levels.append(Level(1, 500, [ships.ScoutShip((200, 0), 'player', high_modules=[modules.SmallRailgun, modules.SmallRailgun],
                                                     mid_modules=[modules.SmallShieldBooster])
                                     for _ in range(15)]))
        levels[-1].enemys.extend([ships.DestroyerShip((0, 0), 'player')])
        levels[-1].enemys.extend([ships.ScoutShip((1500, 0), 'enemy',
                                                  high_modules=[modules.SmallRailgun,
                                                                modules.SmallRailgun])
                                  for _ in range(5)])
        levels[-1].enemys.extend([ships.DestroyerShip((1500, 0), 'enemy',
                                                      high_modules=[modules.SmallRailgun,
                                                                    modules.SmallRailgun,
                                                                    modules.StatisWebfier])
                                  for _ in range(2)])
    return levels
