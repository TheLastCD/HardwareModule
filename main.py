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
    DIGI = "D"
    ANA = "A"


class SensorDirection(Enum):
    INPUT = "I"
    OUTPUT = "O"


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
        return self.sensorType

    def changePsuState(self, on):
        """
            args:
                on: are we setting the sensor on


            notes:
                extra habndling would be needed if there where an actual server
        """
        self.sensorState["Enabled"] = on
        return ProtocolReturnCode.OK.value

    def ReadSensor(self):
        """
            desc:
                Empty function as it will be overridden in subclasses

        """
        pass


class SensorDigital(Sensors):
    def __init__(self, typeEnum, channel):
        super().__init__(typeEnum, channel)
        digitalAttributes = {
            "LightSensor": 0,
            "MotionSensor": 0,
        }
        self.sensorState.update(digitalAttributes)

    def ReadSensor(self, inp):
        if inp == SensorDirection.INPUT.value:
            return "1"  # imagine this is a call to the server
        else:
            # return the power being outputted
            return self.sensorState["Enabled"]


class SensorAnalogue(Sensors):
    def __init__(self, typeEnum, channel):
        super().__init__(typeEnum, channel)
        analogueAttributes = {
            "LightSensorPower": 0,
            "LightSensorDistance": 0,
        }
        self.sensorState.update(analogueAttributes)

    def ReadSensor(self, inp):
        if inp == SensorDirection.INPUT.value:
            return "000F999B"  # imagine this is a call to the server/ sensor protocol handler
        else:
            # return the power being outputted
            return self.sensorState["SuppliedPower"]


# ---------------------------------------------------------------------------------
#
#   Microcontroller Module Emulation
#
# ---------------------------------------------------------------------------------

class Module():
    def SensorFactory(self, sensorDict):
        anasensors = []
        digisensors = []
        for key, val in sensorDict.items():
            print(f"Init sensor: {key}, type: {val[1]} on channel {val[0]}")

            if val[1] == SensorType.ANA:
                anasensors.append(SensorAnalogue(val[1], val[0]))
            else:
                digisensors.append(SensorDigital(val[1], val[0]))

        return (anasensors, digisensors)

    def __init__(self, sensorDict):
        self.sensors = self.SensorFactory(sensorDict)
        self.powerState = 0  # is the controller powered on only exists as part of the emulation

    def returnModulePowerState(self):
        if self.powerState == 0:
            return "OFF"

        else:
            return "PWR"

    def setModulePowerState(self, PWR):
        self.powerState = PWR

    def receiveEvent(self, inp):
        """
            args:
                inp: the command received to act on
        """
        pattern = r'^\^.*\n$'  # simple regex to filter out incorrect commands only covers the ^ and \n

        if re.fullmatch(pattern, inp):
            try:
                # due to arbirary size of Sequence number we struggle to do proper slicing by index
                inpSplit = inp.split()

                opcode = inp[1]  # Opcode is always here
                seqNum = inpSplit[1]
                if opcode == ProtocolCommands.ECHO.value:
                    self.EchoHandler(seqNum)
                elif opcode == ProtocolCommands.PUS.value:
                    self.PowerUpHandler(seqNum, inpSplit[2])
                else:
                    # process and slice the incoming sensor command into chunks can process
                    sensorType = inpSplit[2][0]
                    sensorDirection = inpSplit[2][1]
                    sensorChannel = int(inpSplit[2][2:], 16)
                    try:
                        sensorChannel = int(inpSplit[2][2:], 16)
                    except ValueError:
                        self.sendError(opcode=opcode, seqNum=seqNum)
                        return
                    if opcode == ProtocolCommands.INPUT.value:
                        self.InputHandler(seqNum,
                                          sensorType, sensorChannel, sensorDirection)

                    elif opcode == ProtocolCommands.OUTPUT.value:
                        self.OutputHandler(
                            seqNum, sensorType, sensorChannel, sensorDirection, int(inpSplit[3], 16))
            except IndexError:
                self.SendError(opcode=opcode, seqNum=seqNum)

        else:
            # i'm assuming that given how the regex works there maybe no sequencenumber
            self.SendError()
    # -------------------------------------------------------
    #
    #   handlers for the commands we're processing
    #
    # -------------------------------------------------------

    def EchoHandler(self, seqNum):
        print(rf"^E {seqNum} {ProtocolReturnCode.OK.value} {
              self.returnModulePowerState()}\n")

    def PowerUpHandler(self, seqNum, comm):
        self.setModulePowerState(comm)
        print(rf"^P {seqNum} {ProtocolReturnCode.OK.value}\n")

    def InputHandler(self, seqNum, sensorType, sensorChannel, sensorDirection):
        if sensorType == SensorType.ANA.value:
            for i in self.sensors[0]:
                if i.channel == sensorChannel:
                    print(rf"^I {seqNum} {ProtocolReturnCode.OK.value} {sensorType}{
                        sensorDirection}{sensorChannel} {i.ReadSensor(sensorDirection)}\n")
        elif sensorType == SensorType.DIGI.value:
            for i in self.sensors[1]:
                if i.channel == sensorChannel:
                    print(f"^I {seqNum} {ProtocolReturnCode.OK.value} {sensorType}{
                          sensorDirection}{sensorChannel} {i.ReadSensor(sensorDirection)}\n")

    def OutputHandler(self, seqNum, sensorType, sensorChannel, sensorDirection, comm):
        if sensorType == SensorType.ANA.value:
            for i in self.sensors[0]:
                if i.channel == sensorChannel:
                    print(rf"^O {seqNum} {i.ReadSensor(sensorDirection)}\n")
                    return

        elif sensorType == SensorType.DIGI.value:
            for i in self.sensors[1]:
                if i.channel == sensorChannel:
                    print(rf"^O {seqNum} {i.changePsuState(comm)}\n")
                    return
        self.SendError(opcode="^O", seqNum=seqNum,
                       retEnum=ProtocolReturnCode.RANGE.value)
    # -------------------------------------------------------
    #
    #   Error handling
    #
    # -------------------------------------------------------

    def SendError(self, opcode="^ERR", seqNum=None, retEnum=ProtocolReturnCode.ERROR.value):
        print(rf"{opcode} {seqNum if seqNum else 'NULL'} {retEnum}\n")


# dictionary goes: name/alias, relative channel (IE: analogue channel 1), sensortype
sensorDict = {
    "Digi0": [0, SensorType.DIGI],
    "Digi1": [1, SensorType.DIGI],
    "Ana0": [0, SensorType.ANA],
    "Ana1": [1, SensorType.ANA]

}
x = Module(sensorDict)


while (True):
    # this ensures the \n is properly received
    cli = input("> ").encode('utf-8').decode('unicode_escape')
    x.receiveEvent(cli)
