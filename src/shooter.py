"""This module describes a catapult."""

# Imports

# If wpilib not available use pyfrc
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import common
import datalog
import parameters
import stopwatch


class Shooter(object):
    """Controls catapult shooting mechanisms.

    Provides a simple interface to shoot an exercise ball. Main functions
    are: move, auto_fire and set_position.

    Hardware: 2 Motor Controllers and 1 Encoder

    Attributes:
        encoder_enabled: true if the shooter encoder is present and initialized.
        shooter_enabled: true if the shooter is present and initialized.

    """
    # Public member variables
    encoder_enabled = None
    shooter_enabled = None

    # Private member objects
    _encoder = None
    _left_shooter_controller = None
    _right_shooter_controller = None
    _log = None
    _parameters = None
    _timer = None

    # Private parameters
    _shooter_normal_speed_ratio = None
    _shooter_min_power_speed = None
    _shooter_power_adjustment_ratio = None
    _auto_far_speed_ratio = None
    _auto_medium_speed_ratio = None
    _shooter_up_direction = None
    _shooter_down_direction = None
    _invert_multiplier = None
    _encoder_threshold = None
    _auto_far_encoder_threshold = None
    _encoder_max_limit = None
    _encoder_min_limit = None
    _time threshold = None
    _auto_medium_time_threshold = None
    _auto_far_time_threshold = None

    # Private member variables
    _encoder_count = None
    _log_enabled = None
    _parameters_file = None
    _ignore_encoder_limits = None
    _left_shooter_controller_enabled = False
    _right_shooter_controller_enabled = False

    def __init__(self, params="shooter.par", logging_enabled=False):
        """Create and initialize shooter.

        Initialize default values and read parameters from the parameter file.

        Args:
            params: The parameters filename to use for Shooter configuration.
            logging_enabled: True if logging should be enabled.

        """
        self._initialize(params, logging_enabled)

    def dispose(self):
        """Dispose of a shooter object.

        Dispose of a shooter object when it is no longer required by closing an
        open log file if it exists, and removing references to any internal
        objects.

        """
        if self._log:
            self._log.close()
        self._log = None
        self._parameters = None
        self._encoder = None
        self._left_shooter_controller = None
        self._right_shooter_controller = None
        self._timer = None

    def _initialize(self, params, logging_enabled):
        """Initialize and configure a Shooter object.

        Initialize instance variables to defaults, read parameter values from
        the specified file, instantiate required objects (encoder, controllers
        etc), and update status variables.

        Args:
            params: The parameters filename to use for Shooter configuration.
            logging_enabled: True if logging should be enabled.

        """
        # Initialize public member variables
        self.encoder_enabled = False
        self.shooter_enabled = False

        # Initialize private member objects
        self._encoder = None
        self._left_shooter_controller = None
        self._right_shooter_controller = None
        self._log = None
        self._parameters = None
        self._timer = None

        # Initialize private parameters
        self._shooter_normal_speed_ratio = 1.0
        self._auto_far_speed_ratio = 1.0
        self._auto_medium_speed_ratio =1.0
        self._auto_near_speed_ratio = 1.0
        self._shooter_up_direction = 1.0
        self._shooter_down_direction = -1.0
        self._invert_multiplier = 1.0
        self._encoder_threshold = 10
        self._auto_far_encoder_threshold = 100
        self._auto_medium_encoder_threshold = 50
        self._encoder_max_limit = 10000
        self._encoder_min_limit = 0
        self._time threshold = 0.1
        self._auto_medium_time_threshold = 0.5
        self._auto_far_time_threshold = 1.0

        # Initialize private member variables
        self._encoder_count = 0
        self._ignore_encoder_limits = False
        self._log_enabled = False
        self._robot_state = common.ProgramState.DISABLED
        self._left_shooter_controller_enabled = False
        self._right_shooter_controller_enabled = False

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("shooter.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        self._timer = stopwatch.Stopwatch()

        # Read parameters file
        self._parameters_file = params
        self.load_parameters()

    def load_parameters(self):
        """Load values from a parameter file and create and initialize objects.

        Read parameter values from the specified file, instantiate required
        objects (encoder, controller, etc), and update status variables.

        Returns:
            True if the parameter file was processed successfully.

        """
        # Define and initialize local variables
        left_shooter_channel = -1
        right_shooter_channel = -1
        encoder_a_slot = -1
        encoder_a_channel = -1
        encoder_b_slot = -1
        encoder_b_channel = -1
        encoder_reverse = 0
        encoder_type = 2
        motor_safety_timeout = 2.0

        # Initialize private parameters
        self._auto_far_speed_ratio = 1.0
        self._auto_medium_speed_ratio =1.0
        self._auto_near_speed_ratio = 1.0
        self._shooter_up_direction = 1.0
        self._shooter_down_direction = -1.0
        self._invert_multiplier = 1.0
        self._encoder_threshold = 10
        self._auto_far_encoder_threshold = 100
        self._auto_medium_encoder_threshold = 50
        self._encoder_max_limit = 10000
        self._encoder_min_limit = 0
        self._time threshold = 0.1
        self._auto_medium_time_threshold = 0.5
        self._auto_far_time_threshold = 1.0
        self._invert_left_shooter_motor = False
        self._invert_right_shooter_motor = False

        # Close and delete old objects
        self._parameters = None
        self._encoder = None
        self._left_shooter_controller = None
        self._right_shooter_controller = None

        # Read the parameters file
        self._parameters = parameters.Parameters(self._parameters_file)
        section = __name__.lower()

        # Store parameters from the file to local variables
        if self._parameters:
            #pressure_switch_channel = self._parameters.get_value(section,
            #                                    "PRESSURE_SWITCH_CHANNEL")

            #FIXME
            encoder_a_slot= self._parameters.get_value(section, "ENCODER_A_SLOT")
            encoder_a_channel = self._parameters.get_value(section, "ENCODER_A_CHANNEL")
            encoder_b_channel = self._parameters.get_value(section, "ENCODER_B_CHANNEL")
            encoder_b_slot = self._parameters.get_value(section, "ENCODER_B_SLOT")
            encoder_reverse = self._parameters.get_value(section, "ENCODER_REVERSE")
            encoder_type = self._parameters.get_value(section, "ENCODER_TYPE")
            encoder_threshold = self._parameters.get_value(section, "ENCODER_THRESHOLD")
            invert_controls = self._parameters.get_value(section, "INVERT_CONTROLS")
            shooter_normal_speed_ratio = self._parameters.get_value(section, "SHOOTER_NORMAL_SPEED_RATIO")
            auto_far_speed_ratio = self._parameters.get_value(section, "AUTO_FAR_SPEED_RATIO")
            auto_medium_speed_ratio = self._parameters.get_value(section, "AUTO_MEDIUM_SPEED_RATIO")
            self._auto_near_speed_ratio = self._parameters.get_value(section, "AUTO_NEAR_SPEED_RATIO")
            self._time_threshold = self._parameters.get_value(section, "TIME_THRESHOLD")
            auto_medium_encoder_threshold = self._parameters.get_value(section, "AUTO_MEDIUM_ENCODER_THRESHOLD")
            auto_far_encoder_threshold = self._parameters.get_value(section, "AUTO_FAR_ENCODER_THRESHOLD")
            self._auto_medium_time_threshold = self._parameters.get_value(section,"AUTO_MEDIUM_TIME_THRESHOLD")
            self._auto_far_time_threshold = self._parameters.get_value(section, "AUTO_FAR_TIME_THRESHOLD")
            encoder_max_limit = self._parameters.get_value(section, "ENCODER_MAX_LIMIT")
            encoder_min_limit = self._parameters.get_value(section, "ENCODER_MIN_LIMIT")

        # Create the encoder object if the channel is greater than 0
        self.encoder_enabled = False
        if (encoder_a_slot > 0 and encoder_a_channel > 0 and encoder_b_slot > 0 and encoder_b_channel > 0):
            self._encoder = wpilib.Encoder(encoder_a_channel, encoder_b_channel, encoder_reverse, encoder_type)
            if self._encoder:
                self.encoder_enabled = True
                self._encoder.Start()
                if self._log_enabled:
                    self._log.write_line("Encoder enabled")

        # Create the motor controller objects if the channels are greater than 0
        self._right_shooter_controller_enabled = False
        self._left_shooter_controller_enabled = False
        if right_shooter_channel > 0:
            self._right_shooter_controller = wpilib.Jaguar(
                                                        right_shooter_channel)
        if left_shooter_channel > 0:
            self._left_shooter_controller = wpilib.Jaguar(left_shooter_channel)
        if self._right_shooter_controller:
            self._right_shooter_controller_enabled = True
            if self._log_enabled:
                self._log.write_line("Right shooter motor enabled")
        if self._left_shooter_controller:
            self._left_shooter_controller_enabled = True
            if self._log_enabled:
                self._log.write_line("Left shooter motor enabled")

        # If at least one motor is working, the shooter is enabled
        self.shooter_enabled = False
        if (self._left_shooter_controller_enabled or
            self._right_shooter_controller_enabled):
            self.shooter_enabled = True
            if self._log_enabled:
                self._log.write_line("Shooter enabled")

        return True


    def set_robot_state(self, state):
        """Set the current game state of the robot.

        Store the state of the robot/game mode (disabled, teleop, autonomous)
        and perform any actions that are state related.

        Args:
            state: current robot state (ProgramState enum).

        """
        self._robot_state = state

        # Clear the movement time
        if self._timer:
            self._timer.stop()

        if state == common.ProgramState.DISABLED:
            pass
        if state == common.ProgramState.TELEOP:
            pass
        if state == common.ProgramState.AUTONOMOUS:
            pass

    def set_log_state(self, state):
        """Set the logging state for this object.

        Args:
            state: True if logging should be enabled.

        """
        if state and self._log:
            self._log_enabled = True
        else:
            self._log_enabled = False

    def reset_and_start_timer(self):
        """Resets and restarts the timer for time based movement."""
        if self._timer:
            self._timer.stop()
            self._timer.start()

    def read_sensors(self):
        """Read and store current sensor values."""

        if self.encoder_enabled:
            self._encoder_count = self._encoder.Get()

    def get_current_state(self):
        """Return a string containing sensor and status variables.

        Returns:
            A string with the encoder value

        """
        return '%(enc)3.0f' % {'enc':self._encoder_count}

    def log_current_state(self):
        """Log sensor and status variables."""
        if self._log:
            if self.encoder_enabled:
                self._log.write_value("Encoder count", self._encoder_count, True)


#FIXME


    def shoot(self, power_as_percent):
    """Power the shooting mechanism with the given power percentage.
    The power is vonverted into a motor speed and applied to the motor,
    using conversion values specified in the parameter file.

    param: power_as_percentage-> the amount of power/speed  between 0 and
                                 1.0 (or -1.0)
    """
        """Abort if shooter not available"""
        if (not self.shooter_enabled):
            return

        shooting_power_as_speed = 0.0

        """Take the power percentage and conver to a speed between 0 and
        1.0 (or -1.0)"""
        if (power_as_percentage == 0):
            shooting_power_as_speed = 0.0
        else if power_as_percentage > 0:
            shooting_power_as_speed = ((power_as_percentage * self._shooter_power_adjustment_ratio) + self._shooter_min_power_speed) * self._shooter_normal_speed_ratio
        else:
            shooting_power_as_speed = ((power_as_percentage * self._shooter_power_adjustment_ratio) - self._shooter_min_power_speed) * self._shooter_normal_speed_ratio

        """Set the controller speeed"""
        self._shooter_controller.Set(shooting_power_as_speed, 0)

    def ignore_encoder_limits(self, state):
    """Sets whether the encoder limits should be ignored or not.
    param: state-> true if the encoder limits should be ignored.
    """

        self._ignore_encoder_limits = state

