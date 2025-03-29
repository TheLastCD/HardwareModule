# ---------------------------------------------------------------------------------
#
#   imports
#
# ---------------------------------------------------------------------------------


import re

from enum import Enum

# ---------------------------------------------------------------------------------
#
#   Enums
#
# ---------------------------------------------------------------------------------


class SensorType(Enum):
    DIGI = 0
    ANA = 1


class ProtocolCommands(Enum):
    ECHO = "E"  # Only requires Sequence Number
    INPUT = "I"  # Read inputs or return current output value on a given output
    OUTPUT = "O"  # sets the value of a given output
    PUS = "P"  # Only requires sequence number


class ProtocolReturnCode(Enum):
    """
        return codes are a fixed size coming back in
    """
    OK = "OK_"
    ERROR = "ERR"
    RANGE = "RNG"


# ---------------------------------------------------------------------------------
#
#   Sensor Emulation
#
# ---------------------------------------------------------------------------------


class Sensors():
    """
        Sensor super class to handle returns of object identity
        Sensors have the following attributes that we need to keep track of:
            is it powered on
            what is the supplied power



    """

    def __init__(self, typeEnum, channel):
        """
            args:
                typeEnum:   Enum defining the type of sensor, either digital or analogue
                Channel:    which channel is the sensor on, in real world usecase this would likely be a gpio pin or more specific hardware address
        """

        # default state of the sensors that are agnostic to what type the sensor is
        self.sensorState = {"Enabled": 0,
                            "SuppliedPower": 0,
                            }
        self.sensorType = typeEnum
        self.channel = channel

    # Simple Returns for REST like structure
    def returnChannel(self):
        return self.channel

    def returnSensorType(self):
        return SensorType

    def returnSensorState(self):
        """
            notes: depending on return case could either be digi or ana

        """

        return 0

    def changePsuState(self, on: bool):
        """
            args:
                on: are we setting the sensor on


            notes:
                extra habndling would be needed if there where an actual server
        """
        self.sensorState["Enabled"] = on

        # this is hear for emulation purposes only, in production we'd receive a message from the sensor stating that its power draw had gone to 0
        # the reason why we react when the sensor tells us is to ensure that what is represented here is accurate to whats happening on the hardware
        # Likely through a form of SSE
        if on is False:
            self.sensorState["SuppliedPower"] = 0

        else:
            self.sensorState["SuppliedPower"] = 20.0


class SensorDigital(Sensors):
    def __init__(self, typeEnum, channel):
        super().__init__(typeEnum, channel)
        digitalAttributes = {
            "LightSensor": 0,
            "MotionSensor": 0,
        }
        self.sensorState.update(digitalAttributes)


class SensorAnalogue(Sensors):
    def __init__(self, typeEnum, channel):
        super().__init__(typeEnum, channel)
        analogueAttributes = {
            "LightSensorPower": 0,
            "LightSensorDistance": 0,
        }
        self.sensorState.update(analogueAttributes)

    def ReadPowerConsumption(self):
        pass


# ---------------------------------------------------------------------------------
#
#   Microcontroller Module Emulation
#
# ---------------------------------------------------------------------------------

class Module():
    def SensorFactory(self, sensorDict):
        sensors = []
        for key, val in sensorDict.items():
            print(f"Init sensor: {key}, type: {val[1]} on channel {val[0]}")

            if val[1] == SensorType.ANA:
                sensors.append(SensorAnalogue(val[1], val[0]))
            else:
                sensors.append(SensorDigital(val[1], val[0]))

        return sensors

    def __init__(self, sensorDict):
        self.sensors = self.SensorFactory(sensorDict)

    def sendEvent(self, sensor, msg):
        """
            args:
                sensor: sensor object to send the command to
                msg: any variables if applicable to pass on
            desc:
                Mimics the sending of an event to the sensor
        """

        return 0

    def receiveEvent(self, inp):
        """
            args:
                inp: the command received to act on
        """
        pattern = r'^\^.*\n$'  # simple regex to filter out incorrect commands

        if re.fullmatch(pattern, inp):
            # due to arbirary size of Sequence number we struggle to do proper slicing by index
            inpSplit = inp.split()

            # as the regex filters out an missing ^ i can ignore it when slicing
            opcode = inp[1]
            seqNum = inpSplit[1]

            # process and slice the incoming sensor command into output type and channel
            sensorType = inpSplit[2][0]
            sensorDirection = inpSplit[2][1]
            sensorChannel = inpSplit[2][2:]

            print(f"""Received opcode {opcode}
    Received SS {seqNum}
    Received x {sensorType}
    Received d {sensorDirection}
    Received nn {sensorChannel}""")

        else:
            # this feels correct as is it assumed that none of the input was correct therefore no SS etc??
            print("ERR")


sensorDict = {
    "Digi0": [0, SensorType.DIGI],
    "Digi1": [1, SensorType.DIGI],
    "Ana0": [2, SensorType.ANA],
    "Ana1": [3, SensorType.ANA]

}
x = Module(sensorDict)


x.receiveEvent("^O 2A AO04 8C21\n")

while (True):
    # this ensures the \n is properly received
    cli = input("> ").encode('utf-8').decode('unicode_escape')
    x.receiveEvent(cli)
