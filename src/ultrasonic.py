"""This module provides a class to read a range finder."""


# Imports
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class RangeFinder(object):

    IN_TO_CM_CONVERSION = 2.54
    use_units = None
    min_voltage = None
    voltage_range = None
    min_distance = None
    distance_range = None
    channel = None

    def __init__(self, chan):
        self.channel = wpilib.AnalogChannel(chan)
        self.channel.SetOversampleBits(4)
        self.channel.SetAverageBits(2)
        self.use_units = True
        self.min_voltage = 0.5
        self.voltage_range = 5.0 - self.min_voltage
        self.min_distance = 3.0
        self.distance_range = 60.0 - self.min_distance
        self.IN_TO_CM_CONVERSION = 2.54

    def get_voltage(self):
        #return self.channel.GetVoltage()
        return self.channel.GetAverageVoltage()

    def get_range_in_inches(self):
        if not self.use_units:
            return -1.0
        rng = self.get_voltage()
        if rng < self.min_voltage:
            return -2.0
        rng = (rng - self.min_voltage) / self.voltage_range
        rng = (rng * self.distance_range) + self.min_distance
        return rng

    def get_range_in_cm(self):
        rng = self.get_range_in_inches()
        rng = rng * self.IN_TO_CM_CONVERSION
        return rng

