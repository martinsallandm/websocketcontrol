import numpy as np

from ControlLib import RemoteControl, Control


class PIDController(Control):

    def __init__(self, Kp, Ki=0., Kd=0., T=0.3, order=3):

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.I = 0.

        self.IAE = 0.
        self.ISE = 0.
        self.ITAE = 0.

        self.alphas = np.array([0.4, 0.4, 0.2])
        self.etas = np.zeros_like(self.alphas)
        self.GoodHart = np.dot(self.alphas, self.etas)

        super().__init__(T, order)

    def control(self):

        P = self.Kp * self.e(0)
        self.I = self.I + self.Ki * self.e(0) * self.T
        D = self.Kd * (self.e(0) - self.e(-1))
        return P + self.I + D

    def error_metrics(self):
        e = self.e(0)
        u = self.u(0)

        self.IAE += np.abs(e)
        self.ISE += e**2
        self.ITAE += self.time * np.abs(e)

        self.etas[0] += u
        self.etas[1] += (u - self.etas[0])**2
        self.etas[2] += np.abs(e)

        self.etas *= self.time

        self.GoodHart = np.dot(self.alphas, self.etas)

        return {
            "IAE": "%.2f" % self.IAE,
            "ISE": "%.2f" % self.ISE,
            "ITAE": "%.2f" % self.ITAE,
            "GoodHeart": "%.2f" % self.GoodHart
        }


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
