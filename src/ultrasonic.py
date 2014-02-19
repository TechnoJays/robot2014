"""This module provides a class to read a range finder."""


# Imports
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class RangeFinder(object):
    """Get the distance to the nearest object."""

    volts_per_inch = None
    channel = None

    def __init__(self, chan):
        self.channel = wpilib.AnalogChannel(chan)
        self.channel.SetOversampleBits(4)
        self.channel.SetAverageBits(2)
        self.volts_per_inch = 5 / 512.0

    def get_voltage(self):
        return self.channel.GetAverageVoltage()

    def get_range_in_inches(self):
        rng = self.get_voltage()
        rng = rng / self.volts_per_inch
        return rng

    def get_range_in_feet(self):
        rng = self.get_range_in_inches() / 12.0
        return rng

