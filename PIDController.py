from ControlLib import RemoteControl, Control


class PIDController(Control):

    def __init__(self, Kp, Ki=0., Kd=0., T=0.3, order=3):

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.I = 0.

        super().__init__(T, order)

    def control(self):

        P = self.Kp * self.e(0)
        self.I = self.I + self.Ki * self.e(0) * self.T
        D = self.Kd * (self.e(0) - self.e(-1))
        return P + self.I + D


class PI_DController(PIDController):

    def __init__(self, Kp, Ki=0, Kd=0, T=0.3, order=3):
        super().__init__(Kp, Ki, Kd, T, order)

    def control(self):
        P = self.Kp * self.e(0)
        self.I = self.I + self.Ki * self.e(0) * self.T
        D = self.Kd * (self.y(0) - self.y(-1))
        return P + self.I + D


class I_PDController(PIDController):

    def __init__(self, Kp, Ki=0, Kd=0, T=0.3, order=3):
        super().__init__(Kp, Ki, Kd, T, order)

    def control(self):
        P = self.Kp * self.y(0)
        self.I = self.I + self.Ki * self.e(0) * self.T
        D = self.Kd * (self.y(0) - self.y(-1))
        return P + self.I + D


if __name__ == "__main__":

    pid_controller = PIDController(Kp=8.23, Ki=31.35, Kd=0.54, T=0.01, order=3)
    rc = RemoteControl(pid_controller)
    rc.run()
