import carla
import math
from utils.test_pid import PID


def get_vector3d2speed(vehicle):
    """
    :param vehicle: carla.Location
    :return: Speed
    """
    v = vehicle.get_velocity()
    return (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2))


def get_radian(x, y, x2, y2):
    radian = math.atan2(y2 - y, x2 - x)
    return radian


def draw_waypoint_union(debug, w0, color=carla.Color(255, 0, 0), lt=0):
    debug.draw_point(w0, 0.5, color, lt, False)


def get_k(x, y):
    return (2 * x) / ((x ** 2) + (y ** 2))


def get_steer(wheel_base, k, v):
    w = v * k
    s = (wheel_base * w) / v
    # print(s)
    if s > -1 and s < 1:
        steer = math.asin(s)
    else:
        steer = 0
    return steer

def get_throttle(speed, max_speed):
    pid = PID(0.2, 0.0012, 10)
    pid.update_speed_error(speed, max_speed)
    throttle = pid.total_error()
    # print('throttle[{}] speed[{}]'.format(throttle, speed))
    if throttle > 1.0:
        throttle = 1.0
    else:
        throttle = throttle - 0.1

    return throttle / 10