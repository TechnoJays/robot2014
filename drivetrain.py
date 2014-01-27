# Imports
import math

import wpilib

import common
import datalog
import parameters
import stopwatch


class DriveTrain(object):
    """Drives a robot.

    Provides an interface to manually or autonomously drive the robot, including
    the use of sensors to faciliatate driving.

    Attributes:
        drivetrain_enabled: True if the DriveTrain is fully functional (default False).
        accelerometer_enabled: True if the Accelerometer is fully functional (default False).
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
    _accelerometer = None
    _gyro = None
    _acceleration_timer = None
    _movement_timer = None

    # Private parameters
    _normal_linear_speed_ratio = 0
    _alternate_linear_speed_ratio = 0
    _normal_turning_speed_ratio = 0
    _alternate_turning_speed_ratio = 0
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
    _accelerometer_axis = 0

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
        self._accelerometer = None
        self._gyro = None
        self._movement_timer = None
        self._acceleration_timer = None

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
        self.accelerometer_enabled = False

        # Initialize private member objects
        self._log = None
        self._parameters = None
        self._left_controller = None
        self._right_controller = None
        self._robot_drive = None
        self._accelerometer = None
        self._gyro = None
        self._acceleration_timer = None
        self._movement_timer = None

        # Initialize private parameters
        self._normal_linear_speed_ratio = 1.0;
        self._alternate_linear_speed_ratio = 1.0;
        self._normal_turning_speed_ratio = 1.0;
        self._alternate_turning_speed_ratio = 1.0;
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

        self._movement_timer = stopwatch.Stopwatch()

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
        accelerometer_slot = -1
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
        self._gyro = None
        self._movement_timer = None
        self._acceleration_timer = None

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
            accelerometer_slot = self._parameters.get_value("ACCELEROMETER_SLOT")
            accelerometer_range = self._parameters.get_value("ACCELEROMETER_RANGE")
            self._accelerometer_axis = self._parameters.get_value("ACCELEROMETER_AXIS")
            gyro_channel = self._parameters.get_value("GYRO_CHANNEL")
            gyro_sensitivity = self._parameters.get_value("GYRO_SENSITIVITY")
            self._forward_direction = self._parameters.get_value("FORWARD_DIRECTION")
            self._backward_direction = self._parameters.get_value("BACKWARD_DIRECTION")
            self._left_direction = self._parameters.get_value("LEFT_DIRECTION")
            self._right_direction = self._parameters.get_value("RIGHT_DIRECTION")
            self._normal_linear_speed_ratio = self._parameters.get_value("NORMAL_LINEAR_SPEED_RATIO")
            self._alternate_linear_speed_ratio = self._parameters.get_value("ALTERNATE_LINEAR_SPEED_RATIO")
            self._normal_turning_speed_ratio = self._parameters.get_value("NORMAL_TURNING_SPEED_RATIO")
            self._alternate_turning_speed_ratio = self._parameters.get_value("ALTERNATE_TURNING_SPEED_RATIO")
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


        # Check if the accelerometer is present/enabled
        self.accelerometer_enabled = False
        if accelerometer_slot > 0 and accelerometer_range >= 0:
            self._accelerometer = wpilib.ADXL345_I2C(accelerometer_slot, accelerometer_range)
            if self._accelerometer:
                self.accelerometer_enabled = True
                self._acceleration_timer = stopwatch.Stopwatch()

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

        # Clear the movement time
        if self._movement_timer:
            self._movement_timer.stop()

        # Start the acceleration time and reset distance traveled
        if self.accelerometer_enabled:
            if self._acceleration_timer:
                self._acceleration_timer.stop()
                self._acceleration_timer.start()
            self._distance_traveled = 0.0

        if state == common.ProgramState.DISABLED:
            self._robot_drive.SetSafetyEnabled(True)
        if state == common.ProgramState.TELEOP:
            self._robot_drive.SetSafetyEnabled(True)
        if state == common.ProgramState.AUTONOMOUS:
            self._robot_drive.SetSafetyEnabled(False)

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
        """Read and store current sensor values.

        Reads the gyro angle to get the robots heading and the accelerometer to get
        the acceleration in the forward/backward direction of the robot.  Distance
        traveled is calculated by multiplying the acceleration value by time squared.

        """
        loop_time = 0.0

        if self.gyro_enabled:
            self._gyro_angle = self._gyro.GetAngle()

        if self.accelerometer_enabled:
            self._acceleration = self._accelerometer.GetAcceleration(self._accelerometer_axis)
            if self._acceleration_timer:
                loop_time = self._acceleration_timer.elapsed_time_in_secs()
                self._acceleration_timer.start()
                self._distance_traveled += (self._acceleration * loop_time * loop_time)

    def reset_sensors(self):
        """Reset sensors.

        Resets the gyro and accelerometer.  Also resets the distance traveled.
        """
        if self.gyro_enabled:
            self._gyro.Reset()
        if self.accelerometer_enabled:
            self._acceleration_timer.start()
            self._distance_traveled = 0.0

    def reset_and_start_timer(self):
        """Resets and restarts the timer for time based movement."""
        if self._movement_timer:
            self._movement_timer.stop()
            self._movement_timer.start()

    def get_current_state(self):
        """Return a string containing sensor and status variables.

        Returns:
            A string with the gyro angle, acceleration value, and distance traveled.
        """
        return '%(gyro)3.0f %(acc)3.2f %(dis)2.1f' % \
                {'gyro':self._gyro_angle, 'acc':self._acceleration, 'dis':self._distance_traveled}

    def log_current_state(self):
        """Log sensor and status variables."""
        if self._log:
            if self.gyro_enabled:
                self._log.WriteValue("Gyro angle", self._gyro_angle, True)
            if self.accelerometer_enabled:
                self._log.WriteValue("Acceleration", self._acceleration, True)
                self._log.WriteValue("Distance traveled", self._distance_traveled, True)

    def adjust_heading(self, adjustment, speed):
        """Turns left/right to adjust robot heading.

        Using the gyro to keep track of the current heading, turns the robot until it is
        facing the previous heading plus/minus the adjustment.

        Args:
            adjustment: the heading adjustment in degrees.
            speed: the motor speed ratio used while turning.

        Returns:
            True when the new heading has been reached.
        """
        # Abort if robot drive or gyro is not available
        if not self._robot_drive or not self.gyro_enabled:
            self._adjustment_in_progress = False
            return True

        # If this is the first time the iterative method is called, store the initial heading
        if not self._adjustment_in_progress:
            self._initial_heading = self._gyro_angle
            self._adjustment_in_progress = True

        # Calculate the amount of adjustment remaining
        angle_remaining = (self._initial_heading + adjustment) - self._gyro_angle

        # Determine the turn direction
        turn_direction = 0
        if angle_remaining < 0:
            turn_direction = self._left_direction
        else:
            turn_direction = self._right_direction

        # Check if we've reached the desired heading (within tolerance)
        if math.fabs(angle_remaining) < self._heading_threshold:
            self._robot_drive.ArcadeDrive(0.0, 0.0, False)
            self._adjustment_in_progress = False
            return True
        else:
            if math.fabs(angle_remaining) > self._auto_far_heading_threshold:
                turn_direction = turn_direction * speed * self._auto_far_turning_speed_ratio
            else if math.fabs(angle_remaining) > self._auto_medium_heading_threshold:
                turn_direction = turn_direction * speed * self._auto_medium_turning_speed_ratio
            else:
                turn_direction = turn_direction * speed * self._auto_near_turning_speed_ratio
            self._robot_drive.ArcadeDrive(0.0, turn_direction, False)

        return False

    def drive_distance(self, distance, speed):
        """Drives forward/backward a specified distance.

        Using the accelerometer to calculate distance traveled, drives the robot forward or
        backward until the distance traveled is within tolerance of the desired distance.

        Args:
            distance: the distance in meters with a negative value meaning backwards.
            speed: the motor speed ratio used while driving.

        Returns:
            True when the desired distance has been reached
        """
        # Abort if robot drive or accelerometer is not available
        if not self._robot_drive or not self.accelerometer_enabled:
            return True

        # Determine if robot should drive forward or backward
        directional_multiplier = 0
        if distance > 0:
            directional_multiplier = self._forward_direction
        else:
            directional_multiplier = self._backward_direction

        # Calculate distance left to drive
        distance_left = math.fabs(distance) - math.fabs(self._distance_traveled)

        # Check if we've reached the distance
        if distance_left < self._distance_threshold:
            # Stop driving
            self._robot_drive.ArcadeDrive(0.0, 0.0, False)
            return True
        else:
            if distance_left > self._auto_far_distance_threshold:
                directional_multiplier = directional_multiplier * speed * self._auto_far_linear_speed_ratio
            else if distance_left > self._auto_medium_distance_threshold:
                directional_multiplier = directional_multiplier * speed * self._auto_medium_linear_speed_ratio
            else:
                directional_multiplier = directional_multiplier * speed * self._auto_near_linear_speed_ratio
            self._robot_drive.ArcadeDrive(directional_multiplier, 0.0, False)

        return False

    def drive_time(self, time, direction, speed):
        """Drives forward/backward for a time duration.

        Using a timer, drives the robot forward or backward for a certain time duration.

        Args:
            time: the amount of time to drive.
            direction: the direction to drive.
            speed: the motor speed ratio.

        Returns:
            True when the time duration has been reached.
        """
        # Abort if the robot drive or timer is not available
        if not self._robot_drive or not self._movement_timer:
            return True

        # Get the timer value since we started moving
        elapsed_time = self._movement_timer.elapsed_time_in_secs()

        # Calculate time left to move
        time_left = time - elapsed_time

        # Check if we've reached the time duration
        if time_left < self._time_threshold or time_left < 0:
            self._robot_drive.ArcadeDrive(0.0, 0.0, False)
            self._movement_timer.stop()
            return True
        else:
            directional_speed = 0
            if direction == common.Direction.FORWARD:
                directional_speed = self._forward_direction
            else:
                directional_speed = self._backward_direction

            if time_left > self._auto_far_time_threshold:
                directional_speed = directional_speed * speed * self._auto_far_linear_speed_ratio
            else if time_left > self._auto_medium_time_threshold:
                directional_speed = directional_speed * speed * self._auto_medium_linear_speed_ratio
            else:
                directional_speed = directional_speed * speed * self._auto_near_linear_speed_ratio
            self._robot_drive.ArcadeDrive(directional_speed, 0.0, False)

        return False

    def drive(self, directional_speed, directional_turn, alternate):
        """Drives the robot using a specified linear and turning speed.

        This method is used in manual/teleop driving mode, where the forward/backward and
        left/right values are obtained from the driver controls.

        Args:
            directional_speed: the speed and direction for linear driving forward/backward.
            directional_turn: the speed and direction for turning left/right.
            alternate: True if the robot should move at 'alternate' speed.
        """
        # Abort if the robot drive is not available
        if not self._robot_drive:
            return

        linear = 0.0
        turn = 0.0
        # Determine the actual speed using normal/alternate speed ratios
        if alternate:
            linear = self._alternate_linear_speed_ratio * directional_speed
            turn = self._alternate_turning_speed_ratio * directional_turn
        else:
            linear = self._normal_linear_speed_ratio * directional_speed
            turn = self._normal_turning_speed_ratio * directional_turn

        # Smooth the robot acceleration/deceleration.
        # This is used to prevent tipping or jerky movement, and may not be necessary
        # depending on the robot design.
        # Method 1: using a maximum amount of change per robot iterative cycle
        if math.fabs(linear - self._previous_linear_speed) > self._maximum_linear_speed_change:
            if (linear - self._previous_linear_speed) < 0:
                linear = self._previous_linear_speed - self._maximum_linear_speed_change
            else:
                linear = self._previous_linear_speed + self._maximum_linear_speed_change
        if math.fabs(turn - self._previous_turn_speed) > self._maximum_turn_speed_change:
            if (turn - self._previous_turn_speed) < 0:
                turn = self._previous_turn_speed - self._maximum_turn_speed_change
            else
                turn = self._previous_turn_speed + self._maximum_turn_speed_change

        # Method 2: using a simple low pass filter
        # new speed = target speed - K * (target speed - current speed)
        # Where K should be around 0.8? (higher: slower rate of change)
        #linear = linear - self._linear_filter_constant * (linear - self._previous_linear_speed)
        #turn = turn - self._turn_filter_constant * (turn - self._previous_turn_speed)

        self._robot_drive.ArcadeDrive(linear, turn, False)
        self._previous_linear_speed = linear
        self._previous_turn_speed = turn

    def tank_drive(self, left_stick, right_stick, alternate):
        """Drives the robot using left and right 'tank track' controls.

        This is an alternate method used during manual/teleop driving mode, where each
        side of the robot is controlled by a separate forward/backward control, like
        tank tracks.

        Args:
            left_stick: the 'y' position of the left thumbstick to control the left track.
            right_stick: the 'y' position of the right thumbstick to control the right track.
            alternate: True if the robot should move at 'alternate' speed.
        """
        # Abort if the robot drive is not available
        if not self._robot_drive:
            return

        # Determine the actual speed using the normal/alternate speed ratios
        left = 0
        right = 0
        if alternate:
            left = self._alternate_linear_speed_ratio * left_stick
            right = self._alternate_linear_speed_ratio * right_stick
        else:
            left = self._normal_linear_speed_ratio * left_stick
            right = self._normal_linear_speed_ratio * right_stick

        self._robot_drive.TankDrive(left, right, False)

    def turn_heading(self, heading, speed):
        """Turns the robot left/right to face a specified heading.

        Using the gyro to keep track of the current heading, turns the robot until it is
        facing the specified heading.

        Args:
            heading: the desired heading in degrees.
            speed: the motor speed ratio used while turning.

        Returns:
            True when the new heading has been reached.
        """
        # Abort if the robot drive or gyro is not available
        if not self._robot_drive or not self.gyro_enabled:
            return True

        # Calculate the amount left to turn
        angle_remaining = heading - self._gyro_angle

        # Determine the turn direction
        turn_direction = 0
        if angle_remaining < 0:
            turn_direction = self._left_direction
        else:
            turn_direction = self._right_direction

        # Check if we've reached the desired heading
        if math.fabs(angle_remaining) < self._heading_threshold:
            self._robot_drive.ArcadeDrive(0.0, 0.0, False)
            return True
        else:
            if math.fabs(angle_remaining) > self._auto_far_heading_threshold:
                turn_direction = turn_direction * speed * self._auto_far_turning_ratio
            else if math.fabs(angle_remaining) > self._auto_medium_heading_threshold:
                turn_direction = turn_direction * speed * self._auto_medium_turning_ratio
            else:
                turn_direction = turn_direction * speed * self._auto_near_turning_ratio
            self._robot_drive.ArcadeDrive(0.0, turn_direction, False)

        return False

    def turn_time(self, time, direction, speed):
        """Turns the robot left/right for a time duration.

        Using a timer, turns the robot left or right for a certain time duration.

        Args:
            time: the amount of time to drive.
            direction: the direction to turn.
            speed: the motor speed ratio.

        Returns:
            True when the time duration has been reached.
        """
        # Abort if robot drive or timer is not available
        if not self._robot_drive or not self._movement_timer:
            return True

        # Get the timer value since we started moving
        elapsed_time = self._movement_timer.elapsed_time_in_secs()

        # Calculate time left to turn
        time_left = time - elapsed_time

        directional_speed = 0

        # Check if we've turned long enough
        if time_left < self._time_threshold or time_left < 0:
            self._robot_drive.ArcadeDrive(0.0, 0.0, False)
            self._movement_timer.stop()
            return True
        else:
            if direction == common.Direction.LEFT:
                directional_speed = self._left_direction
            else:
                directional_speed = self._right_direction

            if time_left > self._auto_far_time_threshold:
                directional_speed = directional_speed * speed * self._auto_far_turning_speed_ratio
            else if time_left > self._auto_medium_time_threshold:
                directional_speed = directional_speed * speed * self._auto_medium_turning_speed_ratio
            else:
                directional_speed = directional_speed * speed * self._auto_near_turning_speed_ratio
            self._robot_drive.ArcadeDrive(0.0, directional_speed, False)

        return False

    def get_heading(self):
        """Returns the current heading of the robot.

        Returns:
            The current robot heading in degrees.
        """
        return self._gyro_angle

