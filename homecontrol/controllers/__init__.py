from .emma import ControlTurnOffEmma
from .general import ControlChristmasLightsWhenNotHome, ControlTurnOffLights
from .hallway import ControlHallCeiling, ControlPainting
from .kitchen import ControlMicro
from .livingroom import ControlBalls, ControlWindow
from .matteus import (
    ControlBamboo,
    ControlLedStrip,
    ControlMatteus,
    ControlMatteusTurnOff,
    ControlSpeakers,
)

# Emma
ControlTurnOffEmma()

# General
ControlChristmasLightsWhenNotHome()
ControlTurnOffLights()

# Hallway
ControlHallCeiling()
ControlPainting()

# Kitchen
ControlMicro()

# Livingroom
ControlBalls()
ControlWindow()

# Matteus
ControlSpeakers()
ControlMatteus()
ControlBamboo()
ControlLedStrip()
ControlMatteusTurnOff()
