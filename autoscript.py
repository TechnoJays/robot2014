"""This module provides a class to read autoscript files."""

# Imports

class AutoScriptCommand(object):
    """Object that stores the information for an autoscript command.

    Attributes:
        command: the autonomous command.
        parameters: the List of parameters for the command.

    """
    # Public member variables
    command = None
    parameters = None

    def __init__(self, c, p):
        """Create and initialize an AutoScriptCommand.

        Args:
            c: the autonomous command.
            p: the List of parameters for the command.

        """

class AutoScript(object):
    """Reads autonomous robot sequences from a file into memory.

    Provides a simple interface to read specific name/value pairs
    from a file.

    Attributes:
        file_opened: True if an autoscript file is currently open.

    """
    # Public member variables
    file_opened = False

    # Private member objects
    #TODO

    # Private member variables
    #TODO

    def __init__(self, path_and_file):
        """Create and initialize an AutoScript object with a specified file.

        Instantiate a AutoScript object and open a specified script file.

        Args:
            path_and_file: the path and filename of the autoscript file.

        """
        #TODO

    def dispose(self):
        """Dispose of an AutoScript object.

        Dispose of an AutoScript object when it is no longer required by closing
        the open file if it exists, and removing references to any internal
        objects.

        """
        #TODO

    def open(self, path_and_file):
        """Open a script file for reading.

        Args:
            path_and_file: the path and filename of the autoscript file.

        Returns:
            True if successful.

        """
        #TODO

    def close(self):
        """Close the autoscript file."""
        #TODO

    def read_script(self):
        """Read all autoscript commands from the file.

        Reads the entire autoscript file formatted as a comma separated value
        (CSV) file.  The commands are stored as objects in a List.

        Returns:
            True if successful.

        """
        #TODO

    def get_available_scripts(self):
        """Get a list of autoscript files in the current directory.

        Returns:
            A List of AutoScript filenames.

        """
        #TODO

    def get_next_command(self):
        """Get the next AutoScript command.

        Returns:
            The next AutoScriptCommand from the file.

        """
        #TODO

    def get_command(self, command_index):
        """Get the specified AutoScript command.

        Args:
            command_index: the index of the command.

        Returns:
            The specified AutoScriptCommand.

        """
        #TODO

