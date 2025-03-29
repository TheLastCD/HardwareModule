import re

from enum import Enum


class SensorType(Enum):
    DIGI = 0
    ANA = 1


class IO(Enum):
    INP = 0
    OUT = 1


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


"""


"""


class Sensors():
    """
        Sensor super class to handle returns of object identity
        Sensors have the following attributes that we need to keep track of:
            is it powered on
            what is the supplied power



    """

    def __init__(self, typeEnum, io, channel):
        """
            args:
                typeEnum:   Enum defining the type of sensor, either digital or analogue
                io:         define whether sensor is on an input or an output
                Channel:    which channel is the sensor on, in real world usecase this would likely be a gpio pin or more specific hardware address
        """

        # default state of the sensors that are agnostic to what type the sensor is
        self.sensorSate = {"Enabled": 0,
                           "SuppliedPower": 0,
                           }
        self.sensorType = typeEnum
        self.IO = io
        self.channel = channel

    # Simple Returns for REST like structure
    def returnChannel(self):
        return self.channel

    def returnIO(self):
        return self.IO

    def returnSensorType(self):
        return SensorType


class SensorInput(Sensors):
    def __init__(self, typeEnum, io, channel):
        super().__init__(typeEnum, io, channel)

    def returnSensorState(self):
        """
            notes: depending on return case could either be digi or ana

        """
        pass


class SensorOutput(Sensors):
    def __init__(self, typeEnum, io, channel):
        super().__init__(typeEnum, io, channel)

    def changePsuState(self, on: bool):
        """
            args:
                on: are we setting the sensor on
        """
        pass

    def ReadPowerConsumption(self):
        pass


class Module():
    def SensorFactory(self, Dict):
        for key, val in Dict:
            print(key, val)

    def __init__(self, sensorDict):
        self.SensorFactory(sensorDict)

    def ResponseGenerator(self):

        pass


# x = SensorInput(SensorType.DIGI, IO.INP, 1)
# print(x.channel)


sensorDict = {
    "Digi0": 0,
    "Digi1": 1,
    "Ana0": 2,
    "Ana1": 3,


}


class ProtocolHandler():
    def __init__(self):
        pass

    def ReadInput(self):
        inp = input("> ")
        return inp

    def ProcessInput(self, inp):
        pattern = r"\^O\s\w+\s\\n"

        if re.fullmatch(pattern, inp):
            print(inp)
        else:
            return False
