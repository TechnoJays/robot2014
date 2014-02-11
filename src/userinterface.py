""" This module provides the connection

"""

# Imports
import math
import os

import wpilib

import common
import parameters
import datalog

class Joystick(object):
    """Enumerates joystick inputs

    This enumeration is used to describe the inputs available from the joystick

     Attributes:

        JoystickAxis
            LEFTX
            LEFTY
            RIGHTX
            RIGHTY
            DPADX
            DPADY

        JoystickButtons
            X
            A
            B
            Y
            LEFTBUMPER
            RIGHTBUMPER
            LEFTTRIGGER
            RIGHTTRIGGER
            BACK
            START

        UserControllers
            DRIVER
            SCORING

    """

    LEFTX=1
    LEFTY=2
    RIGHTX=3
    RIGHTY=4
    DPADX=5
    DPADY=6

    X=1
    A=2
    B=3
    Y=4
    LEFTBUMPER=5
    RIGHTBUMPER=6
    LEFTTRIGGER=7
    RIGHTTRIGGER=8
    BACK=9
    START=10


class UserInterface(object):
    """Provides the user interface connectionS
    """

    _log = None
    _parameters = None

    _controller_1 = None
    _controller_1_buttons = 0
    _controller_1_previous_button_state = 0
    _controller_1_dead_band = 0.0

    _controller_2 = None
    _controller_2_buttons = 0
    _controller_2_previous_button_state = 0
    _controller_2_dead_band = 0.0


    _driver_station_lcd = None
    _data_log = None
    # TODO: may not need parameters file
    _parameters_file = None

    _robot_state = None
    _display_line = 0
    _log_enabled = False


    def __init__(self, params="userinterface.par", logging_enabled=False):
        """ Create and initialize a UserInterface

        Args:
            params: The parameters filename to use for configuration
            logging_enabled: True if logging should be enabled

        """

        self._initialize(params,logging_enabled)

    def dispose(self)
        """ Dispose of a UserInterface object.

        Dispose of the UserInterface object

        """

        if self._log:
            self._log.close()
        self._log = None
        self._parameters = None
        self._controller_1 = None
        self._controller_2 = None

    def _initialize(self, params, logging_enabled):
        """Initialize and configure the UserInterface object.

        Initialize instance variables to defaults, read parameter values from
        the specified file, instantiate required objects and update status
        variables.

        Args:
            params: The parameters filename to use for configuration.
            logging_enabled: True if logging should be enabled.

        """

        # Initialize public member variables

        # Intialize private member objects
        self._log = None
        self._parameters = None
        self._controller_1 = None
        self._controller_2 = None
        self._controller_1_previous_button_state = []
        self._controller_2_previous_button_state = []

        # Initialize private parameters
        self._controller_1_buttons = 4
        self._controller_2_buttons = 4
        self._controller_1_dead_band = 0.05
        self._controller_2_dead_band = 0.05

        # Initialize private member variables
        _display_line = 0
        _log_enabled = false
        _robot_state = common.ProgramState.DISABLED
        # TODO: may not need parameters file
        _parameters_file = None

        if logging_enabled:
            #Create a new data log object
            self._log = datalog.DataLog("userinterface.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Read parameters file
        self._parameters_file = os.path.realpath('../doc/' + params)
        self.load_parameters()

    def load_parameters(self):
        """Load values from a parameter file and create and initialize objects.

        Read parameter values from the specified file, instantiate required
        objects, and update status variables.

        Returns:
            True if the parameter file was processed successfully.

        """

        # Define and Initialize local variables
        controller_1_port = 1
        controller_2_port = 2
        controller_1_axis = 2
        controller_2_axis = 2
        param_reader = None

        # Close and delete old objects
        self._parameters = None
        self._controller_1 = None
        self._controller_2 = None
        self._controller_1_previous_button_state = []
        self._controller_2_previous_button_state = []

        # Read the parameters file
        param_reader = parameters.Parameters(self._parameters_file)
        if param_reader:
            _parameters = param_reader.read_values(__name__.lower())

        if _log_enabled:
            if _parameters:
                self._log._write_line("Robot parameters loaded successfully")
            else:
                self._log._write_line("Failed to read Robot parameters")

        if _parameters:

