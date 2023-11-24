import math


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


def middle_angle():
    return 1


def distance_between_points(point1, point2):
    return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point2[1] - point1[1], 2))


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))