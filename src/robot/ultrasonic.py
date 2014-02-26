"""This module provides a class to read a range finder."""


# Imports
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time


class RangeFinder(object):
    """Get the distance to the nearest object."""

    _volts_per_inch = None
    _channel = None
    _range_list = None

    def __init__(self, chan):
        # TODO: change hard coded values to come from parameters
        self._channel = wpilib.AnalogChannel(chan)
        self._channel.SetOversampleBits(4)
        self._channel.SetAverageBits(4)
        self._volts_per_inch = 5 / 512.0
        self._range_list = []

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

    def get_filtered_range_in_feet(self):
        """Get the median filtered range in feet."""
        current_range = self.get_range_in_feet()
        if current_range > 1.0:
            if len(self._range_list) >= 21:
                self._range_list.pop(0)
            self._range_list.append(current_range)
        sorted_ranges = list(self._range_list)
        sorted_ranges.sort()
        return sorted_ranges[len(sorted_ranges)-1]

