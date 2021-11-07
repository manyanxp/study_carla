
# -*- utf-8 -*-
# !/usr/bin/env python

import carla
import random
import pygame
import numpy as np
import queue


class CarlaSyncMode(object):
    def __init__(self, world, *sensors, **kwargs):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / kwargs.get('fps', 20)
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.frame = self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data


def draw_image(surface, image, blend=False):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    if blend:
        image_surface.set_alpha(100)
    surface.blit(image_surface, (0, 0))


def get_font():
    fonts = [x for x in pygame.font.get_fonts()]
    default_font = 'ubuntumono'
    font = default_font if default_font in fonts else fonts[0]
    font = pygame.font.match_font(font)
    return pygame.font.Font(font, 14)


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                return True
    return False

from utils.test_pid import PID
import math
import pandas as pd


def get_throttle(speed, max_speed):
    # pid = s3.PID(0.10,0.0001,1.3)
    pid = PID(0.2, 0.0012, 10)
    # pid_speed = PID(0.1, 0.00012, 1.3)
    pid.update_speed_error(speed, max_speed)
    throttle = pid.total_error()
    # print('throttle[{}] speed[{}]'.format(throttle, speed))
    if throttle > 1.0:
        throttle = 1.0
    else:
        throttle = throttle - 0.1

    return throttle / 10


def get_speed(vehicle):
    v = vehicle.get_velocity()
    return (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2))


def get_radian(x, y, x2, y2):
    radian = math.atan2(y2 - y, x2 - x)
    return radian


def draw_waypoint_union(debug, w0, color=carla.Color(255, 0, 0), lt=0):
    debug.draw_point(w0, 0.5, color, lt, False)


def get_k(x, y):
    return (2 * x) / ((x ** 2) + (y ** 2))


def get_steer(wb, k, v):
    w = v * k
    s = (wb * w) / v
    # print(s)
    if s > -1 and s < 1:
        steer = math.asin(s)
    else:
        steer = 0
    return steer


def get_waypoints_from_distance(debug, map, vehicle_location, distance):
    wps = []
    waypoint = map.get_waypoint(vehicle_location, lane_type=(carla.LaneType.Driving))
    wps.append(waypoint)
    waypoint = random.choice(waypoint.next(1.0))
    # print("距離 {}".format(waypoint.transform.location.distance(vehicle_location)))
    total_distance = 0
    while waypoint.transform.location.distance(vehicle_location) < distance:
        waypoint = random.choice(waypoint.next(1.0))
        # waypoint = waypoint.next(1.0)
        wps.append(waypoint)
        total_distance = waypoint.transform.location.distance(vehicle_location)
        draw_waypoint_union(debug, waypoint.transform.location, lt=1)

    return (wps, total_distance)


def transform_waypoints_to_axsis(waypoints):
    X = []
    Y = []
    for waypoint in waypoints:
        X.append(waypoint.transform.location.x)
        Y.append(waypoint.transform.location.y)
    return (X, Y)


