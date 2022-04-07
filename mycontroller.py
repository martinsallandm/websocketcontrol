from ControlLib import Control, RemoteControl


class MyControllerName(Control):

    def control(self):
        """
        Return the control signal.
        You can access the error at instant 0, -1, and -2 as:
        self.e(0), self.e(-1) and self.e(-2) respectively

        Obs.: To access more errors, create your controller with the
        command:
        controller = MyControllerName(T, n)
        where T is the sampling time (normally 0.3) and n is the order
        of the controller (how many errors you can access)
        For instance:

        controller = MyControllerName(0.5, 6)

        Will use a controller with 0.5s sampling time and will access
        from self.e(0) up to self.e(-5)
        """

        # in this simple controller, it applies a control signal that
        # is 90% the current error

        u0 = 0.9 * self.e(0)

        return u0


controller = MyControllerName(0.2, 3)
rc = RemoteControl(controller)
rc.run()
