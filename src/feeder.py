"""This module provides a disc feeder class."""

# Imports

# If wpilib not available use pyfrc
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import common
import datalog
import parameters


class Direction(object):
    STOP = 0
    IN = 1
    OUT = 2


class Feeder(object):
    """A mechanism that pulls balls into a shooter.

    This class desribes a feeder mechanism that uses two arms with spinning
    arms to pull balls into the robot.  The arms are raised and lowered using
    compressed air and a solenoid.  A relay is used to turn the compressor on
    and off.

    Attributes:
        feeder_enabled: True if the feeder is fully functional (default False).
        compressor_enabled: True if compressor is functional (default False).
        solenoid_enabled: True if the solenoid is functional (default False).
        left_arm_enabled: True if the left arm is functional (default False).
        right_arm_enabled: True if the right arm is functional (default False).

    """
    # Public member variables
    feeder_enabled = False
    compressor_enabled = False
    solenoid_enabled = False
    left_arm_enabled = False
    right_arm_enabled = False

    # Private member objects
    _compressor = None
    _left_arm = None
    _log = None
    _parameters = None
    _right_arm = None
    _solenoid = None

    # Private parameters
    _clockwise = None
    _counter_clockwise = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _robot_state = common.ProgramState.DISABLED

    def __init__(self, params="feeder.par", logging_enabled=False):
        """Create and initialize a ball feeder.

        Instantiate a feeder and specify a parameters file and whether logging
        is enabled or disabled.

        Args:
            params: The parameters filename to use for Feeder configuration.
            logging_enabled: True if logging should be enabled.

        """
        self._initialize(params, logging_enabled)

    def dispose(self):
        """Dispose of a feeder object.

        Dispose of a feeder object when it is no longer required by closing an
        open log file if it exists, and removing references to any internal
        objects.

        """
        if self._log:
            self._log.close()
        self._log = None
        self._parameters = None
        self._compressor = None
        self._solenoid = None
        self._left_arm = None
        self._right_arm = None

    def _initialize(self, params, logging_enabled):
        """Initialize and configure a Feeder object.

        Initialize instance variables to defaults, read parameter values from
        the specified file, instantiate required objects (compressor, solenoid,
        etc), and update status variables.

        Args:
            params: The parameters filename to use for Feeder configuration.
            logging_enabled: True if logging should be enabled.

        """
        # Initialize public member variables
        self.feeder_enabled = False
        self.compressor_enabled = False
        self.solenoid_enabled = False
        self.left_arm_enabled = False
        self.right_arm_enabled = False

        # Initialize private member objects
        self._log = None
        self._parameters = None
        self._compressor = None
        self._solenoid = None
        self._left_arm = None
        self._right_arm = None

        # Initialize private parameters
        self._clockwise = None
        self._counter_clockwise = None

        # Initialize private member variables
        self._log_enabled = False
        self._robot_state = common.ProgramState.DISABLED

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("feeder.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Read parameters file
        self._parameters_file = params
        self.load_parameters()

    def load_parameters(self):
        """Load values from a parameter file and create and initialize objects.

        Read parameter values from the specified file, instantiate required
        objects (compressor, solenoid, etc), and update status variables.

        Returns:
            True if the parameter file was processed successfully.

        """
        # Define and initialize local variables
        pressure_switch_channel = -1
        compressor_relay_channel = -1
        solenoid_channel = -1
        left_arm_channel_channel = -1
        right_arm_channel_channel = -1

        # Initialize private parameters
        self._clockwise = 1.0
        self._counter_clockwise = -1.0

        # Close and delete old objects
        self._parameters = None
        self._compressor = None
        self._solenoid = None
        self._left_arm = None
        self._right_arm = None

        # Read the parameters file
        self._parameters = parameters.Parameters(self._parameters_file)
        section = __name__.lower()

        # Store parameters from the file to local variables
        if self._parameters:
            pressure_switch_channel = self._parameters.get_value(section,
                                                "PRESSURE_SWITCH_CHANNEL")
            compressor_relay_channel = self._parameters.get_value(section,
                                                "COMPRESSOR_RELAY_CHANNEL")
            solenoid_channel = self._parameters.get_value(section,
                                                "SOLENOID_CHANNEL")
            right_arm_channel = self._parameters.get_value(section,
                                                "RIGHT_ARM_CHANNEL")
            left_arm_channel = self._parameters.get_value(section,
                                                "LEFT_ARM_CHANNEL")
            self._clockwise = self._parameters.get_value(section,
                                                "CLOCKWISE")
            self._counter_clockwise = self._parameters.get_value(section,
                                                "COUNTER_CLOCKWISE")

        # Create the compressor object if the channel is greater than 0
        self.compressor_enabled = False
        if pressure_switch_channel > 0 and compressor_relay_channel > 0:
            self._compressor = wpilib.Compressor(pressure_switch_channel,
                    compressor_relay_channel)
            if self._compressor:
                self.compressor_enabled = True
                if self._log_enabled:
                    self._log.write_line("Compressor enabled")

        # Create the solenoid object if the channel is greater than 0
        self.solenoid_enabled = False
        if solenoid_channel > 0:
            self._solenoid = wpilib.Solenoid(solenoid_channel)
            if self._solenoid:
                self.solenoid_enabled = True
                if self._log_enabled:
                    self._log.write_line("Solenoid enabled")

        # Create the motor controller objects if the channels are greater than 0
        self.right_arm_enabled = False
        self.left_arm_enabled = False
        if right_arm_channel > 0:
            self._right_arm = wpilib.Jaguar(right_arm_channel)
        if left_arm_channel > 0:
            self._left_arm = wpilib.Jaguar(left_arm_channel)
        if self._right_arm:
            self.right_arm_enabled = True
            if self._log_enabled:
                self._log.write_line("Right arm enabled")
        if self._left_arm:
            self.left_arm_enabled = True
            if self._log_enabled:
                self._log.write_line("Left arm enabled")

        # If the compressor, solenoid,and one of the arms are enabled,
        # the feeder is fully functional
        self.feeder_enabled = False
        if (self.compressor_enabled and self.solenoid_enabled and
            (self.left_arm_enabled or self.right_arm_enabled)):
            self.feeder_enabled = True
            if self._log_enabled:
                self._log.write_line("Feeder enabled")

        return True

    def set_robot_state(self, state):
        """Set the current game state of the robot.

        Store the state of the robot/game mode (disabled, teleop, autonomous)
        and perform any actions that are state related.

        Args:
            state: current robot state (ProgramState enum).

        """
        self._robot_state = state

        # Make sure the compressor is running in every state
        if self.compressor_enabled:
            if not self._compressor.Enabled():
                self._compressor.Start()

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

    def set_position(self, direction):
        """Set the feeder arms up or down.

        Args:
            direction: common.Direction enumeration of up or down.

        """
        if self.solenoid_enabled and self.compressor_enabled:
            if direction == common.Direction.UP:
                self._solenoid.Set(False)
            elif direction == common.Direction.DOWN:
                self._solenoid.Set(True)

    def feed(self, direction, speed):
        """Conrol the arm that feed the ball into the robot.

        Args:
            direction: Direction enumeration of in, out, stop.
            speed: The speed that you feed that ball.

        """
        if direction == Direction.IN:
            if self.right_arm_enabled:
                self._right_arm.Set(self._clockwise * speed, 0)
            if self.left_arm_enabled:
                self._left_arm.Set(self._counter_clockwise * speed, 0)
        elif direction == Direction.OUT:
            if self.right_arm_enabled:
                self._right_arm.Set(self._counter_clockwise * speed, 0)
            if self.left_arm_enabled:
                self._left_arm.Set(self._clockwise * speed, 0)
        elif direction == Direction.STOP:
            if self.right_arm_enabled:
                self._right_arm.Set(0.0, 0)
            if self.left_arm_enabled:
                self._left_arm.Set(0.0, 0)

