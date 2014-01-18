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
        accelerometer_enabled: True if the Acceleromter is fully functional (default False).
        gyro_enabled: True if the Gyro is fully functional (default False).

    """
    # Public member variables
    drivetrain_enabled = False
    accelerometer_enabled = False
    gyro_enabled = False

    # Private member objects
    _log = None
    _parameters = None
    _left_controller = None
    _right_controller = None
    _robot_drive = None
    _acceleromter = None
    _gyro = None
    # TODO _acceleration_timer
    # TODO _timer

    # Private parameters
    _normal_linear_speed_ratio = 0
    _turbo_linear_speed_ratio = 0
    _normal_turning_speed_ratio = 0
    _turbo_turning_speed_ratio = 0
    _auto_far_linear_speed_ratio = 0
    _auto_medium_linear_speed_ratio = 0
    _auto_near_linear_speed_ratio = 0
    _auto_far_turning_speed_ratio = 0
    _auto_medium_turning_speed_ratio = 0
    _auto_near_turning_speed_ratio = 0
    _forward_direction = 0
    _backward_direction = 0
    _left_direction = 0
    _right_direction = 0
    _linear_filter_constant = 0
    _turn_filter_constant = 0
    _maximum_linear_speed_change = 0
    _maximum_turn_speed_change = 0
    _time_threshold = 0
    _auto_medium_time_threshold = 0
    _auto_far_time_threshold = 0
    _distance_threshold = 0
    _auto_medium_distance_threshold = 0
    _auto_far_distance_threshold = 0
    _heading_threshold = 0
    _auto_medium_heading_threshold = 0
    _auto_far_heading_threshold = 0
    _acceleromter_axis = 0

    # Private member variables
    _log_enabled = False
    _parameters_file = None
    _robot_state = common.ProgramState.DISABLED
    _acceleration = 0
    _distance_traveled = 0
    _gyro_angle = 0
    _initial_heading = 0
    _previous_linear_speed = 0
    _previous_turn_speed = 0
    _adjustment_in_progress = False

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
        self._left_controller = None
        self._right_controller = None
        self._robot_drive = None
        self._acceleromter = None
        self._gyro = None
        # TODO _acceleration_timer
        # TODO _timer

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
        self.gyro_enabled = False
        self.acceleromter_enabled = False

        # Initialize private member objects
        self._log = None
        self._parameters = None
        self._left_controller = None
        self._right_controller = None
        self._robot_drive = None
        self._acceleromter = None
        self._gyro = None
        # TODO _acceleration_timer
        # TODO _timer

        # Initialize private parameters
        self._normal_linear_speed_ratio = 1.0;
        self._turbo_linear_speed_ratio = 1.0;
        self._normal_turning_speed_ratio = 1.0;
        self._turbo_turning_speed_ratio = 1.0;
        self._auto_far_linear_speed_ratio = 1.0;
        self._auto_medium_linear_speed_ratio = 1.0;
        self._auto_near_linear_speed_ratio = 1.0;
        self._auto_far_turning_speed_ratio = 1.0;
        self._auto_medium_turning_speed_ratio = 1.0;
        self._auto_near_turning_speed_ratio = 1.0;
        self._auto_medium_time_threshold = 0.5;
        self._auto_far_time_threshold = 1.0;
        self._auto_medium_distance_threshold = 2.0;
        self._auto_far_distance_threshold = 5.0;
        self._auto_medium_heading_threshold = 15.0;
        self._auto_far_heading_threshold = 25.0;
        self._distance_threshold = 0.5;
        self._heading_threshold = 3.0;
        self._time_threshold = 0.1;
        self._forward_direction = 1.0;
        self._backward_direction = -1.0;
        self._left_direction = -1.0;
        self._right_direction = 1.0;
        self._accelerometer_axis = 0;
        self._maximum_linear_speed_change = 0.0;
        self._maximum_turn_speed_change = 0.0;
        self._linear_filter_constant = 0.0;
        self._turn_filter_constant = 0.0;

        # Initialize private member variables
        self._log_enabled = False
        self._robot_state = common.ProgramState.DISABLED
        self._parameters_file = None
        self._acceleration = 0
        self._distance_traveled = 0
        self._gyro_angle = 0
        self._initial_heading = 0
        self._previous_linear_speed = 0
        self._previous_turn_speed = 0
        self._adjustment_in_progress = False

        # Enable logging if specified
        if logging_enabled:
            # Create a new data log object
            self._log = datalog.DataLog("drivetrain.log")

            if self._log and self._log.file_opened:
                self._log_enabled = True
            else:
                self._log = None

        # Create a timer object
        # TODO

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
        left_motor_slot = -1
        left_motor_channel = -1
        left_motor_inverted = 0
        right_motor_slot = -1
        right_motor_channel = -1
        right_motor_inverted = 0
        acceleromter_slot = -1
        accelerometer_range = -1
        gyro_channel = -1
        gyro_sensitivity = 0.007
        motor_safety_timeout = 2.0
        parameters_read = False

        # Close and delete old objects
        self._parameters = None
        self._robot_drive = None
        self._left_controller = None
        self._right_controller = None
        self._accelerometer = None
        # TODO accel timer
        self._gyro = None

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
            left_motor_slot = self._parameters.get_value("LEFT_MOTOR_SLOT")
            left_motor_channel = self._parameters.get_value("LEFT_MOTOR_CHANNEL")
            left_motor_inverted = self._parameters.get_value("LEFT_MOTOR_INVERTED")
            right_motor_slot = self._parameters.get_value("RIGHT_MOTOR_SLOT")
            right_motor_channel = self._parameters.get_value("RIGHT_MOTOR_CHANNEL")
            right_motor_inverted = self._parameters.get_value("RIGHT_MOTOR_INVERTED")
            motor_safety_timeout = self._parameters.get_value("MOTOR_SAFETY_TIMEOUT")
            acceleromter_slot = self._parameters.get_value("ACCELEROMETER_SLOT")
            acceleromter_range = self._parameters.get_value("ACCELEROMETER_RANGE")
            self._accelerometer_axis = self._parameters.get_value("ACCELEROMETER_AXIS")
            gyro_channel = self._parameters.get_value("GYRO_CHANNEL")
            gyro_sensitivity = self._parameters.get_value("GYRO_SENSITIVITY")
            self._forward_direction = self._parameters.get_value("FORWARD_DIRECTION")
            self._backward_direction = self._parameters.get_value("BACKWARD_DIRECTION")
            self._left_direction = self._parameters.get_value("LEFT_DIRECTION")
            self._right_direction = self._parameters.get_value("RIGHT_DIRECTION")
            self._normal_linear_speed_ratio = self._parameters.get_value("NORMAL_LINEAR_SPEED_RATIO")
            self._turbo_linear_speed_ratio = self._parameters.get_value("TURBO_LINEAR_SPEED_RATIO")
            self._normal_turning_speed_ratio = self._parameters.get_value("NORMAL_TURNING_SPEED_RATIO")
            self._turbo_turning_speed_ratio = self._parameters.get_value("TURBO_TURNING_SPEED_RATIO")
            self._auto_far_linear_speed_ratio = self._parameters.get_value("AUTO_FAR_LINEAR_SPEED_RATIO")
            self._auto_medium_linear_speed_ratio = self._parameters.get_value("AUTO_MEDIUM_LINEAR_SPEED_RATIO")
            self._auto_near_linear_speed_ratio = self._parameters.get_value("AUTO_NEAR_LINEAR_SPEED_RATIO")
            self._auto_far_turning_speed_ratio = self._parameters.get_value("AUTO_FAR_TURNING_SPEED_RATIO")
            self._auto_medium_turning_speed_ratio = self._parameters.get_value("AUTO_MEDIUM_TURNING_SPEED_RATIO")
            self._auto_near_turning_speed_ratio = self._parameters.get_value("AUTO_NEAR_TURNING_SPEED_RATIO")
            self._distance_threshold = self._parameters.get_value("DISTANCE_THRESHOLD")
            self._heading_threshold = self._parameters.get_value("HEADING_THRESHOLD")
            self._time_threshold = self._parameters.get_value("TIME_THRESHOLD")
            self._auto_medium_time_threshold = self._parameters.get_value("AUTO_MEDIUM_TIME_THRESHOLD")
            self._auto_far_time_threshold = self._parameters.get_value("AUTO_FAR_TIME_THRESHOLD")
            self._auto_medium_distance_threshold = self._parameters.get_value("AUTO_MEDIUM_DISTANCE_THRESHOLD")
            self._auto_far_distance_threshold = self._parameters.get_value("AUTO_FAR_DISTANCE_THRESHOLD")
            self._auto_medium_heading_threshold = self._parameters.get_value("AUTO_MEDIUM_HEADING_THRESHOLD")
            self._auto_far_heading_threshold = self._parameters.get_value("AUTO_FAR_HEADING_THRESHOLD")
            self._maximum_linear_speed_change = self._parameters.get_value("MAXIMUM_LINEAR_SPEED_CHANGE")
            self._maximum_turn_speed_change = self._parameters.get_value("MAXIMUM_TURN_SPEED_CHANGE")
            self._linear_filter_constant = self._parameters.get_value("LINEAR_FILTER_CONSTANT")
            self._turn_filter_constant = self._parameters.get_value("TURN_FILTER_CONSTANT")


        # Check if the acceleromter is present/enabled
        self.accelerometer_enabled = False
        if acceleromter_slot > 0 and acceleromter_range >= 0:
            self._accelerometer = wpilib.ADXL345_I2C(accelerometer_slot, accelerometer_range)
            if self._accelerometer:
                self.accelerometer_enabled = True
                #TODO create accel timer

        # Check if gyro is present/enabled
        self.gyro_enabled = False
        if gyro_channel > 0:
            self._gyro = wpilib.Gyro(gyro_channel)
            if self._gyro:
                self._gyro.SetSensitivity(gyro_sensitivity)
                self.gyro_enabled = True

        # Create motor controllers
        if left_motor_slot > 0 and left_motor_channel > 0:
            self._left_controller = wpilib.Jaguar(left_motor_slot, left_motor_channel)
        if right_motor_slot > 0 and right_motor_channel > 0:
            self._right_controller = wpilib.Jaguar(right_motor_slot, right_motor_channel)

        # Create RobotDrive using motor controllers
        if self._left_motor_controller and self._right_motor_controller:
            self._robot_drive = wpilib.RobotDrive(self._left_controller, self._right_controller)
            self._robot_drive.SetExpiration(motor_safety_timeout)
            self._robot_drive.SetSafetyEnabled(True)

        # Invert motors if specified
        if left_motor_inverted and self._robot_drive:
            self._robot_drive.SetInvertedMotor(wpilib.RobotDrive.kRearLeftMotor, True)
        if right_motor_inverted and self._robot_drive:
            self._robot_drive.SetInvertedMotor(wpilib.RobotDrive.kRearRightMotor, True)

        if self._log_enabled:
            if self.accelerometer_enabled:
                self._log.WriteLine("Accelerometer enabled\n")
            else:
                self._log.WriteLine("Accelerometer disabled\n")
            if self.gyro_enabled:
                self._log.WriteLine("Gyro enabled\n")
            else:
                self._log.WriteLine("Gyro disabled\n")

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

    def read_sensors(self):

    def reset_sensors(self):

    def reset_and_start_timer(self):

    def get_current_state(self):

    def log_current_state(self):

    def adjust_heading(self, adjustment, speed):

    def drive_distance(self, distance, speed):

    def drive_time(self, time, direction, speed):

    def drive(self, directional_speed, directional_turn, turbo):

    def tank_drive(self, left_stick, right_stick, turbo):

    def turn_heading(self, heading, speed):

    def turn_time(self, time, direction, speed):

    def get_heading(self):

