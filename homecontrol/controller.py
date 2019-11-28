STATE_NA = "not applicable"
STATE_ON = "on"
STATE_OFF = "off"


class Controller:
    controllers = []

    def __init__(self):
        self.state = "na"

    @staticmethod
    def update():
        for control in Controller.controllers:
            last_state = control.state
            control.update()

            if control.state != last_state:
                if control.state == STATE_ON:
                    control.turn_on()
                elif control.state == STATE_OFF:
                    control.turn_off()
