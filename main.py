from enum import Enum


class SensorType(Enum):
    DIGI = 0
    ANA = 1


class IO(Enum):
    INP = 0
    OUT = 1


class Sensors():
    """
        Sensor super class to handle returns of object identity


    """

    def __init__(self, typeEnum, io, channel):
        """
            args:
                typeEnum:   Enum defining the type of sensor, either digital or analogue
                io:         define whether sensor is on an input or an output
                Channel:    which channel is the sensor on, in real world usecase this would likely be a gpio pin or more specific hardware address
        """
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
    def __init__(self):
        pass

    def SensorFactory(self):
        pass


x = SensorInput(SensorType.DIGI, IO.INP, 1)
print(x.channel)


sensoreDict = {
    Digi0: 0,
    Digi1: 1,
    Ana0: 2,
    Ana1: 3,


}
