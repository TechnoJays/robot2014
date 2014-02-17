"""Shooter Module"""

#Import
import wpilib """Includes Jaguar and Encoder classes"""
import math
import datalog
import parameters
import stopwatch
import common



class Shooter(object):
	"""Controls catapult Shooting mechanisms
    
	Provides a simple interface to shoot an exercise ball. Main functions
	are: move, auto fire and set position. 
	
    Hardware: 2 Motor Controllers and 1 Encoder
	
	Attributes:
	    encoder_enabled: true if the shooter encoder is present and initialized.
		rhs_shooter_enabled: true if the right hand side (rhs) catapult motor is present
		                    and initialized.
		lhs_shooter_enabled: true id the left hand side (lhs) catapult motor is present
		                    and initialized.
		_encoder: encoder used to track current catapult position. 
		_rhs_shooter_controller: motor controller used to move rhs shooter arm.
		_lhs_shooter_controller: motor controller used to move lhs shooter arm. 
		_log: log object used to log data or status comments to a file
	
	
    """
	
    # Public member variables
    encoder_enabled = None
	pitch_enabled = None
	shooter_enabled = None

    # Private member objects
	_encoder = None
    _pitch_controller = None
	_shooter_controller = None
	_log = None
	_parameters = None
	_timer = None
	
	# Private parameters
	_shooter_normal_speed_ratio = None
	_shooter_min_power_speed = None
	_shooter_power_adjustment_ratio = None
	_pitch_normal_speed_ratio = None
	_pitch_turbo_speed_ratio = None
	_auto_far_speed_ratio = None
	_auto_medium_speed_ratio = None
	_pitch_up_direction = None
	_pitch_down_direction = None
	_shoot_forward_direction = None
	_shoot_backward_direction = None
	_invert_multiplier = None
	_encoder_threshold = None
	_auto_far_encoder_threshold = None
	_encoder_max_limit = None
	_encoder_min_limit = None
	_time threshold = None
	_auto_medium_time_threshold = None
	_auto_far_time_threshold = None
	_angle_linear_fit_gradient = None
	_angle_linear_fit_constant = None
	_fulcrum_clear_encoder_count = None

    # Private member variables 
    _encoder_count = None
	_log_enabled = None
	_parameters_file = None
	_ignore_encoder_limits = None
	

    def __init__(self, parameters="shooter.par", logging_enabled):
		"""Initialize Shooter
		
		Initialize default values and read parameters from the parameter file.
		
		param:	parameters-> path of parameter file, default name is "shooter.par" 
				logging_enabled-> logging_enabled true if logging is enabled. 
		"""
		
		""" Initialize public member variables
		
		"""
		self.encoder_enabled = False
		self.shooter_enabled = False
		self.pitch_enabled = False
		
		"""Initialize private member objects
		
		Create a microcontroller to move the pitch
		Create a microcontroller to move the shooter
		Create an encoder to track pitch postion
		Create a timer for autonomous function
		
		************Must update parameters inside of objects************
		"""
		self._pitch_controller = wpilib.Jaguar()
		self._shooter_controller = wpilib.Jaguar()
		self._encoder = wpilib.Encoder()
		self._timer = stopwatch.Stopwatch()		
		self._log = datalog.Datalog("shooter.log")
		
		
		
		"""Initialize Private Parameter Values"""
		self._invert_multiplier = 0.0;
		self._shooter_normal_speed_ratio = 1.0;
		self._pitch_normal_speed_ratio = 1.0;
		self._pitch_turbo_speed_ratio = 1.0;
		self._auto_far_speed_ratio = 1.0;
		self._auto_medium_speed_ratio = 1.0;
		self._auto_near_speed_ratio = 1.0;	
		self._auto_medium_encoder_threshold = 50;
		self._auto_far_encoder_threshold = 100;
		self._auto_medium_time_threshold = 0.5;
		self._auto_far_time_threshold = 1.0;
		self._encoder_threshold = 10;
		self._pitch_up_direction = 1.0;
		self._pitch_down_direction = -1.0;
		self._shoot_forward_direction = 1.0;
		self._shoot_backward_direction = -1.0;
		self._time_threshold = 0.1;
		self._encoder_max_limit = -1;
		self._encoder_min_limit = -1;
		self._shooter_min_power_speed = 0.4;
		self._shooter_power_adjustment_ratio = 0.006;
		self._angle_linear_fit_gradient = 1.0;
		self._angle_linear_fit_constant = 0.0;
		self._fulcrum_clear_encoder_count = 0;

		"""Initialize private member variables
	
		"""
		self._encoder_count = 0
		self._log_enabled = False
		self._ignore_encoder_limits = False
		
		""" Enable logging if specified by logging_enabled parameter"""
		if _log == not None and _log.file_opened == True:
			self.log_enabled = logging_enabled
		else:
			self._log_enabled = False
		
		
		"""Storing parameter file name from user in _parameter"""
		self._parameters_file = parameters
		
		load_parameters()
		
		
	def load_parameters(self):
		"""Define and initialize local variables"""
		
		pitch_motor_slot = -1;
		pitch_motor_channel = -1;
		shooter_motor_slot = -1;
		shooter_motor_channel = -1;
		encoder_a_slot = -1;
		encoder_a_channel = -1;
		encoder_b_slot = -1;
		encoder_b_channel = -1;
		encoder_reverse = 0;
		encoder_type = 2;
		invert_controls = 0;
		motor_safety_timeout = 2.0;
		section_name = None;	
		
		"""Attempt to read parameters file"""
		self._parameters = parameter.Parameters(self._parameters_file, "r")
		if (self._parameters !== None and self._parameters.file_opened == True):
			section_name = __name__.lower()
		else:
		
		"""Log whether shooter parameters where loaded successfully."""
		if self.log_enabled == True:
			if section_name == not None:
				self._log.write_line("Shooter paramters loaded successfully\n")
			else:
				self._log.write_line("Shooter paramters failed to read\n")
		
		if parameter_read = not False:
			shooter_motor_slot = self._parameters.get_value(section_name, "SHOOTER_MOTOR_SLOT")
			shooter_motor_channel = self._parameters.get_value(section_name, "SHOOTER_MOTOR_CHANNEL")
			pitch_motor_slot = self._parameters.get_value(section_name, "PITCH_MOTOR_SLOT")
			pitch_motor_channel = self._parameters.get_value(section_name, "PITCH_MOTOR_CHANNEL")
			encoder_a_slot= self._parameters.get_value(section_name, "ENCODER_A_SLOT")
			encoder_a_channel = self._parameters.get_value(section_name, "ENCODER_A_CHANNEL")
			encoder_b_channel = self._parameters.get_value(section_name, "ENCODER_B_CHANNEL")
			encoder_b_slot = self._parameters.get_value(section_name, "ENCODER_B_SLOT")
			encoder_reverse = self._parameters.get_value(section_name, "ENCODER_REVERSE")
			encoder_type = self._parameters.get_value(section_name, "ENCODER_TYPE")
			encoder_threshold = self._parameters.get_value(section_name, "ENCODER_THRESHOLD")
			motor_safety_timeout = self._parameters.get_value(section_name, "MOTOR_SAFETY_TIMEOUT" )
			invert_controls = self._parameters.get_value(section_name, "INVERT_CONTROLS")
			self._pitch_up_direction = self._parameters.get_value(section_name, "PITCH_UP_DIRECTION")
			self._pitch_down_direction = self._parameters.get_value(section_name, "PITCH_DOWN_DIRECTION")
			self._pitch_normal_speed_ratio = self._parameters.get_value(section_name, "PITCH_NORMAL_SPEED_RATIO")
			self._pitch_turbo_speed_ratio = self._parameters.get_value(section_name, "PITCH_TURBO_SPEED_RATIO")
			shooter_normal_speed_ratio = self._parameters.get_value(section_name, "SHOOTER_NORMAL_SPEED_RATIO")
			auto_far_speed_ratio = self._parameters.get_value(section_name, "AUTO_FAR_SPEED_RATIO")
			auto_medium_speed_ratio = self._parameters.get_value(section_name, "AUTO_MEDIUM_SPEED_RATIO")
			self._auto_near_speed_ratio = self._parameters.get_value(section_name, "AUTO_NEAR_SPEED_RATIO")
			self._time_threshold = self._parameters.get_value(section_name, "TIME_THRESHOLD")
			auto_medium_encoder_threshold = self._parameters.get_value(section_name, "AUTO_MEDIUM_ENCODER_THRESHOLD")
 			auto_far_encoder_threshold = self._parameters.get_value(section_name, "AUTO_FAR_ENCODER_THRESHOLD")
 			self._auto_medium_time_threshold = self._parameters.get_value(section_name,"AUTO_MEDIUM_TIME_THRESHOLD")
 			self._auto_far_time_threshold = self._parameters.get_value(section_name, "AUTO_FAR_TIME_THRESHOLD")
 			encoder_max_limit = self._parameters.get_value(section_name, "ENCODER_MAX_LIMIT")
 			encoder_min_limit = self._parameters.get_value(section_name, "ENCODER_MIN_LIMIT")
 			shoot_forward_direction = self._parameters.get_value(section_name, "SHOOT_FORWARD_DIRECTION")
 			shoot_backward_direction = self._parameters.get_value(section_name, "SHOOT_BACKWARD_DIRECTION")
 			shooter_min_power_speed = self._parameters.get_value(section_name, "SHOOTER_MIN_POWER_SPEED")
 			self._shooter_power_adjustment_ratio = self._parameters.get_value(section_name, "SHOOTER_POWER_ADJUSTMENT_RATIO")
 			angle_linear_fit_gradinet = self._parameters.get_value(section_name, "ANGLE_LINEAR_FIT_GRADINET")
 			self._angle_linear_fit_constant = self._parameters.get_value(section_name, "ANGLE_LINEAR_FIT_CONSTANT")
 			self._fulcrum_clear_encoder_count = self._parameters.get_value(section_name, "FULCRUM_CLEAR_ENCODER_COUNT")
		

		"""Check if shooter encoder is present/enabled and starts counting the encoder"""
		if (encoder_a_slot > 0 and encoder_a_channel > 0 and encoder_b_slot > 0 and encoder_b_channel > 0):
			self._encoder = wpilib.Encoder(encoder_a_channel, encoder_b_channel, encoder_reverse, encoder_type)
				if self._encoder == not None:
					self.encoder_enabled = True
					self._encoder.Start()
				else:
		else:
			self.encoder_enabled = False
		
		"""Check if the pitch motor is present/enabled"""
		if (pitch_motor_slot > 0 and pitch_motor_channel > 0):
			self._pitch_controller = wpilib.Jaguar(pitch_motor_slot, pitch_motor_channel)
			if (self._pitch_controller == not None):
				self._pitch_controller.SetExpiration(motor_safety_timeout)
				self._pitch_controller.SetSafetyEnabled(True)
				self.pitch_enabled = True
			else:
		else:
			self.pitch_enabled = False
		
		
		"""Check if the shooter motor is present/enabled"""
		if (shooter_motor_slot > 0 and shooter_motor_channel > 0):
			self._shooter_controller = wpilib.Jaguar(shooter_motor_slot, shooter_motor_channel)
			if (self._shooter_controller == not None):
				self._shooter_controller.SetExpiration(motor_safety_timeout)
				self._shooter_controller.SetSafetyEnabled(True)
				self.shooter_enabled = True
			else:
		else:
			self.shooter_enabled = False
		
		"""Lets Log whether the Encoder, Pitch Motor and Shooter Motor are 
		enabled/disabled
		"""
		if self._log_enabled == True:
			if self.encoder_enabled == True:
				self._log.writeline("Shooter encoder enabled\n")
			else:
				self._log.writeline("Shooter encoder disabled\n")
			if self.pitch_enabled == True:
				self._log.writeline("Pitch motor enabled\n")
			else:
				self._log.writeline("Pitch motor disabled\n")
			if self.shooter_enabled == True:
				self._log.writeline("Shooter motor enabled\n")
			else:
				self._log.writeline("Shooter motor disabled\n")
		
		"""Set the inversion multipler depending on the controls settings"""
		if invert_controls == True:
			self.invert_multiplier = -1
		else:
			self.invert_multiplier = 1
		
		return True
	
	def read_sensors(self)
	""" Read and store current encoder value"""
		if encoder_enabled == True:
			self._encoder_count = self._encoder.Get()
		else:
		
	def reset_and_start_timer(self)
	"""Resets and restarts the timer for the time based movement in Shooter class"""
		if (self._timer == not None)
			self._timer.stop()
			self._timer.reset()
			self._timer.start()
		else:
		
	def set_robot_state(self, state)
	"""Set the current state of the robot and perform any action 
	necessary during mode changes
	
	param:	state-> state current robot state
	"""
		
		"""Stop the timer on any state change."""
		if self._timer == not None:
			self._timer.stop()
		else:
		
		"""Adjust motor safety checks depending on the robot state"""
		if state == common.ProgramState.DISABLED:
			if self.pitch_enabled == True:
				self._pitch_controller.SetSafetyEnabled(True)
			else:
			if self.shooter_enabled == True:
				self._shooter_controller.SetSafetyEnabled(True)
			else:
		else if state == common.ProgramState.TELEOP:
			if self.pitch_enabled == True:
				self._pitch_controller.SetSafetyEnabled(True)
			if self.shooter_enabled == True:
				self._shooter_controller.SetSafetyEnabled(True)
		else if state == common.ProgramState.AUTONOMOUS:
			if self.pitch_enabled == True:
				self._pitch_controller.SetSafetyEnabled(False)
			if self.shooter_enabled == True:
				self._shooter_controller.SetSafetyEnabled(False)		
		else:
	
	def get_current_state(self):
	"""Return encoder count"""
		if self.encoder_enabled == True:
			return self._encoder_count
		else:
			return None
	
	def log_current_state(self):
	""" Log encoder and count with timestamp when requested"""
		if self._log == not None:
			if self.encoder_enabled == True:
				self._log.write_value("Encoder count", self._encoder_count, True)
			else:
		else:
		
	def set_log_state(self, state):
	"""Enable or disable logging for this object
	
	param: state -> set true if logging should be enabled
	"""
		if state == True and self._log == not None:
			self.log_enabled = True
		else:
			self.log_enabled = False
			
	def set_pitch(self, time, direction, speed):
	""" Set the shooter pitch to a position provided by the argument.
	
	param:	time-> amount of time to move the pitch
			direction-> the direction to move the pitch
			speed-> motor speed ratio
			return-> true when the desired position is reached
	"""
	
		"""Abort if pitch is not available"""
		if (self.pitch_enabled == False or self._timer == None):
			return true
		else:
		
		time_left = 0.0
		directional_speed = 0.0
		elapsed_time = 999.0
		
		"""Get the timer value since we started moving."""
		elapsed_time = self._timer.Get()
		
		"""Calculate the time left to move."""
		time_left = time - elapsed_time
		
		if self.encoder_enabled == True:
			"""Check the encoder position against the boundaries if 
			boundaries enabled. Check Max Limit."""
			
			if self._ignore_encoder_limits == False and self._encoder_max_limit > 0 and direction == common.Direction.DOWN:
				self._pitch_controller.Set(0,0)
				self._timer.stop()
				return True
			else:
			
			"""Check Min Limit"""
			if self._ignore_encoder_limits == False and self._encoder_min_limit > 0 and direction == common.Direction.UP:
				self._pitch_controller.Set(0,0)
				self._timer.stop()
				return True
			else:
		else:
		
		"""Check to see if we've reached the proper height."""
		if ((time_left < self._time_threshold) or (time_left < 0)):
			self._pitch_controller.Set(0,0)
			self._timer.stop()
			return True
		else:
		"""Continue moving"""
			if direction == common.Direction.UP:
				directional_speed = self._pitch_up_direction
			else:
				directional_speed = self._pitch_down_direction
		
			if time_left > self._auto_far_time_threshold:
				directional_speed = directional_speed * speed * self._auto_far_time_threshold
			else if time_left > self._auto_medium_time_threshold:
				directional_speed = directional_speed * speed * self._auto_medium_time_threshold
			else:
			    directional_speed = directional_speed * speed * self._auto_near_speed_ratio
	        
			self._pitch_controller.Set(directional_speed, 0)
			return False
			
	def set_pitch_angle(self, angle, speed):
    """Sets the shooter pitch to an angle provided by the argument
	
	param:  angle-> desired angle in degrees
	        speed-> motor speed ratio
			return-> ture when the desired angle is reached
	"""
		"""Abort if the pitch control or encoder are not available."""
		if not self.encoder_enabled or not self.pitch_enabled:
			return True
			
		"""Movement direction/speed"""
		movement_direction = 0.0
		
		"""Convert angle to encoder position"""
		encoder_count = floor((self._angle_linear_fit_gradient* angle) + self.angle_linear_fit_constant)
		
		"""Check the encoder position against the boundaries if boundaries enabled.
		Check Max Limit"""
		
		if (not self.ignore_encoder_limits and self._encoder_max_limit > 0 and (encoder_count > self._encoder_count):
			if self._encoder_count > self._encoder_max_limit:
				self._pitch_controller.Set(0,0)
				return True
			else:
		else:
		
		"""Check Min Limit"""
		if (not self.ignore_encoder_limits and self._encoder_min_limit > 0 and (encoder_count > self._encoder_count):
			if self._encoder_count > self._encoder_min_limit:
				self._pitch_controller.Set(0,0)
				return True
			else:
		else:	
		
		"""Check to see if we've reached the proper height"""
		if (abs(encoder_count - self._encoder_count) <= self._encoder_threshold):
			self._pitch_controller.Set(0,0)
			return True
		
		
		"""Continue moving"""
		else:
			"""Calculate the direction needed to move, and turn into a speed"""
			if(encoder_count - self._encoder_count) > 0:
				if (abs(encoder_count - self._encoder_count) > self._auto_far_encoder_threshold):
					movement_direction = self._pitch_down_direction * speed * self._auto_far_speed_ratio
				else if (abs(encoder_count - self._encoder_count) > self._auto_medium_encoder_threshold):
					movement_direction = self._pitch_down_direction * speed * self._auto_medium_speed_ratio
				else:
					movement_direction = self._pitch_down_direction * speed * self._auto_near_speed_ratio
			else:
				if (abs(encoder_count - self._encoder_count) > self._auto_far_encoder_threshold):
					movement_direction = self._pitch_up_direction * speed * self._auto_far_speed_ratio
				else if (abs(encoder_count - self._encoder_count) > self._auto_medium_encoder_threshold):
					movement_direction = self._pitch_up_direction * speed * self._auto_medium_speed_ratio
				else:
					movement_direction = self._pitch_up_direction * speed * self._auto_near_speed_ratio
			
			"""Move"""
			self._pitch_controller.Set(movement_direction,0)
			return False
	
	def move_pitch(self, directional_speed, turbo):
	"""Move the shooter pitch until commanded otherwise
     
    param: directional_speed->the speed and direction to move the pitch
           turbo-> true if the pitch should move at 'turbo' speed.
    """
	
	    """Abort if pitch control not available"""
	    if not self.pitch_enabled:
		    return
			
		"""Apply the controls inverion to hte requested movement"""
		directional_speed = directional_speed * self._invert_multiplier
		
		"""Set the encoder counting to match movement direction"""
		if self.encoder_enabled:
		    """Check the encoder position against the boundaries if boundaries enabled.
			Check Max Limit"""
			if (not self._ignore_encoder_limits and self._encoder_max_limit > 0 and (directional_speed * self._pitch_down_direction) > 0:
			    if self._encoder_count > self._encoder_max_limit:
					directional_speed = 0.0;
				else:
			else:
			
			"""Check Min Limit"""
			if (not self._ignore_encoder_limits and self._encoder_min_limit > 0 and (directional_speed * self._pitch_up_direction) > 0:
			    if self._encoder_count < self._encoder_min_limit:
					directional_speed = 0.0
				else:
			else:
		else:

		if turbo:
			directional_speed = directional_speed * self._pitch_turbo_speed_ratio
		else:
			directional_speed = directional_speed * self._pitch_normal_speed_ratio
		
		"""Set the controller speed"""
		self._pitch_controller.Set(directional_speed, 0)
		
			
	def pitch_clear_for_climbing(self)
	"""Checks to see if the pitch fulcrum is far enough back to use the winch.
	
	return-> true when the fulcrum is clear, or if the encoder is not present
	"""
	
		if self._encoder_enabled:
		    """Check the encoder position agains the location when it is clear 
			for the winch"""
			if self._encoder_count > self._fulcrum_clear_encoder_count:
				return True
			else:
				return False
		else:
			return True
	
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
		