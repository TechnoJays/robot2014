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
import math
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

    # Private parameters
    _max_hold_to_shoot_time = None
    _catapult_feed_position = None
    _catapult_low_pass_position = None
    _truss_pass_power = None

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
    _current_feeder_position = None
    _hold_to_shoot_step = -1
    _hold_to_shoot_power = -1
    _prep_for_feed_step = -1
    _prep_for_low_pass_step = -1
    _truss_pass_step = -1

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

        # Initialize private parameters
        self._max_hold_to_shoot_time = None
        self._catapult_feed_position = None
        self._catapult_low_pass_position = None
        self._truss_pass_power = None

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
        self._current_feeder_position = None
        self._hold_to_shoot_step = -1
        self._hold_to_shoot_power = 0
        self._prep_for_feed_step = -1
        self._prep_for_low_pass_step = -1
        self._truss_pass_step = -1

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
        self._drive_train = drivetrain.DriveTrain("/py/par/drivetrain.par",
                                                  self._log_enabled)
        self._feeder = feeder.Feeder("/py/par/feeder.par", self._log_enabled)
        self._shooter = shooter.Shooter("/py/par/shooter.par",
                                        self._log_enabled)
        self._user_interface = userinterface.UserInterface(
                                                    "/py/par/userinterface.par",
                                                    self._log_enabled)

    def load_parameters(self):
        """Load values from a parameter file and create and initialize objects.

        Read parameter values from the specified file, instantiate required
        objects, and update status variables.

        Returns:
            True if the parameter file was processed successfully.

        """
        # Close and delete old objects
        self._parameters = None

        # Read the parameters file
        self._parameters = parameters.Parameters(self._parameters_file)
        section = __name__.lower()

        # Read parameters from the file
        if self._parameters:
            self._max_hold_to_shoot_time = self._parameters.get_value(section,
                                                "MAX_HOLD_TO_SHOOT_TIME")
            self._catapult_feed_position = self._parameters.get_value(section,
                                                "CATAPULT_FEED_POSITION")
            self._catapult_low_pass_position = self._parameters.get_value(
                                                section,
                                                "CATAPULT_LOW_PASS_POSITION")
            self._truss_pass_power = self._parameters.get_value(section,
                                                "TRUSS_PASS_POWER")

        return True

    def RobotInit(self):
        """Performs robot-wide initialization.

        Called each time the robot enters the Disabled mode.

        """
        self._initialize("/py/par/robot.par", True)

    def _disabled_init(self):
        """Prepares the robot for Disabled mode."""
        self._set_robot_state(common.ProgramState.DISABLED)

        # Default starting mode is to have the arms UP
        if self._feeder:
            self._current_feeder_position = common.Direction.UP
            self._feeder.set_position(self._current_feeder_position)

        # Read sensors
        self._read_sensors()

        # Get the list of autoscript files/routines
        if self._autoscript:
            self._autoscript_files = self._autoscript.get_available_scripts(
                                                                    "/py/as/")
            if self._autoscript_files and len(self._autoscript_files) > 0:
                self._autoscript_file_counter = 0
                self._autoscript_filename = self._autoscript_files[
                                                self._autoscript_file_counter]
                if self._user_interface:
                    self._user_interface.output_user_message(
                                                self._autoscript_filename,
                                                True)

        # This would be used for camera initialization
        if self._timer:
            self._timer.stop()
            self._timer.start()

    def Disabled(self):
        """Control the robot during Disabled mode.

        Monitors the user input for a restart request.  This is
        useful during development to load new Python code and
        avoid rebooting the robot.

        Handle the changing of program settings from the driver
        before the start of a match (e.g., autonomous program).

        """
        self._disabled_init()

        # Repeat this loop as long as we're in Disabled
        while self.IsDisabled():
            # Set all motors to be stopped (prevent motor safety errors)
            if self._drive_train:
                self._drive_train.drive(0.0, 0.0, False)
            if self._feeder:
                self._feeder.feed(feeder.Direction.STOP, 0.0)
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
                                        userinterface.UserControllers.DRIVER)

            self._check_restart()
            wpilib.Wait(0.01)

    def _autonomous_init(self):
        """Prepares the robot for Autonomous mode."""
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()
        if self._autoscript and self._autoscript_filename:
            self._autoscript.parse(self._autoscript_filename)
            self._current_command_complete = False
            self._current_command_in_progress = False
            self._current_command = self._autoscript.get_next_command()

        self._set_robot_state(common.ProgramState.AUTONOMOUS)
        self.GetWatchdog().SetEnabled(False)

    def Autonomous(self):
        """Controls the robot during Autonomous mode.

        Instantiate a Class using default values.

        """
        self._autonomous_init()
        # Repeat this loop as long as we're in Autonomous
        while self.IsAutonomous() and self.IsEnabled():
            autoscript_finished = False
            self._current_command_complete = False

            # Read sensors
            self._read_sensors()

            # Execute autoscript commands
            if self._autoscript and self._autoscript_filename:
                # If we see either invalid or end, we're finished
                if (self._current_command and
                    self._current_command.command != "invalid" and
                    self._current_command.command != "end"):
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
                                        self._current_command.parameters[0],
                                        self._current_command.parameters[1])):
                                self._current_command_complete = True
                    elif self._current_command.command == "drivedistance":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 2 or
                            not self._drive_train):
                            self._current_command_complete = True
                        else:
                            if (self._drive_train.drive_distance(
                                        self._current_command.parameters[0],
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
                                        self._current_command.parameters[0],
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
                                        self._current_command.parameters[0],
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
                                        self._current_command.parameters[0],
                                        self._current_command.parameters[1],
                                        self._current_command.parameters[2])):
                                self._current_command_complete = True
                    elif self._current_command.command == "setfeederposition":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 1 or
                            not self._feeder):
                            self._current_command_complete = True
                        else:
                            self._current_feeder_position = \
                                        self._current_command.parameters[0]
                            self._feeder.set_position(
                                        self._current_command.parameters[0])
                            self._current_command_complete = True
                    elif self._current_command.command == "feedtime":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 3 or
                            not self._feeder):
                            self._current_command_complete = True
                        else:
                            if not self._current_command_in_progress:
                                self._feeder.reset_and_start_timer()
                                self._current_command_in_progress = True
                            if (self._feeder.feed_time(
                                        self._current_command.parameters[0],
                                        self._current_command.parameters[1],
                                        self._current_command.parameters[2])):
                                self._current_command_complete = True
                    elif self._current_command.command == "auto_fire":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 1 or
                            not self._shooter):
                            self._current_command_complete = True
                        else:
                            if (self._shooter.auto_fire(
                                        self._current_command.parameters[0])):
                                self._current_command_complete = True
                    elif self._current_command.command == "setshooter":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 2 or
                            not self._shooter):
                            self._current_command_complete = True
                        else:
                            if (self._shooter.set_position(
                                        self._current_command.parameters[0],
                                        self._current_command.parameters[1])):
                                self._current_command_complete = True
                    elif self._current_command.command == "shoottime":
                        if (not self._current_command.parameters or
                            len(self._current_command.parameters) != 3 or
                            not self._shooter):
                            self._current_command_complete = True
                        else:
                            if not self._current_command_in_progress:
                                self._shooter.reset_and_start_timer()
                                self._current_command_in_progress = True
                            if (self._shooter.shoot_time(
                                        self._current_command.parameters[0],
                                        self._current_command.parameters[1],
                                        self._current_command.parameters[2])):
                                self._current_command_complete = True

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
                    self._feeder.feed(feeder.Direction.STOP, 0.0)
                if self._shooter:
                    self._shooter.move(0.0)

            self._check_restart()
            wpilib.Wait(0.01)

    def _operator_control_init(self):
        """Prepares the robot for Teleop mode."""
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()

        self._set_robot_state(common.ProgramState.TELEOP)

        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)

    def OperatorControl(self):
        """Controls the robot during Teleop/OperatorControl mode.

        Instantiate a Class using default values.

        """
        self._operator_control_init()
        dog = self.GetWatchdog()
        # Repeat this loop as long as we're in Teleop
        while self.IsOperatorControl() and self.IsEnabled():
            # Feed the watchdog timer
            dog.Feed()

            # Read sensors
            self._read_sensors()

            # Perform tele-auto routines
            self._perform_tele_auto()

            # Perform user controlled actions
            if self._user_interface:
                # Check for alternate speed mode request
                self._check_alternate_speed_modes()

                # Check for ignore encoder limit request
                self._check_ignore_limits()

                # Check for tele-auto requests
                self._check_tele_auto_requests()

                # Manually control the robot
                self._control_drive_train()
                self._control_shooter()
                self._control_feeder()

                # Check for tele-auto kill switch
                self._check_tele_auto_kill()

                # Check for debug to console request
                self._check_debug_request()

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
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.START) == 1):
            raise RuntimeError("Restart")

    def _read_sensors(self):
        """Have the objects read their sensors."""
        if self._drive_train:
            self._drive_train.read_sensors()
        if self._shooter:
            self._shooter.read_sensors()

    def _set_robot_state(self, state):
        """Notify objects of the current mode."""
        if self._drive_train:
            self._drive_train.set_robot_state(state)
        if self._feeder:
            self._feeder.set_robot_state(state)
        if self._shooter:
            self._shooter.set_robot_state(state)
        #if self._targeting:
        #    self._targeting.set_robot_state(state)
        if self._user_interface:
            self._user_interface.set_robot_state(state)

    def _check_tele_auto_requests(self):
        """Check if any teleop autonomous routines are requested."""
        # Hold the right trigger to shoot, longer duration = more power
        if (self._user_interface.button_state_changed(
                    userinterface.UserControllers.SCORING,
                    userinterface.JoystickButtons.RIGHTTRIGGER)):
            if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.RIGHTTRIGGER) == 1):
                self._timer.start()
                self._hold_to_shoot_step = 1
            else:
                self._timer.stop()
                duration = self._timer.elapsed_time_in_secs()
                self._hold_to_shoot_power = (((duration * 1.0) /
                                           self._max_hold_to_shoot_time)
                                            * 100.0)
                if self._hold_to_shoot_power > 100.0:
                    self._hold_to_shoot_power = 100.0
                self._hold_to_shoot_step = 2
        # Press Y to prepare to pick up a ball
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.Y) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.Y)):
            self._prep_for_feed_step = 1
        # Press X to prepare to pick up a ball for a low pass
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.X) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.X)):
            self._prep_for_low_pass_step = 1
        # Press left bumper to pass over the truss
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.LEFTBUMPER) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.LEFTBUMPER)):
            self._truss_pass_step = 1

    def _perform_tele_auto(self):
        """Perform teleop autonomous actions."""
        # Hold to shoot
        if self._hold_to_shoot_step == 2:
            if self._shooter:
                if self._shooter.auto_fire(self._hold_to_shoot_power):
                    self._hold_to_shoot_step = -1
        # Prep for feed
        if self._prep_for_feed_step != -1:
            if self._prep_for_feed_step == 1:
                if self._feeder:
                    self._current_feeder_position = common.Direction.DOWN
                    self._feeder.set_position(self._current_feeder_position)
                self._prep_for_feed_step = 2
            elif self._prep_for_feed_step == 2:
                if self._shooter:
                    if self._shooter.set_position(self._catapult_feed_position,
                                                  1.0):
                        self._prep_for_feed_step = -1
        # Prep for low pass
        if self._prep_for_low_pass_step != -1:
            if self._prep_for_low_pass_step == 1:
                if self._feeder:
                    self._current_feeder_position = common.Direction.DOWN
                    self._feeder.set_position(self._current_feeder_position)
                self._prep_for_low_pass_step = 2
            elif self._prep_for_low_pass_step == 2:
                if self._shooter:
                    if self._shooter.set_position(
                                        self._catapult_low_pass_position,
                                        1.0):
                        self._prep_for_low_pass_step = -1
        # Truss pass
        if self._truss_pass_step != -1:
            if self._shooter:
                if self._shooter.auto_fire(self._truss_pass_power):
                    self._truss_pass_step = -1

    def _check_debug_request(self):
        """Print debug info to driver station."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.BACK) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.BACK)):
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

    def _check_tele_auto_kill(self):
        """Check kill switch for all tele-auto functionality."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.BACK) == 1):
            self._hold_to_shoot_step = -1
            self._prep_for_feed_step = -1
            self._prep_for_low_pass_step = -1
            self._truss_pass_step = -1

    def _check_alternate_speed_modes(self):
        """Check for alternate speed mode."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.LEFTBUMPER) == 1):
            self._driver_alternate = True
        else:
            self._driver_alternate = False

    def _check_ignore_limits(self):
        """Check if encoder soft limits should be ignored."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.START) == 1):
            self._shooter.ignore_encoder_limits(True)
        else:
            self._shooter.ignore_encoder_limits(False)

    def _control_drive_train(self):
        """Manually control the drive train."""
        driver_left_y = self._user_interface.get_axis_value(
                userinterface.UserControllers.DRIVER,
                userinterface.JoystickAxis.LEFTY)
        driver_right_x = self._user_interface.get_axis_value(
                userinterface.UserControllers.DRIVER,
                userinterface.JoystickAxis.RIGHTX)
        if driver_left_y != 0.0 or driver_right_x != 0.0:
            # Abort any relevent teleop auto routines
            if self._drive_train:
                self._drive_train.arcade_drive(driver_left_y, driver_right_x,
                                               False)
        else:
            # Make sure we don't mess with any teleop auto routines
            # if they're running
            self._drive_train.arcade_drive(0.0, 0.0, False)

    def _control_shooter(self):
        """Manually control the catapult."""
        scoring_left_y = self._user_interface.get_axis_value(
                userinterface.UserControllers.SCORING,
                userinterface.JoystickAxis.LEFTY)
        if scoring_left_y != 0.0:
            if self._shooter:
                self._shooter.move(scoring_left_y)
                # Abort any relevent teleop auto routines
                self._hold_to_shoot_step = -1
                self._prep_for_feed_step = -1
                self._prep_for_low_pass_step = -1
                self._truss_pass_step = -1
        else:
            # Make sure we don't mess with any teleop auto routines
            # if they're running
            if (self._hold_to_shoot_step == -1 and
                self._prep_for_feed_step == -1 and
                self._prep_for_low_pass_step == -1 and
                self._truss_pass_step == -1):
                self._shooter.move(0.0)

    def _control_feeder(self):
        """Manually control the feeder."""
        scoring_right_y = self._user_interface.get_axis_value(
                userinterface.UserControllers.SCORING,
                userinterface.JoystickAxis.RIGHTY)
        # Toggle feeder arms
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.RIGHTBUMPER) == 1
            and self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.RIGHTBUMPER)):
            if self._current_feeder_position == common.Direction.UP:
                self._current_feeder_position = common.Direction.DOWN
            else:
                self._current_feeder_position = common.Direction.UP
            self._feeder.set_position(self._current_feeder_position)
            # Abort any relevent teleop auto routines
            self._prep_for_feed_step = -1
            self._prep_for_low_pass_step = -1
        # Manually control feeder motors
        if scoring_right_y != 0.0:
            if self._feeder:
                direction = feeder.Direction.STOP
                if scoring_right_y > 0:
                    direction = feeder.Direction.IN
                else:
                    direction = feeder.Direction.OUT
                self._feeder.feed(direction, math.fabs(scoring_right_y))
                # Abort any relevent teleop auto routines
        else:
            # Make sure we don't mess with any teleop auto routines
            # if they're running
            self._feeder.feed(feeder.Direction.STOP, 0.0)


def run():
    """Create the robot and start it."""
    robot = MyRobot()
    robot.StartCompetition()
