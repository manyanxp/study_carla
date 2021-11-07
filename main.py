
# -*- utf-8 -*-
# !/usr/bin/env python

import random
import pygame
import numpy as np
import queue
import argparse

from utils.util import *


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


def parse_arg():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--generation',
        metavar='G',
        default='2',
        help='restrict to certain actor generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    argparser.add_argument(
        '--sync',
        action='store_true',
        help='Activate synchronous mode execution')
    argparser.add_argument(
        '--town',
        default="Town01",
        help='Town Name (default:Town01)'
    )
    argparser.add_argument(
        '--speed',
        type=int,
        default=20,
        help='Town Name (default:Town01)'
    )
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    return args


def main():
    args = parse_arg()

    actor_list = []
    pygame.init()

    display = pygame.display.set_mode(
        (640, 480),
        pygame.HWSURFACE | pygame.DOUBLEBUF)
    font = get_font()
    clock = pygame.time.Clock()

    client = carla.Client(args.host, args.port)
    client.set_timeout(60.0)

    world = client.load_world(args.town)
    # world = client.get_world()

    try:
        map = world.get_map()
        start_pose = random.choice(map.get_spawn_points())
        waypoint = map.get_waypoint(start_pose.location, lane_type=(carla.LaneType.Driving))

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
                speed = get_vector3d2speed(vehicle)

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

                throttle = get_throttle(speed, args.speed)
                control = vehicle.get_control()
                if throttle > 0.0:
                    control.throttle = min(control.throttle + throttle, 1)
                else:
                    control.throttle = 0.0

                control.steer = steer
                control.manual_gear_shift = False
                control.gear = 1
                vehicle.apply_control(control)

                next_p.append(next_waypoint)

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