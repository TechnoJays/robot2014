"""DataLog writes log messages to a text file."""

#Imports 

import wpilib
import os



class DataLog(object):
	"""Log robot code to a text file. 

	This code opens, deletes, closes and writes to files. 
	
    Attributes: 
		file_opened: If true, text file is open. If false, text 
					 file is closed.
		_fo: The file opened.
		_file_name: Name of the file
		_mode: Access Mode of write function (e.g. "w", "a+",...)
		_line: Line of text to record in data log text file.
		_timestamp: If true, record time stamp before string (line,
					parameter, value). If false, don't record time-
					stamp.
		_parameter: Name of parameter (corresponding to value)
		_value: The value (corresponding to parameter)

    """
	# Public member variables
	file_opened = None
    
    # Private member objects
    _fo = None

    # Private member variables
	_file_name = None
	_mode = None
	_line = None
	_timestamp = None
	_parameter = None
	_value = None
	_get_msec_time =(wpilib.time.GetFPGATimestamp()/1000)
	
	
	def __init__(self, file_name="datalog.txt", mode="w"):
		"""Initialize data log"""
		
		# Initialize public member variables
		self.file_opened = False
		
		# Private member objects
		self._fo = None
		
		# Initialize private member variables
		self._file_name = file_name
		self._mode = mode
		self._line = None
		self._timestamp = False
		self._parameter = None
		self._value = None
		self._get_msec_time =(wiblib.time.GetFPGATimestamp()/1000)
		
		self._open(mode)
		
	def _open(self, mode):
		"""Opens a file according to user defined access mode.
		
		Access Mode:
		http://www.tutorialspoint.com/python/python_files_io.htm
	
		Set file_opened to True
		
		"""
		self._mode = mode
		self._fo = open(self.file_name, self.mode)
		self.file_opened = not self._fo.closed
		
		
	def delete(self):
		"""Deletes file"""
		
		os.remove(self._file_name)
		
		
	def close(self):
		"""Closes file
		
		Checks if file is created and file is opened, before 
		closing the file and flags the file is closed. 
		
		"""
		if self._file_name = None and self.file_opened == True:
			self._fo.close()
			self.file_opened = False
		else:
			print ("Close File Error: No file opened.")
			
			
		
	def write_line(self, line, timestamp):
		"""Writes a line of text 
		
		Captures line of text followed by a Carriage Return ("\n")
		if timestamp is True add Timestamp before line of text
		"""
		self._line = str(line)
		if timestamp == True:
			self._time = str(self._get_msec_time)
			self._fo.write("%s", %(self._time))
		else:
		self._fo.write("   %s/n", %(self._line))
		
	def write_value(self, parameter, value, timestamp):
		"""Writes the parameter and value to the open text file
		
		if timestamp is True add Timestamp before line of text
		"""
		
		self._parameter = str(parameter)
		self._value = str(value)
		if timestamp == True:
			self._time = str(self._get_msec_time)
			self._fo.write("%s", %(self._time))
		else:
		self._fo.write("   %s = %s/n" %(self._parameter, self.value))
	
	
		
		
		
		
	
		
		
		
		
		
		
	
	