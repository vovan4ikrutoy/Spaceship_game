import math

import pygame


def angle_from_to_point(point1: (int, int), point2: (int, int)):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]
    if x == 0:
        x = 0.01
    ans = 0
    if x >= 0 and y >= 0:
        ans = -math.degrees(math.atan(y/x))
    elif x >= 0 >= y:
        ans = -math.degrees(math.atan(y/x))
    elif x <= 0 <= y:
        ans = -math.degrees(math.atan(y/x)) + 180
    elif x <= 0 and y <= 0:
        ans = -math.degrees(math.atan(y/x)) + 180
    if ans < 0:
        ans = 270 + (90 - abs(ans))
    return ans


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def calculate_res(count):
    for i in range(1, 4):
        if count <= math.pow(i, 2):
            return i
    raise ZeroDivisionError('Well... f*ck. Error from calculate_res? Seriously?')


def calculate_rects(count, box_size: int, x_offset):
    ans = []
    res = calculate_res(count)
    x = 0
    y = 0
    for i in range(count):
        ans.append((pygame.Rect((x_offset + ((box_size + 10) / res) * x, ((box_size + 10) / res) * y),
                                (box_size / res, box_size / res)), i))
        x += 1
        if x >= res:
            x = 0
            y += 1
    return ans


def distance_between_points(point1, point2):
    return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point2[1] - point1[1], 2))


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))
