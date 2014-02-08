"""This module provides a disc feeder class."""

# Imports

# If wpilib not available use pyfrc
try
    import wpilib
except ImportError:
    import pyfrc as wpilib
import common
import datalog
import parameters


class Feeder(object):
    """A mechanism that feeds frisbees to a shooter.

    This class desribes a feeder mechanism that uses an air compressor and a
    solenoid to push a frisbee into the shooting mechanism.  A relay is used
    to turn the compressor on and off, which powers a solenoid piston that does
    the actual pushing.

    Attributes:
        feeder_enabled: True if the feeder is fully functional (default False).
        compressor_enabled: True if compressor is functional (default False).
        solenoid_enabled: True if the solenoid is functional (default False).

    """
    # Public member variables
    feeder_enabled = False
    compressor_enabled = False
    solenoid_enabled = False

    # Private member objects
    _compressor = None
    _log = None
    _parameters = None
    _piston = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _robot_state = common.ProgramState.DISABLED

    def __init__(self, params="feeder.par", logging_enabled=False):
        """Create and initialize a frisbee feeder.

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
        self._piston = None

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

        # Initialize private member objects
        self._log = None
        self._parameters = None
        self._compressor = None
        self._piston = None

        # Initialize private parameters

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
        parameters_read = False

        # Close and delete old objects
        self._parameters = None
        self._compressor = None
        self._piston = None

        # Read the parameters file
        self._parameters = parameters.Parameters(self._parameters_file)
        if self._parameters and self._parameters.file_opened:
            parameters_read = self._parameters.read_values()
            self._parameters.close()

        if self._log_enabled:
            if parameters_read:
                self._log.write_line("Feeder parameters loaded successfully")
            else:
                self._log.write_line("Failed to read Feeder parameters")

        # Store parameters from the file to local variables
        if parameters_read:
            pressure_switch_channel = self._parameters.get_value(
                    "PRESSURE_SWITCH_CHANNEL")
            compressor_relay_channel = self._parameters.get_value(
                    "COMPRESSOR_RELAY_CHANNEL")
            solenoid_channel = self._parameters.get_value(
                    "SOLENOID_CHANNEL")

        # Create the compressor object if the channel is greater than 0
        self.compressor_enabled = False
        if pressure_switch_channel > 0 and compressor_relay_channel > 0:
            self._compressor = wpilib.Compressor(pressure_switch_channel,
                    compressor_relay_channel)
            if self._compressor:
                self.compressor_enabled = True

        # Create the solenoid object if the channel is greater than 0
        self.solenoid_enabled = False
        if solenoid_channel > 0:
            self._piston = wpilib.Solenoid(solenoid_channel)
            if self._piston:
                self.solenoid_enabled = True

        # If both the compressor and solenoid are enabled, the feeder is
        # fully functional
        if self.compressor_enabled and self.solenoid_enabled:
            self.feeder_enabled = True
        else:
            self.feeder_enabled = False

        if self._log_enabled:
            if self.compressor_enabled:
                self._log.write_line("Compressor enabled")
            else:
                self._log.write_line("Compressor disabled")
            if self.solenoid_enabled:
                self._log.write_line("Solenoid enabled")
            else:
                self._log.write_line("Solenoid disabled")
            if self.feeder_enabled:
                self._log.write_line("Feeder enabled")
            else:
                self._log.write_line("Feeder disabled")

        return parameters_read

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

    def set_piston(self, state):
        """Set the state of the feeder piston.

        Setting to True will extend the piston, False will retract the piston.
        This uses the solenoid powered by compressed air.

        Args:
            state: True if the piston is extended.

        """
        if self.feeder_enabled and self.solenoid_enabled:
            self._piston.Set(state)

