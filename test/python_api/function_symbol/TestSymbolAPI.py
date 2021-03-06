"""
Test newly added SBSymbol and SBAddress APIs.
"""

from __future__ import print_function

import lldb_shared

import os, time
import re
import lldb, lldbutil
from lldbtest import *

class SymbolAPITestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    def setUp(self):
        # Call super's setUp().
        TestBase.setUp(self)
        # Find the line number to of function 'c'.
        self.line1 = line_number('main.c', '// Find the line number for breakpoint 1 here.')
        self.line2 = line_number('main.c', '// Find the line number for breakpoint 2 here.')

    @add_test_categories(['pyapi'])
    @expectedFailureWindows("llvm.org/pr24778")
    def test(self):
        """Exercise some SBSymbol and SBAddress APIs."""
        self.build()
        exe = os.path.join(os.getcwd(), "a.out")

        # Create a target by the debugger.
        target = self.dbg.CreateTarget(exe)
        self.assertTrue(target, VALID_TARGET)

        # Now create the two breakpoints inside function 'a'.
        breakpoint1 = target.BreakpointCreateByLocation('main.c', self.line1)
        breakpoint2 = target.BreakpointCreateByLocation('main.c', self.line2)
        #print("breakpoint1:", breakpoint1)
        #print("breakpoint2:", breakpoint2)
        self.assertTrue(breakpoint1 and
                        breakpoint1.GetNumLocations() == 1,
                        VALID_BREAKPOINT)
        self.assertTrue(breakpoint2 and
                        breakpoint2.GetNumLocations() == 1,
                        VALID_BREAKPOINT)

        # Now launch the process, and do not stop at entry point.
        process = target.LaunchSimple (None, None, self.get_process_working_directory())
        self.assertTrue(process, PROCESS_IS_VALID)

        # Frame #0 should be on self.line1.
        self.assertTrue(process.GetState() == lldb.eStateStopped)
        thread = lldbutil.get_stopped_thread(process, lldb.eStopReasonBreakpoint)
        self.assertTrue(thread.IsValid(), "There should be a thread stopped due to breakpoint condition")
        frame0 = thread.GetFrameAtIndex(0)
        symbol_line1 = frame0.GetSymbol()
        # We should have a symbol type of code.
        self.assertTrue(symbol_line1.GetType() == lldb.eSymbolTypeCode)
        addr_line1 = symbol_line1.GetStartAddress()
        # And a section type of code, too.
        self.assertTrue(addr_line1.GetSection().GetSectionType() == lldb.eSectionTypeCode)

        # Continue the inferior, the breakpoint 2 should be hit.
        process.Continue()
        self.assertTrue(process.GetState() == lldb.eStateStopped)
        thread = lldbutil.get_stopped_thread(process, lldb.eStopReasonBreakpoint)
        self.assertTrue(thread.IsValid(), "There should be a thread stopped due to breakpoint condition")
        frame0 = thread.GetFrameAtIndex(0)
        symbol_line2 = frame0.GetSymbol()
        # We should have a symbol type of code.
        self.assertTrue(symbol_line2.GetType() == lldb.eSymbolTypeCode)
        addr_line2 = symbol_line2.GetStartAddress()
        # And a section type of code, too.
        self.assertTrue(addr_line2.GetSection().GetSectionType() == lldb.eSectionTypeCode)

        # Now verify that both addresses point to the same module.
        if self.TraceOn():
            print("UUID:", addr_line1.GetModule().GetUUIDString())
        self.assertTrue(addr_line1.GetModule().GetUUIDString() == addr_line2.GetModule().GetUUIDString())
