# Imports
import wpilib
import common
import datalog
import parameters

class DriveTrain(object):
    """Drives a robot.

    Provides an interface to manually or autonomously drive the robot, including
    the use of sensors to faciliatate driving.

    Attributes:
        drivetrain_enabled: True if the DriveTrain is fully functional (default False).

    """
    # Public member variables
    drivetrain_enabled = False

    # Private member objects
    _log = None
    _parameters = None

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _robot_state = common.ProgramState.DISABLED

    def __init__(self):
        """Create and initialize a DriveTrain.

        Instantiate a DriveTrain using default values.

        """
        self._initialize("parameters.par", False)

    def __init__(self, logging_enabled):
        """Create and initialize a DriveTrain.

        Instantiate a DriveTrain and specify if logging is enabled or disabled.

        Args:
            logging_enabled: True if logging should be enabled.

        """
        self._initialize("parameters.par", logging_enabled)

    def __init__(self, parameters):
        """Create and initialize a DriveTrain.

        Instantiate a DriveTrain and specify a parameters file.

        Args:
            parameters: The parameters filename to use for configuration.

        """
        self._initialize(parameters, False)

    def __init__(self, parameters, logging_enabled):
        """Create and initialize a DriveTrain.

        Instantiate a DriveTrain and specify a parameters file and whether logging
        is enabled or disabled.

        Args:
            parameters: The parameters filename to use for configuration.
            logging_enabled: True if logging should be enabled.

        """
        self._initialize(parameters, logging_enabled)

    def dispose(self):
        """Dispose of a DriveTrain object.

        Dispose of a DriveTrain object when it is no longer required by closing an
        open log file if it exists, and removing references to any internal
        objects.

        """
        if self._log:
            self._log.close()
        self._log = None
        self._parameters = None

    def _initialize(self, parameters, logging_enabled):
        """Initialize and configure a DriveTrain object.

        Initialize instance variables to defaults, read parameter values from
        the specified file, instantiate required objects and update status
        variables.

        Args:
            parameters: The parameters filename to use for configuration.
            logging_enabled: True if logging should be enabled.

        """
        # Initialize public member variables
        self.drivetrain_enabled = False

        # Initialize private member objects
        self._log = None
        self._parameters = None

        # Initialize private parameters

        # Initialize private member variables
        self._log_enabled = False
        self._robot_state = common.ProgramState.DISABLED

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("drivetrain.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Read parameters file
        self._parameters_file = parameters
        self.load_parameters()

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
                self._log.write_line("DriveTrain parameters loaded successfully")
            else:
                self._log.write_line("Failed to read DriveTrain parameters")

        # Store parameters from the file to local variables
        if parameters_read:
            pass

        # TODO

        return parameters_read

    def set_robot_state(self, state):
        """Set the current game state of the robot.

        Store the state of the robot/game mode (disabled, teleop, autonomous)
        and perform any actions that are state related.

        Args:
            state: current robot state (ProgramState enum).

        """
        self._robot_state = state

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

