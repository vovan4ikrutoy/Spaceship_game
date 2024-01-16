import modules
import ships


class Level:
    def __init__(self, number, money, enemys):
        self.number = number
        self.money = money
        self.enemys = enemys


def init_levels():
    levels = [Level(0, 450, [ships.ScoutShip((8000, 6000), 'enemy',
                                             high_modules=[modules.SmallRailgun], ai_type='close') for _ in
                             range(2)]),
              Level(1, 850, [ships.DestroyerShip((8000, 6000), 'enemy',
                                                 high_modules=[modules.SmallRailgun for _ in range(3)],
                                                 mid_modules=[modules.ShieldBooster], ai_type='close'),
                             ships.ScoutShip((8000, 6001), 'enemy',
                                             high_modules=[modules.SmallRailgun], ai_type='normal'),
                             ships.ScoutShip((8000, 6002), 'enemy',
                                             high_modules=[modules.SmallRailgun], ai_type='normal')
                             ]),
              Level(2, 1500, [ships.DestroyerShip((8000, 6000), 'enemy',
                                                 high_modules=[modules.SmallRailgun for _ in range(3)],
                                                 mid_modules=[modules.ShieldBooster], ai_type='close') for _ in range(5)]),
              Level(3, 6999, [])]
    for i in range(11):
        levels.append(Level(1, 500, []))
        levels[-1].enemys.extend([ships.ScoutShip((1500, 0), 'enemy',
                                                  high_modules=[modules.SmallRailgun])
                                  for _ in range(5)])
        levels[-1].enemys.extend([ships.DestroyerShip((1500, 0), 'enemy',
                                                      high_modules=[modules.SmallRailgun,
                                                                    modules.SmallRailgun,
                                                                    modules.StatisWebfier])
                                  for _ in range(2)])
    return levels