def main():
    actor_list = []
    pygame.init()

    display = pygame.display.set_mode(
        (640, 480),
        pygame.HWSURFACE | pygame.DOUBLEBUF)
    font = get_font()
    clock = pygame.time.Clock()

    client = carla.Client('localhost', 2000)
    client.set_timeout(60.0)

    world = client.load_world('Town01')
    # world = client.get_world()

    try:
        m = world.get_map()
        start_pose = random.choice(m.get_spawn_points())
        waypoint = m.get_waypoint(start_pose.location, lane_type=(carla.LaneType.Driving))

        blueprint_library = world.get_blueprint_library()

        vehicle = world.spawn_actor(
            random.choice(blueprint_library.filter('model3')),
            start_pose)
        actor_list.append(vehicle)
        # 自分で車両コントロールしたいなら、物理シミュレーションを有効にする。
        # Flaseは無効、Trueは有効
        # これが無効だと、スロットル調整しても、車両が動かない。
        # vehicle.set_simulate_physics(False)

        camera_rgb = world.spawn_actor(
            blueprint_library.find('sensor.camera.rgb'),
            carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15)),
            attach_to=vehicle)
        actor_list.append(camera_rgb)

        camera_semseg = world.spawn_actor(
            blueprint_library.find('sensor.camera.semantic_segmentation'),
            carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15)),
            attach_to=vehicle)
        actor_list.append(camera_semseg)

        debug = world.debug
        next_waypoint = random.choice(waypoint.next(1.0))
        # draw_waypoint_union(debug, next_waypoint.transform.location, lt=1)
        next_p = []
        next_p.append(next_waypoint)
        # Create a synchronous mode context.
        with CarlaSyncMode(world, camera_rgb, camera_semseg, fps=21) as sync_mode:
            while True:
                if should_quit():
                    return
                clock.tick()

                # Advance the simulation and wait for the data.
                snapshot, image_rgb, image_semseg = sync_mode.tick(timeout=2.0)

                # Choose the next waypoint and update the car location.
                # waypoint = random.choice(waypoint.next(1.5))
                # vehicle.set_transform(waypoint.transform)
                # if vehicle.get_location() != next_waypoint.transform.location:
                # transform = next_waypoint.transform
                # angle = math.atan2(transform.location.x, transform.location.y)
                print('Vehicle Location {}'.format(vehicle.get_location()))
                print('Next Waypoint {}'.format(next_waypoint.transform.location))

                waypoints = get_waypoints_from_distance(debug, m, vehicle.get_location(), 30)
                X, Y = transform_waypoints_to_axsis(waypoints[0])

                param = np.polyfit(Y, X, 2)
                print("取得したWaypointの数 {} 距離 {} 式 {}".format(len(waypoints[0]), waypoints[1], param))

                # steer = angle
                speed = get_speed(vehicle)

                X = next_waypoint.transform.location.x - vehicle.get_location().x
                Y = next_waypoint.transform.location.y - vehicle.get_location().y

                k = get_k(X / 100, Y / 100)
                if speed > 0:
                    steer = get_steer(251.106 / 100, param[0], (speed / 3.6))
                else:
                    steer = 0

                try:
                    print('操舵角 {} 曲率 {} 曲率半径 {} 時速 {}'.format(steer, param[0], 1 / param[0], speed))
                except ZeroDivisionError:
                    print('操舵角 {} 曲率 {} 曲率半径 {} 時速 {}'.format(steer, param[0], np.nan, speed))

                throttle = get_throttle(speed, 100.0)
                control = vehicle.get_control()
                if throttle > 0.0:
                    control.throttle = min(control.throttle + throttle, 1)
                else:
                    control.throttle = 0.0

                control.steer = steer
                control.manual_gear_shift = False
                control.gear = 1
                vehicle.apply_control(control)

                # print('Next Point : {}'.format(X))
                # next_waypoint = random.choice(next_waypoint.next(1.0))
                # draw_waypoint_union(debug, next_waypoint.transform.location, lt=1)
                # else:
                #    print('Next!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

                next_p.append(next_waypoint)

                # print("throttle {} steer {} brake = {} hand_brake {}  reverse {} manual_gear_shift {}  gear {}".format(control.throttle, control.steer, control.brake, control.hand_brake, control.reverse, control.manual_gear_shift, control.gear))
                # print("speed = {} throtle = {}".format(speed, throttle))

                image_semseg.convert(carla.ColorConverter.CityScapesPalette)
                fps = round(1.0 / snapshot.timestamp.delta_seconds)

                # Draw the display.
                draw_image(display, image_rgb)
                draw_image(display, image_semseg, blend=True)
                display.blit(
                    font.render('% 5d FPS (real)' % clock.get_fps(), True, (255, 255, 255)),
                    (8, 10))
                display.blit(
                    font.render('% 5d FPS (simulated)' % fps, True, (255, 255, 255)),
                    (8, 28))
                display.blit(
                    font.render('% 5d throttle' % control.throttle, True, (255, 255, 255)),
                    (8, 46))
                display.blit(
                    font.render('% 5d speed (km/h)' % speed, True, (255, 255, 255)),
                    (8, 64))
                pygame.display.flip()

    finally:

        print('destroying actors.')
        for actor in actor_list:
            actor.destroy()

        pygame.quit()
        print('done.')


if __name__ == '__main__':

    try:

        main()

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')