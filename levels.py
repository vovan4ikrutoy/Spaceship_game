import modules
import ships


class Level:
    def __init__(self, number, money, enemys, hint=''):
        self.number = number
        self.money = money
        self.enemys = enemys
        self.hint = hint


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
                                                  mid_modules=[modules.ShieldBooster], ai_type='close') for _ in
                              range(4)], hint='Попробуйте держать дистанцию и наносить урон дальнобойным оружием'),
              Level(3, 3000, [ships.CarrierShip((8000, 6000), 'enemy',
                                                high_modules=[modules.Flamethrower, modules.MediumRocketLauncher,
                                                              modules.MediumRocketLauncher],
                                                mid_modules=[],
                                                low_modules=[modules.ArmorRein for _ in range(2)],
                                                ai_type='close')],
                    hint='Средняя ракета не может поразить ускоренный разведчик'),
              Level(4, 3769, [ships.MinerShip((9300, 5750), 'enemy',
                                              high_modules=[modules.MediumRailgun for _ in range(2)]),
                              ships.MinerShip((9300, 6000), 'enemy',
                                              high_modules=[modules.MediumRailgun for _ in range(2)]),
                              ships.MinerShip((9300, 6250), 'enemy',
                                              high_modules=[modules.MediumRailgun for _ in range(2)]),
                              ships.DestroyerShip((8500, 6000), 'enemy',
                                                  high_modules=[modules.SmallRocketLauncher for _ in range(3)]),
                              ships.DestroyerShip((8500, 6001), 'enemy',
                                                  high_modules=[modules.SmallRocketLauncher for _ in range(3)]),
                              ships.DestroyerShip((8500, 6002), 'enemy',
                                                  high_modules=[modules.SmallRocketLauncher for _ in range(3)]),
                              ships.DestroyerShip((8500, 6003), 'enemy',
                                                  high_modules=[modules.SmallRocketLauncher for _ in range(3)]),
                              ships.DestroyerShip((8500, 6004), 'enemy',
                                                  high_modules=[modules.SmallRocketLauncher for _ in range(3)]),
                              ships.DestroyerShip((8500, 6005), 'enemy',
                                                  high_modules=[modules.SmallRailgun for _ in range(3)]),
                              ships.DestroyerShip((8500, 6006), 'enemy',
                                                  high_modules=[modules.SmallRailgun for _ in range(3)]),
                              ships.ScoutShip((8000, 6000), 'enemy', high_modules=[modules.IonGun],
                                              low_modules=[modules.Acceleration]),
                              ships.ScoutShip((8000, 6001), 'enemy', high_modules=[modules.IonGun],
                                              low_modules=[modules.Acceleration]),
                              ships.ScoutShip((8000, 6002), 'enemy', high_modules=[modules.IonGun],
                                              low_modules=[modules.Acceleration]),
                              ships.ScoutShip((8000, 6003), 'enemy', high_modules=[modules.IonGun],
                                              low_modules=[modules.Acceleration]),
                              ships.ScoutShip((8000, 6004), 'enemy', high_modules=[modules.IonGun],
                                              low_modules=[modules.Acceleration])],
                    hint='Уровень можно пройти с любой конфигурацией большого корабля, попробуй их все!'),
              Level(5, 5000, [ships.CarrierShip((8500, 5500), 'enemy',
                                                [modules.MediumRailgun for _ in range(3)],
                                                [modules.ShieldBooster],
                                                [modules.ShieldReinforcement]),
                              ships.CarrierShip((8500, 6500), 'enemy',
                                                [modules.MediumRailgun for _ in range(3)],
                                                [modules.ShieldBooster],
                                                [modules.ShieldReinforcement]),
                              ships.ScoutShip((8000, 6000), 'enemy',
                                              [modules.SmallRailgun], [], []),
                              ships.ScoutShip((8000, 6000), 'enemy',
                                              [modules.SmallRailgun], [], []),
                              ships.ScoutShip((8000, 6000), 'enemy',
                                              [modules.SmallRailgun], [], []),
                              ships.ScoutShip((8000, 6000), 'enemy',
                                              [modules.SmallRailgun], [], [])
                              ], hint=r'¯\_☹_/¯')]
    for i in range(0):
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
