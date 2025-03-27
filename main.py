from enum import Enum


class SensorType(Enum):
    DIGI = 0
    ANA = 1


class IO(Enum):
    INP = 0
    OUT = 1


class Sensors():
    def __init__(self, typeEnum, io, channel):
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
        pass

    def ReadPowerConsumption(self):
        pass


x = SensorInput(SensorType.DIGI, IO.INP, 1)
print(x.channel)
