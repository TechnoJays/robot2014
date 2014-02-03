"""This module tests the autoscript module.

    Packages(s) required:
    - pytest

"""

# Imports
import pytest

import sys,os
sys.path.append(os.path.realpath('src'))
import autoscript


class TestAutoScriptCommand:
    """Test the AutoScriptCommand class."""

    def setup_method(self, method):
        """Setup each test."""
        pass

    def test_full_constructor(self):
        d = "command"
        p = ['name', 'val', 'val2']
        c = autoscript.AutoScriptCommand(d, p)
        assert c.command == d
        assert c.parameters == p

class TestAutoScript:
    """Test the AutoScript class."""

    def setup_method(self, method):
        """Setup each test."""
        pass

    def test_init_no_file(self):
        a = autoscript.AutoScript()
        assert a._commands == None
        assert a._command_iterator == None

    def test_init_with_valid_file(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        assert a._commands != None
        assert len(a._commands) > 0
        assert a._command_iterator != None

    def test_dispose(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        a.dispose()
        assert a._commands == None

    def test_parse_valid_file(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        assert a._commands != None
        assert len(a._commands) > 0
        assert a._command_iterator != None

    def test_parse_file_not_found(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test_asdfd.as'))
        assert a._commands == None
        assert a._command_iterator == None

    def test_parse_malformed_file(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test2.as'))
        assert a._commands != None
        assert len(a._commands) == 2
        assert a._command_iterator != None

    def test_get_available_scripts_no_path(self):
        a = autoscript.AutoScript()
        x = a.get_available_scripts()
        assert x == []

    def test_get_available_scripts_with_path_with_slash(self):
        a = autoscript.AutoScript()
        x = a.get_available_scripts('tests/files/')
        assert x != None
        assert len(x) > 0

    def test_get_available_scripts_with_path_no_slash(self):
        a = autoscript.AutoScript()
        x = a.get_available_scripts('tests/files')
        assert x != None
        assert len(x) > 0

    def test_get_next_command_first_command(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        c = a.get_next_command()
        assert a._commands != None
        assert len(a._commands) > 0
        assert a._command_iterator != None
        assert c != None

    def test_get_next_command_second_command(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        c1 = a.get_next_command()
        c2 = a.get_next_command()
        assert a._commands != None
        assert len(a._commands) > 0
        assert a._command_iterator != None
        assert c1 != None
        assert c2 != None

    def test_get_next_command_none_left(self):
        a = autoscript.AutoScript(os.path.realpath('tests/files/test1.as'))
        c1 = a.get_next_command()
        c2 = a.get_next_command()
        c3 = a.get_next_command()
        c4 = a.get_next_command()
        assert a._commands != None
        assert len(a._commands) > 0
        assert a._command_iterator != None
        assert c1 != None
        assert c2 != None
        assert c3 != None
        assert c4 == None

