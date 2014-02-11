"""This module contains the FRC robot class."""

# Imports

# If wpilib not available use pyfrc
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

import common
import datalog
import drivetrain
import parameters
import userinterface


class MyRobot(wpilib.SimpleRobot):
    """Controls the robot.

    This is the main robot class that controls the robot during all 3 modes.
    There is 1 method for each mode: Disabled, Autonomous, and OperatorControl
    (teleop).  The methods are called once from the main control loop each time
    the robot enters the states.

    """
    # Public member variables

    # Private member objects
    _drive_train = None
    _log = None
    _parameters = None
    _user_interface = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None

    def _initialize(self, params, logging_enabled):
        """Initialize the robot.

        Initialize instance variables to defaults, read parameter values from
        the specified file, instantiate required objects and update status
        variables.

        Args:
            params: The parameters filename to use for configuration.
            logging_enabled: True if logging should be enabled.

        """
        # Initialize public member variables

        # Initialize private member objects
        self._drive_train = None
        self._log = None
        self._parameters = None
        self._user_interface = None

        # Initialize private parameters

        # Initialize private member variables
        self._log_enabled = False

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("robot.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Read parameters file
        self._parameters_file = params
        self.load_parameters()

        # Create robot objects
        self._drive_train = drivetrain.DriveTrain("drivetrain.par",
                self._log_enabled)
        self._user_interface = userinterface.UserInterface("userinterface.par",
                self._log_enabled)

    def load_parameters(self):
        """Load values from a parameter file and create and initialize objects.

        Read parameter values from the specified file, instantiate required
        objects, and update status variables.

        Returns:
            True if the parameter file was processed successfully.

        """
        # Define and initialize local variables
        parameters_read = False

        # Close and delete old objects
        self._parameters = None

        # Read the parameters file
        self._parameters = parameters.Parameters(self._parameters_file)
        if self._parameters and self._parameters.file_opened:
            parameters_read = self._parameters.read_values()
            self._parameters.close()

        if self._log_enabled:
            if parameters_read:
                self._log.write_line("Robot parameters loaded successfully")
            else:
                self._log.write_line("Failed to read Robot parameters")

        # Store parameters from the file to local variables
        if parameters_read:
            pass

        # TODO

        return parameters_read

    def RobotInit(self):
        """Performs robot-wide initialization.

        Called each time the robot enters the Disabled mode.

        """
        self._initialize("robot.par", True)

    def Disabled(self):
        """Control the robot during Disabled mode.

        Monitors the user input for a restart request.  This is
        useful during development to load new Python code and
        avoid rebooting the robot.

        Handle the changing of program settings from the driver
        before the start of a match (e.g., autonomous program).

        """
        # Perform initialization before looping
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.DISABLED)
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.DISABLED)
            self._drive_train.read_sensors()


        # Repeat this loop as long as we're in Disabled
        while self.IsDisabled():
            # Set all motors to be stopped (prevent motor safety errors)
            if self._drive_train:
                self._drive_train.Drive(0.0, 0.0, False)
            self._check_restart()  #TODO - only include while testing
            wpilib.Wait(0.01)

    def Autonomous(self):
        """Controls the robot during Autonomous mode.

        Instantiate a Class using default values.

        """
        # Perform initialization before looping
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.AUTONOMOUS)
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.AUTONOMOUS)

        # Repeat this loop as long as we're in Autonomous
        self.GetWatchdog().SetEnabled(False)
        while self.IsAutonomous() and self.IsEnabled():
            self._check_restart()  #TODO - only include while testing
            wpilib.Wait(0.01)

    def OperatorControl(self):
        """Controls the robot during Teleop/OperatorControl mode.

        Instantiate a Class using default values.

        """
        # Perform initialization before looping
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.TELEOP)
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.TELEOP)

        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)

        # Repeat this loop as long as we're in Teleop
        while self.IsOperatorControl() and self.IsEnabled():
            # Feed the watchdog timer
            dog.Feed()

            # Read sensors
            if self._drive_train:
                self._drive_train.read_sensors()

            # Perform autonomous actions

            # Perform user controlled actions
            if self._user_interface:
                # Get the values for the thumbsticks and dpads
                driver_left_y = self._user_interface.get_axis_value(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickAxis.LEFTY)
                driver_right_y = self._user_interface.get_axis_value(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickAxis.RIGHTY)
                scoring_left_y = self._user_interface.get_axis_value(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickAxis.LEFTY)
                scoring_right_y = self._user_interface.get_axis_value(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickAxis.RIGHTY)
                scoring_dpad_y = self._user_interface.get_axis_value(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickAxis.DPADY)

                # Manually control the robot
                if driver_left_y != 0.0 or driver_right_y != 0.0:
                    if self._drive_train:
                        self._drive_train.tank_drive(driver_left_y,
                                driver_right_y, False)
                else:
                    self._drive_train.tank_drive(0.0, 0.0, False)

                # Update/store the UI button state
                self._user_interface.store_button_states(
                        userinterface.UserControllers.DRIVER)
                self._user_interface.store_button_states(
                        userinterface.UserControllers.SCORING)

            self._check_restart()  #TODO - only include while testing
            wpilib.Wait(0.01)

    def _check_restart(self):
        """Monitor user input for a restart request."""
        #if lstick.GetRawButton(10):
        #    raise RuntimeError("Restart")
        #TODO


def run():
    """Create the robot and start it."""
    robot = MyRobot()
    robot.StartCompetition()
