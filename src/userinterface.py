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


class UserControllers (object):

    KDRIVER = 0
    KSCORING = 1


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

        _driver_station_lcd = wpilib.DriverStationLCD_GetInstance()

        if logging_enabled:
            #Create a new data log object
            self._log = datalog.DataLog("userinterface.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Read parameters file
        self._parameters_file = os.path.realpath(params)
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
        section = __name__.lower()
        print(section)

        # Close and delete old objects
        self._parameters = None
        self._controller_1 = None
        self._controller_2 = None
        self._controller_1_previous_button_state = []
        self._controller_2_previous_button_state = []

        # Read the parameters file
        param_reader = parameters.Parameters(self._parameters_file)
        if param_reader:
            _parameters = param_reader.read_values(section)

        if _log_enabled:
            if _parameters:
                self._log._write_line("Robot parameters loaded successfully")
            else:
                self._log._write_line("Failed to read Robot parameters")

        if _parameters:
            controller_1_port = param_reader.get_value(section,
                                                       "CONTROLLER_1_PORT")
		    controller_2_port = param_reader.get_value(section,
                                                       "CONTROLLER_2_PORT")
            controller_1_axis = param_reader.get_value(section,
                                                       "CONTROLLER_1_AXIS")
            controller_2_axis = param_reader.get_value(section,
                                                       "CONTROLLER_2_AXIS")

            self._controller_1_buttons = param_reader.get_value(section,
                                                                "CONTROLLER1_BUTTONS")
            self._controller_2_buttons = param_reader.get_value(section,
                                                                "CONTROLLER2_BUTTONS")

            self._controller_1_dead_band = param_reader.get_value(section,
                                                                  "CONTROLLER1_DEAD_BAND")
            self._controller_2_dead_band = param_reader.get_value(section,
                                                                  "CONTROLLER2_DEAD_BAND")
            # Initialize previous button state lists
            self._controller_1_previous_button_state = [0] * (self._controller_1_buttons + 1)
            self._controller_2_previous_button_state = [0] * (self._controller_2_buttons + 1)

            # Initialize  controller objects
            self._controller_1 = wpilib.Joystick(controller_1_port,
                                                 controller_1_axis,
                                                 self._controller_1_buttons)
            self._controller_2 = wpilib.Joystick(controller_2_port,
                                                 controller_2_axis,
                                                 self._controller_2_buttons)

            # TODO - Store the button states

        return _parameters

    def set_robot_state(self, state):
        """Set the current state of the  robot and perform any actions
        necessary during mode changes.

        Args:
            state: current robot state

        """
        _robot_state = state

    def set_log_state(self, state):
        """Enable or disable logginf for this object

            Args:
                state: true if logging should be enabled
        """
        if (state):
            self._log_enabled = true
        else
            self._log_enabled = false


    def button_state_changed(self, controller, button):
        """Check if the button state for the specified controller/button has changed
        since the last "Store".

        Args:
            controller: the controller to read the button state from
            button: the button ID to read the state from

        Return:
            true if the button state has changed

        """

        # Get the current button state
        current_state = get_button_state(controller, button)
        previous_state = 0

        if controller = UserControllers.KDRIVER:
            previous_state = self._controller_1_previous_button_state[button]
        else if controller = UserControllers.KSCORING:
            previous_state = self._controller_2_previous_button_state[button]

        if current_state != previous_state:
            return true
        else:
            return false


    def get_axis_value(self, controller, axis):
        """ Read the current axis value for the specified controller/axis

        Args:
            controller: the controller to read the axis value from
            axis: the axis ID to read

        Return:
            the current position fo the specified axis

        """

        # Get the current axis value from the controller
        value = 0.0

        if controller == UserControllers.KDRIVER:
            if self._controller_1:
                value = self._controller_1.GetRawAxis(axis)
                if abs(value) < self._controller_1_dead_band:
                    return 0.0
                return value
        else if controller ==  UserControllers.KSCORING:
            if self._controller_2:
                value = self._controller_2.GetRawAxis(axis)
                if abs(value) < self._controller_2_dead_band:
                    return 0.0
                return value

        return 0.0

    def get_button_state(self, controller, button):
        """Read the button state for the specified controller/button

        Args:
            controller: the controller to read the button state from
            button: the button ID to read the state from

        Return:
            1 if button is currently pressed

        """

        if controller == UserControllers.KDRIVER:
            if self._controller_1:
                return self._controller_1.GetRawButton(button)
            else:
                return 0
        else if controller == UserControllers.SCORING:
            if self._controller_2:
                return self._controller_2.GetRawButton(button)
            else:
                return 0

        return 0


    def store_button_states (self, controller):
        """Store the current  button states for the specified controller

        Args:
            controller: the controller to read the button states from

        """

        button_state = 0
        button_count = 0

        # Get the total number of buttons for the controller
        button_count = {
                        0: self._controller_1_buttons,
                        1: self._controller_2_buttons
                        }.get(controller,0)


        # Store the current state of each button for this controller
        # +1 is used in array indexing since #defines and GeRawButton start at 1,
        # and array starts at 0.
        for i in range(button_count):
            button_state = self.get_button_state(controller, i+1)

            if controller == UserControllers.KDRIVER:
                _controller_1_previous_button_state[i+1] = button_state

            if controller == UserControllers.KSCORING:
                _controller_2_previous_button_state[i+1] = button_state
