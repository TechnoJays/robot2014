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
    _range_print_timer = None
    _user_interface = None

    # Private parameters
    _max_hold_to_shoot_time = None
    _min_hold_to_shoot_power = None
    _catapult_feed_position = None
    _truss_pass_power = None
    _truss_pass_position = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _autoscript_file_counter = 0
    _autoscript_filename = None
    _autoscript_files = None
    _driver_alternate = False
    _scoring_alternate = False
    _current_feeder_position = None
    _hold_to_shoot_step = -1
    _hold_to_shoot_power = -1
    _prep_for_feed_step = -1
    _truss_pass_step = -1
    _driver_controls_swap_ratio = 1.0
    _hold_to_shoot_power_factor = 0.0
    _shooter_setup_step = -1
    _disable_range_print = False
    _robot_names = None
    _drive_train_names = None
    _feeder_names = None
    _shooter_names = None
    _user_interface_names = None

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
        self._range_print_timer = None
        self._user_interface = None

        # Initialize private parameters
        self._max_hold_to_shoot_time = None
        self._min_hold_to_shoot_power = None
        self._catapult_feed_position = None
        self._truss_pass_power = None
        self._truss_pass_position = None

        # Initialize private member variables
        self._log_enabled = False
        self._parameters_file = None
        self._autoscript_file_counter = 0
        self._autoscript_filename = None
        self._autoscript_files = None
        self._driver_alternate = False
        self._scoring_alternate = False
        self._driver_controls_swap_ratio = 1.0
        self._current_feeder_position = None
        self._hold_to_shoot_step = -1
        self._hold_to_shoot_power = 0
        self._prep_for_feed_step = -1
        self._truss_pass_step = -1
        self._hold_to_shoot_power_factor = 0.0
        self._shooter_setup_step = -1
        self._disable_range_print = False

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("robot.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True

        self._timer = stopwatch.Stopwatch()
        self._range_print_timer = stopwatch.Stopwatch()

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

        # Store the attributes/names in each object
        self._robot_names = dir(self)
        self._drive_train_names = dir(self._drive_train)
        self._feeder_names = dir(self._feeder)
        self._shooter_names = dir(self._shooter)
        self._user_interface_names = dir(self._user_interface)

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
            self._min_hold_to_shoot_power = self._parameters.get_value(section,
                                                "MIN_HOLD_TO_SHOOT_POWER")
            self._catapult_feed_position = self._parameters.get_value(section,
                                                "CATAPULT_FEED_POSITION")
            self._truss_pass_power = self._parameters.get_value(section,
                                                "TRUSS_PASS_POWER")
            self._truss_pass_position = self._parameters.get_value(section,
                                                "TRUSS_PASS_POSITION")

        self._hold_to_shoot_power_factor = ((100.0 -
                                             self._min_hold_to_shoot_power) /
                                            100.0)
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
            self._feeder.set_feeder_position(self._current_feeder_position)

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
                    self._disable_range_print = True
                    self._user_interface.output_user_message(
                                                self._autoscript_filename,
                                                True)

        # This would be used for camera initialization
        if self._timer:
            self._timer.stop()
            self._timer.start()

        self.GetWatchdog().SetEnabled(False)

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
                self._shooter.move_shooter(0.0)
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
                    self._disable_range_print = True
                    self._user_interface.output_user_message(
                                                self._autoscript_filename,
                                                True)
                self._user_interface.store_button_states(
                                        userinterface.UserControllers.DRIVER)

            wpilib.Wait(0.01)

    def _autonomous_init(self):
        """Prepares the robot for Autonomous mode."""
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()
        if self._autoscript and self._autoscript_filename:
            self._autoscript.parse(self._autoscript_filename)

        # Read sensors
        self._read_sensors()
        self._disable_range_print = False

        self._set_robot_state(common.ProgramState.AUTONOMOUS)
        self.GetWatchdog().SetEnabled(False)

        # Perform the shooter setup
        self._shooter_setup_step = 1
        while (self.IsAutonomous() and self.IsEnabled() and
               not self._shooter_setup()):
            wpilib.Wait(0.01)

    def Autonomous(self):
        """Controls the robot during Autonomous mode.

        Instantiate a Class using default values.

        """
        # Autonomous initialization
        self._autonomous_init()

        # Method names must be unique for reflection to work,
        # and they should be descriptive
        autoscript_finished = False
        current_command = None
        current_command_complete = True # Initially true to get 1st command

        if not self._autoscript or not self._autoscript_filename:
            autoscript_finished = True

        owner = None
        method = None

        # Repeat this loop as long as we're in Autonomous
        while self.IsAutonomous() and self.IsEnabled():

            # Read sensors
            self._read_sensors()
            self._print_range()

            # Execute autoscript commands
            if not autoscript_finished:

                # Handle the command
                # If we found the method, unpack the parameters List
                # (using *) and call it
                if not current_command_complete:
                    try:
                        current_command_complete = \
                                method(*current_command.parameters)
                    except TypeError:
                        current_command_complete = True

                # Move on to the next command when the current is finished
                if current_command_complete:
                    # Get next command
                    current_command_complete = False
                    current_command = self._autoscript.get_next_command()

                    # If it's None or invalid or end, we're finished
                    if (not current_command or
                        current_command.command == "invalid" or
                        current_command.command == "end"):
                        autoscript_finished = True
                    else:
                        # Try to get the method reference using its name
                        owner, method = self._get_method(
                                                    current_command.command)
                        if not method:
                            current_command_complete = True
                        # Check if method has '_time' in it
                        elif '_time' in current_command.command:
                            # We need to reset its internal timer first
                            reset = None
                            owner, reset = self._get_method(
                                                    'reset_and_start_timer',
                                                    obj=owner)
                            if reset:
                                try:
                                    reset()
                                except TypeError:
                                    current_command_complete = True
                            else:
                                current_command_complete = True

            # Autoscript is finished
            else:
                # Set all motors to inactive
                if self._drive_train:
                    self._drive_train.drive(0.0, 0.0, False)
                if self._feeder:
                    self._feeder.feed(feeder.Direction.STOP, 0.0)
                if self._shooter:
                    self._shooter.move_shooter(0.0)

            wpilib.Wait(0.01)

    def _get_method(self, name, obj=None):
        """This tries to find the matching method in one of the objects.

        Args:
            name: the name of the method.

        Returns:
            Object, Method.

        """
        calling_object = None
        method = None

        # Determine which object contains the method
        if not obj:
            if name:
                if name in self._robot_names:
                    calling_object = self
                elif name in self._drive_train_names:
                    calling_object = self._drive_train
                elif name in self._feeder_names:
                    calling_object = self._feeder
                elif name in self._shooter_names:
                    calling_object = self._shooter
                elif name in self._user_interface_names:
                    calling_object = self._user_interface
        else:
            calling_object = obj

        # Get the method reference from the object
        if calling_object:
            try:
                method = getattr(calling_object, name)
                # Make sure method is callable
                if method and not callable(method):
                    method = None
            except AttributeError:
                pass

        return calling_object, method

    def _operator_control_init(self):
        """Prepares the robot for Teleop mode."""
        # Perform initialization before looping
        if self._timer:
            self._timer.stop()

        self._disable_range_print = False
        self._set_robot_state(common.ProgramState.TELEOP)

        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(1.0)

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

                # Print the range and check for other print timeouts
                self._print_range()
                self._check_ui_print_timeout()

                # Check swap drivetrain direction request
                self._check_swap_drivetrain_request()

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

            wpilib.Wait(0.01)

    def reset_and_start_timer(self):
        """Resets and restarts the timer."""
        if self._timer:
            self._timer.stop()
            self._timer.start()

    def wait_time(self, duration):
        """Autonomous method that does nothing for a specified duration."""
        elapsed_time = self._timer.elapsed_time_in_secs()
        time_left = duration - elapsed_time
        if time_left < 0:
            self._timer.stop()
            return True
        return False

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
                requested_power = (((duration * 1.0) /
                                    self._max_hold_to_shoot_time)
                                   * 100.0)
                self._hold_to_shoot_power = ((requested_power *
                                              self._hold_to_shoot_power_factor)
                                             + self._min_hold_to_shoot_power)
                if self._hold_to_shoot_power > 100.0:
                    self._hold_to_shoot_power = 100.0
                self._shooter.reset_and_start_timer()
                self._hold_to_shoot_step = 2
        # Press Y to prepare to pick up a ball
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.Y) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.Y)):
            self._prep_for_feed_step = 1
        # Press left bumper to pass over the truss
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.LEFTBUMPER) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.LEFTBUMPER)):
            self._truss_pass_step = 1

    def _shooter_setup(self):
        """Get the shooter into a workable state.

        This is because the shooter starts with the arm UP, so the encoder
        value is not starting at 0.  To fix this, we disable encoder
        boundaries and move the arm down for enough time to ensure the arm is
        all the way down.  Then we reset the encoder to 0.

        Returns:
            True when setup is complete.

        """
        if self._shooter:
            # This requires the air tank to be pre-charged before a match
            #if self._shooter_setup_step == 1:
            #    if self._feeder:
            #        self._current_feeder_position = common.Direction.DOWN
            #        self._feeder.set_feeder_position(
            #                                self._current_feeder_position)
            #        wpilib.Wait(0.2)
            #    self._shooter_setup_step = 2
            #    return False
            if self._shooter_setup_step == 1:
                self._shooter.ignore_encoder_limits(True)
                self._shooter.reset_and_start_timer()
                self._shooter_setup_step = 2
                return False
            elif self._shooter_setup_step == 2:
                if self._shooter.shoot_time(2.0, common.Direction.DOWN, 0.65):
                    self._shooter_setup_step = 3
                return False
            elif self._shooter_setup_step == 3:
                self._shooter.reset_sensors()
                self._shooter.ignore_encoder_limits(False)
                self._shooter_setup_step = -1
        return True

    def _perform_tele_auto(self):
        """Perform teleop autonomous actions."""
        # Hold to shoot
        if self._hold_to_shoot_step == 2:
            self._disable_range_print = True
            self._range_print_timer.start()
            self._user_interface.output_user_message('Power: %(pwr)3.0f' %
                                             {'pwr':self._hold_to_shoot_power},
                                             True)
            if self._shooter:
                if self._shooter.shoot_time(0.1, common.Direction.DOWN, 1.0):
                    self._hold_to_shoot_step = 3
        elif self._hold_to_shoot_step == 3:
            if self._shooter:
                if self._shooter.auto_fire(self._hold_to_shoot_power):
                    self._hold_to_shoot_step = -1
        # Prep for feed
        if self._prep_for_feed_step != -1:
            if self._prep_for_feed_step == 1:
                if self._feeder:
                    self._current_feeder_position = common.Direction.DOWN
                    self._feeder.set_feeder_position(
                                                self._current_feeder_position)
                self._prep_for_feed_step = 2
            elif self._prep_for_feed_step == 2:
                if self._shooter:
                    if self._shooter.set_shooter_position(
                                                self._catapult_feed_position,
                                                1.0):
                        self._prep_for_feed_step = -1
        # Truss pass
        if self._truss_pass_step != -1:
            if self._shooter:
                #if self._shooter.auto_fire(self._truss_pass_power):
                if self._shooter.set_shooter_position(self._truss_pass_position,
                                                      1.0):
                    self._truss_pass_step = -1

    def _check_debug_request(self):
        """Print debug info to driver station."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.BACK) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.BACK)):
            self._disable_range_print = True
            self._range_print_timer.start()
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

    def _print_range(self):
        """Print the range to the nearest object."""
        if not self._disable_range_print:
            if self._drive_train:
                rng = self._drive_train.get_range()
                self._user_interface.output_user_message('Range: %(rng)4.1f' %
                                                         {'rng':rng},
                                                         True)

    def _check_ui_print_timeout(self):
        """Show any non-range message on the screen for 2 seconds."""
        if self._disable_range_print:
            elapsed_time = self._range_print_timer.elapsed_time_in_secs()
            if elapsed_time > 2.0:
                self._range_print_timer.stop()
                self._disable_range_print = False

    def _check_tele_auto_kill(self):
        """Check kill switch for all tele-auto functionality."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.SCORING,
                        userinterface.JoystickButtons.BACK) == 1):
            self._hold_to_shoot_step = -1
            self._prep_for_feed_step = -1
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

    def _check_swap_drivetrain_request(self):
        """Check if the driver wants to swap forward and reverse."""
        if (self._user_interface.get_button_state(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.RIGHTTRIGGER) == 1 and
            self._user_interface.button_state_changed(
                        userinterface.UserControllers.DRIVER,
                        userinterface.JoystickButtons.RIGHTTRIGGER)):
            self._driver_controls_swap_ratio = (self._driver_controls_swap_ratio
                                                * -1.0)
            self._disable_range_print = True
            self._range_print_timer.start()
            if self._driver_controls_swap_ratio > 0:
                self._user_interface.output_user_message(("Controls "
                                                          "normal"),
                                                         True)
            else:
                self._user_interface.output_user_message(("Controls "
                                                          "swapped"),
                                                         True)

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
                driver_left_y = driver_left_y * self._driver_controls_swap_ratio
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
                self._shooter.move_shooter(scoring_left_y)
                # Abort any relevent teleop auto routines
                self._hold_to_shoot_step = -1
                self._prep_for_feed_step = -1
                self._truss_pass_step = -1
        else:
            # Make sure we don't mess with any teleop auto routines
            # if they're running
            if (self._hold_to_shoot_step == -1 and
                self._prep_for_feed_step == -1 and
                self._truss_pass_step == -1):
                self._shooter.move_shooter(0.0)

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
            self._feeder.set_feeder_position(self._current_feeder_position)
            # Abort any relevent teleop auto routines
            self._prep_for_feed_step = -1
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
