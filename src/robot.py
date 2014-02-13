"""This module contains the FRC robot class."""

# Imports

# If wpilib not available use pyfrc
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

import autoscript
import common
import datalog
import drivetrain
import feeder
import parameters
import shooter
import stopwatch
#import targeting
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
    _autoscript = None
    _drive_train = None
    _feeder = None
    _log = None
    _parameters = None
    _shooter = None
    #_targeting = None
    _timer = None
    _user_interface = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _current_command_complete = False
    _current_command_in_progress = False
    _current_command = None
    _autoscript_file_counter = 0
    _autoscript_filename = None
    _autoscript_files = None
    _driver_alternate = False
    _scoring_alternate = False

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
        self._autoscript = None
        self._drive_train = None
        self._feeder = None
        self._log = None
        self._parameters = None
        self._shooter = None
        #self._targeting = None
        self._timer = None
        self._user_interface = None

        # Initialize private member variables
        self._log_enabled = False
        self._parameters_file = None
        self._current_command_complete = False
        self._current_command_in_progress = False
        self._current_command = None
        self._autoscript_file_counter = 0
        self._autoscript_filename = None
        self._autoscript_files = None
        self._driver_alternate = False
        self._scoring_alternate = False

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("robot.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True

        self._timer = stopwatch.Stopwatch()

        # Read parameters file
        self._parameters_file = params
        self.load_parameters()

        # Create robot objects
        self._autoscript = autoscript.AutoScript()
        self._drive_train = drivetrain.DriveTrain("drivetrain.par",
                self._log_enabled)
        self._feeder = feeder.Feeder("feeder.par", self._log_enabled)
        self._shooter = shooter.Shooter("shooter.par", self._log_enabled)
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
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.DISABLED)
            self._drive_train.read_sensors()
        if self._feeder:
            self._feeder.set_robot_state(common.ProgramState.DISABLED)
        if self._shooter:
            self._shooter.set_robot_state(common.ProgramState.DISABLED)
            self._shooter.read_sensors()
        #if self._targeting:
        #    self._targeting.set_robot_state(common.ProgramState.DISABLED)
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.DISABLED)

        # Get the list of autoscript files/routines
        if self._autoscript:
            self._autoscript_files = self._autoscript.get_available_scripts()
            if self._autoscript_files and len(self._autoscript_files) > 0:
                self._autoscript_file_counter = 0
                self._autoscript_filename = self._autoscript_files[
                                                self._autoscript_file_counter]
                if self._user_interface:
                    self._user_interface.output_user_message(
                                                self._autoscript_filename,
                                                True)

        if self._timer:
            self._timer.stop()
            self._timer.start()

        # Repeat this loop as long as we're in Disabled
        while self.IsDisabled():
            # Set all motors to be stopped (prevent motor safety errors)
            if self._drive_train:
                self._drive_train.drive(0.0, 0.0, False)
            if self._feeder:
                self._feeder.feed(feeder.Direction.STOP)
            if self._shooter:
                self._shooter.move(0.0)
            if (self._user_interface and self._autoscript and
                self._autoscript_files and len(self._autoscript_files) > 0):
                if (self._user_interface.get_button_state(
                                    userinterface.UserControllers.DRIVER,
                                    userinterface.JoystickButtons.START) == 1
                    and self._user_interface.button_state_changed(
                                    userinterface.UserControllers.DRIVER,
                                    userinterface.JoystickButtons.START)):
                    self._autoscript_file_counter += 1
                    if (self._autoscript_file_counter >
                        (len(self._autoscript_files) - 1)):
                        self._autoscript_file_counter = 0
                    self._autoscript_filename = self._autoscript_files[
                                                  self._autoscript_file_counter]
                    self._user_interface.output_user_message(
                                                self._autoscript_filename,
                                                True)
                self._user_interface.store_button_states(
                                        user_interface.UserControllers.DRIVER)

            self._check_restart()
            wpilib.Wait(0.01)

    def Autonomous(self):
        """Controls the robot during Autonomous mode.

        Instantiate a Class using default values.

        """
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()
        if self._autoscript and self._autoscript_filename:
            self._autoscript.parse(self._autoscript_filename)
            self._current_command_complete = False
            self._current_command_in_progress = False
            self._current_command = self._autoscript.get_next_command()
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.AUTONOMOUS)
        if self._feeder:
            self._feeder.set_robot_state(common.ProgramState.AUTONOMOUS)
        if self._shooter:
            self._shooter.set_robot_state(common.ProgramState.AUTONOMOUS)
        #if self._targeting:
        #    self._targeting.set_robot_state(common.ProgramState.AUTONOMOUS)
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.AUTONOMOUS)

        # Repeat this loop as long as we're in Autonomous
        self.GetWatchdog().SetEnabled(False)
        while self.IsAutonomous() and self.IsEnabled():
            autoscript_finished = False
            self._current_command_complete = False

            # Read sensors
            if self._drive_train:
                self._drive_train.read_sensors()
            if self._shooter:
                self._shooter.read_sensors()

            # Execute autoscript commands
            if self._autoscript and self._autoscript_filename:
                # If we see either invalid or end, we're finished
                if (self._current_command and
                    self._current_command.command != "invalid" and
                    self._current_command.command != "end")
                    if self._current_command.command == "wait":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 1 or
                            not self._timer):
                            self._current_command_complete = True
                        else:
                            if not self._current_command_in_progress:
                                self._timer.stop()
                                self._timer.start()
                                self._current_command_in_progress = True
                            elapsed_time = self._timer.elapsed_time_in_secs()
                            time_left = (self._current_command.parameters[0] -
                                         elapsed_time)
                            if time_left < 0:
                                self._timer.stop()
                                self._current_command_complete = True
                    elif self._current_command.command == "adjustheading":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 2 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if (self._drive_train.adjust_heading(
                                        self._current_command.parameters[0]
                                        self._current_command.parameters[1])):
                                self._current_command_complete = True
                    elif self._current_command.command == "drivedistance":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 2 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if (self._drive_train.drive_distance(
                                        self._current_command.parameters[0]
                                        self._current_command.parameters[1])):
                                self._current_command_complete = True
                    elif self._current_command.command == "drivetime":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 3 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if not self._current_command_in_progress:
                                self._drive_train.reset_and_start_timer()
                                self._current_command_in_progress = True
                            if (self._drive_train.drive_time(
                                        self._current_command.parameters[0]
                                        self._current_command.parameters[1],
                                        self._current_command.parameters[2])):
                                self._current_command_complete = True
                    elif self._current_command.command == "setheading":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 2 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if (self._drive_train.set_heading(
                                        self._current_command.parameters[0]
                                        self._current_command.parameters[1])):
                                self._current_command_complete = True
                    elif self._current_command.command == "turntime":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 3 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if not self._current_command_in_progress:
                                self._drive_train.reset_and_start_timer()
                                self._current_command_in_progress = True
                            if (self._drive_train.turn_time(
                                        self._current_command.parameters[0]
                                        self._current_command.parameters[1],
                                        self._current_command.parameters[2])):
                                self._current_command_complete = True

                    #TODO feeder
                    #TODO shooter
                    #TODO targeting?
                    #TODO other autonomous?

                    # Catchall - for any unrecognized command
                    else:
                        self._current_command_complete = True

                    # Get next command if/when current one is finished
                    if self._current_command_complete:
                        self._current_command_complete = False
                        self._current_command = (
                                        self._autoscript.get_next_command())
                else:
                    autoscript_finished = True
            else:
                autoscript_finished = True

            if autoscript_finished:
                # Set all motors to inactive
                if self._drive_train:
                    self._drive_train.drive(0.0, 0.0, False)
                if self._feeder:
                    self._feeder.feed(feeder.Direction.STOP)
                if self._shooter:
                    self._shooter.move(0.0)

            self._check_restart()
            wpilib.Wait(0.01)

    def OperatorControl(self):
        """Controls the robot during Teleop/OperatorControl mode.

        Instantiate a Class using default values.

        """
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()
        if self._drive_train:
            self._drive_train.set_robot_state(common.ProgramState.TELEOP)
        if self._feeder:
            self._feeder.set_robot_state(common.ProgramState.TELEOP)
        if self._shooter:
            self._shooter.set_robot_state(common.ProgramState.TELEOP)
        #if self._targeting:
        #    self._targeting.set_robot_state(common.ProgramState.TELEOP)
        if self._user_interface:
            self._user_interface.set_robot_state(common.ProgramState.TELEOP)

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
            if self._shooter:
                self._shooter.read_sensors()

            # Perform teleop autonomous actions
            # TODO

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

                # Check for alternate speed mode
                if (self._user_interface.get_button_state(
                                user_interface.UserControllers.DRIVER,
                                user_interface.JoystickButtons.RIGHTBUMPER)
                    == 1):
                    self._driver_alternate = True
                else:
                    self._driver_alternate = False
                if (self._user_interface.get_button_state(
                                user_interface.UserControllers.SCORING,
                                user_interface.JoystickButtons.RIGHTBUMPER)
                    == 1):
                    self._scoring_alternate = True
                else:
                    self._scoring_alternate = False

                # Check if encoder soft limits should be ignored
                if (self._user_interface.get_button_state(
                                user_interface.UserControllers.SCORING,
                                user_interface.JoystickButtons.LEFTBUMPER)
                    == 1):
                    self._shooter.ignore_limits(True)
                else:
                    self._shooter.ignore_limits(False)

                # Check if any teleop autonomous routines are requested
                # TODO


                # Manually control the robot
                # Drive train
                if driver_left_y != 0.0 or driver_right_y != 0.0:
                    #TODO: abort any relevent teleop auto routines
                    if self._drive_train:
                        self._drive_train.tank_drive(driver_left_y,
                                driver_right_y, False)
                else:
                    #TODO: make sure we don't mess with any teleop auto routines
                    # if they're running
                    self._drive_train.tank_drive(0.0, 0.0, False)

                # TODO Shooter
                # TODO Feeder

                # Print debug info to driver station
                if (self._user_interface.get_button_state(
                                user_interface.UserControllers.SCORING,
                                user_interface.JoystickButtons.BACK) == 1 and
                    self._user_interface.button_state_changed(
                                user_interface.UserControllers.SCORING,
                                user_interface.JoystickButtons.BACK)):
                    self._user_interface.output_user_message("Diagnostics",
                                                             True)
                    if self._drive_train:
                        self._drive_train.log_current_state()
                        state = self._drive_train.get_current_state()
                        self._user_interface.output_user_message(state, False)
                    if self._shooter:
                        self._shooter.log_current_state()
                        state = self._shooter.get_current_state()
                        self._user_interface.output_user_message(state, False)


                # Update/store the UI button state
                self._user_interface.store_button_states(
                        userinterface.UserControllers.DRIVER)
                self._user_interface.store_button_states(
                        userinterface.UserControllers.SCORING)

            self._check_restart()
            wpilib.Wait(0.01)

    def _check_restart(self):
        """Monitor user input for a restart request."""
        #TODO comment out when in competitions
        if (self._user_interface.get_button_state(
                        user_interface.UserControllers.SCORING,
                        user_interface.JoystickButtons.START) == 1):
            raise RuntimeError("Restart")



def run():
    """Create the robot and start it."""
    robot = MyRobot()
    robot.StartCompetition()
