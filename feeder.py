# Imports
import wpilib
import common
import datalog
import parameters

## Class desc
class Feeder(object):
    # Public member variables
    feeder_enabled = False
    compressor_enabled = False
    solenoid_enabled = False

    # Private member objects
    compressor_ = None
    log_ = None
    parameters_ = None
    piston_ = None

    # Private member variables
    log_enabled_ = False
    parameters_file_ = None
    robot_state_ = ProgramState.disabled

    ## Short method description
    #
    #  Long description
    #
    def __init__(self):
        self.initialize("feeder.par", False)

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def __init__(self, logging_enabled):
        self.initialize("feeder.par", logging_enabled)

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def __init__(self, parameters):
        self.initialize(parameters, False)

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def __init__(self, parameters, logging_enabled):
        self.initialize(parameters, logging_enabled)

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def dispose(self):
        if self.log_:
            self.log_.close()
        self.log_ = None
        self.parameters_ = None
        self.compressor_ = None
        self.piston_ = None
        return

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def initialize(self, parameters, logging_enabled):
        # Initialize public member variables
        self.feeder_enabled = False
        self.compressor_enabled = False
        self.solenoid_enabled = False

        # Initialize private member objects
        self.log_ = None
        self.parameters_ = None
        self.compressor_ = None
        self.piston_ = None

        # Initialize private parameters

        # Initialize private member variables
        self.log_enabled_ = False
        self.robot_state_ = ProgramState.disabled

        # Create a new data log object
        self.log_ = DataLog("feeder.log")

        # Enable logging if specified
        if self.log_ and self.log_.file_opened:
            self.log_enabled_ = logging_enabled
        else:
            self.log_enabled_ = False

        # Read parameters file
        self.parameters_file_ = parameters
        self.load_parameters()

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def load_parameters(self):
        # Define and initialize local variables
        pressure_switch_channel = -1
        compressor_relay_channel = -1
        solenoid_channel = -1
        parameters_read = False

        # Close and delete old objects
        self.parameters_ = None
        self.compressor_ = None
        self.piston_ = None

        # Read the parameters file
        self.parameters_ = Parameters(self.parameters_file_)
        if self.parameters_ and self.parameters_.file_opened:
            parameters_read = self.parameters_.read_values()
            self.parameters_.close()

        if self.log_enabled_:
            if parameters_read:
                self.log_.write_line("Feeder parameters loaded successfully")
            else:
                self.log_.write_line("Failed to read Feeder parameters")

        if parameters_read:
            pressure_switch_channel = self.parameters_.get_value("PRESSURE_SWITCH_CHANNEL")
            compressor_relay_channel = self.parameters_.get_value("COMPRESSOR_RELAY_CHANNEL")
            solenoid_channel = self.parameters_.get_value("SOLENOID_CHANNEL")

        self.compressor_enabled = False
        if pressure_switch_channel > 0 and compressor_relay_channel > 0:
            self.compressor_ = wpilib.Compressor(pressure_switch_channel, compressor_relay_channel)
            if self.compressor_:
                self.compressor_enabled = True

        self.piston_enabled = False
        if solenoid_channel > 0:
            self.piston_ = wpilib.Solenoid(solenoid_channel)
            if self.piston_:
                self.piston_enabled = True

        if self.compressor_enabled and self.solenoid_enabled:
            self.feeder_enabled = True
        else:
            self.feeder_enabled = False

        if self.log_enabled_:
            if self.compressor_enabled:
                self.log_.write_line("Compressor enabled")
            else:
                self.log_.write_line("Compressor disabled")
            if self.solenoid_enabled:
                self.log_.write_line("Solenoid enabled")
            else:
                self.log_.write_line("Solenoid disabled")
            if self.feeder_enabled:
                self.log_.write_line("Feeder enabled")
            else:
                self.log_.write_line("Feeder disabled")

        return parameters_read

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def set_robot_state(self, state):
        self.robot_state_ = state

        # Make sure the compressor is running in every state
        if self.compressor_enabled_:
            if not self.compressor_.Enabled():
                self.compressor_.Start()

        if state == ProgramState.disabled:
            pass
        if state == ProgramState.teleop:
            pass
        if state == ProgramState.autonomous:
            pass

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def set_log_state(self, state):
        if state and self.log_:
            self.log_enabled_ = True
        else:
            self.log_enabled_ = False

    ## Short method description
    #
    #  Long description
    #
    # @param param Param description
    def set_piston(self, state):
        if self.feeder_enabled_ and self.solenoid_enabled_:
            self.piston_.Set(state)

