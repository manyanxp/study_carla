import matplotlib.pyplot as plt


class PID(object):
    def __init__(self, Kp_, Ki_, Kd_):
        self.Kp = Kp_
        self.Ki = Ki_
        self.Kd = Kd_
        self.p_error = 0.0
        self.i_error = 0.0
        self.d_error = 0.0
        self.init_d = False
        self.prev_cte = 0.0

    def update_speed_error(self, set_s, desired):
        self.p_error = (desired - set_s)
        if self.init_d is False:
            self.d_error = self.p_error
            self.init_d = True
            self.prev_cte = self.p_error
        else:
            self.d_error = self.p_error - self.prev_cte
            self.prev_cte = self.p_error

        self.i_error += self.p_error

    def total_error(self):
        return (self.Kp * self.p_error) + (self.Ki * self.i_error) + (self.Kd * self.d_error)


def main():
    pid_speed = PID(0.2, 0.0012, 10)
    # pid_speed = PID(0.1, 0.00012, 1.3)
    max_speed = 100.0
    speeds = []
    speed = 0
    throttle = 0.0
    for time in range(0, 1000):
        pid_speed.update_speed_error(speed, max_speed)
        throttle = pid_speed.total_error()

        if throttle > 1.0:
            throttle = 1.0

        if speed < max_speed:
            print("throttle = {} speed = {}".format(throttle, speed))

        speed = speed + throttle

        speeds.append(speed)

    plt.axhline(max_speed, color="b", linestyle="--")
    plt.xlim(0, 1000)
    plt.ylim(0, max_speed + 10)
    plt.xlabel("Time[sec.]")
    plt.ylabel("km/h")
    plt.plot(speeds)
    plt.show()


if __name__ == '__main__':
    main()