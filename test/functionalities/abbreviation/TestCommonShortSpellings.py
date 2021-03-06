"""
Test some lldb command abbreviations to make sure the common short spellings of
many commands remain available even after we add/delete commands in the future.
"""

from __future__ import print_function

import lldb_shared

import os, time
import lldb
from lldbtest import *
import lldbutil

class CommonShortSpellingsTestCase(TestBase):
    
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_abbrevs2 (self):
        command_interpreter = self.dbg.GetCommandInterpreter()
        self.assertTrue(command_interpreter, VALID_COMMAND_INTERPRETER)
        result = lldb.SBCommandReturnObject()

        abbrevs = [
            ('br s', 'breakpoint set'),
            ('disp', '_regexp-display'),  # a.k.a., 'display'
            ('di', 'disassemble'),
            ('dis', 'disassemble'),
            ('ta st a', 'target stop-hook add'),
            ('fr v', 'frame variable'),
            ('ta st li', 'target stop-hook list'),
        ]

        for (short_val, long_val) in abbrevs:
            command_interpreter.ResolveCommand(short_val, result)
            self.assertTrue(result.Succeeded())
            self.assertEqual(long_val, result.GetOutput())
