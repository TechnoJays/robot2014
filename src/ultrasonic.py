"""This module provides a class to read a range finder."""


# Imports
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class RangeFinder(object):
    """Get the distance to the nearest object."""

    _volts_per_inch = None
    _channel = None

    def __init__(self, chan):
        # TODO: change hard coded values to come from parameters
        self._channel = wpilib.AnalogChannel(chan)
        self._channel.SetOversampleBits(4)
        self._channel.SetAverageBits(2)
        self._volts_per_inch = 5 / 512.0

    def get_voltage(self):
        """Get the voltage from the analog channel."""
        return self._channel.GetAverageVoltage()

    def get_range_in_inches(self):
        """Get the range to the nearest object in inches."""
        rng = self.get_voltage()
        rng = rng / self._volts_per_inch
        return rng

    def get_range_in_feet(self):
        """Get the range to the nearest object in feet."""
        rng = self.get_range_in_inches() / 12.0
        return rng

