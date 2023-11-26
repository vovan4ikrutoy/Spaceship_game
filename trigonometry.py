import math

import pygame


def angle_from_to_point(point1: (int, int), point2: (int, int)):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]
    ans = 0
    if x == 0:
        x = 0.01
    ans = 0
    if x >= 0 and y >= 0:
        ans = -math.degrees(math.atan(y/x))
    elif x >= 0 and y <= 0:
        ans = -math.degrees(math.atan(y/x))
    elif x <= 0 and y >= 0:
        ans = -math.degrees(math.atan(y/x)) + 180
    elif x <= 0 and y <= 0:
        ans = -math.degrees(math.atan(y/x)) + 180
    if ans < 0:
        ans = 270 + (90 - abs(ans))
    return ans


def calculate_rects(count, box_size: int, x_offset):
    ans = []
    for i in range(1, 5):
        if count <= math.pow(i, 2):
            res = i
            break
    x = 0
    y = 0
    for i in range(count):
        ans.append(pygame.Rect((x_offset + (box_size / res) * x, (box_size / res) * y), (box_size / res, box_size / res)))
        x += 1
        if x >= res:
            x = 0
            y += 1
    return ans


def distance_between_points(point1, point2):
    return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point2[1] - point1[1], 2))


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))