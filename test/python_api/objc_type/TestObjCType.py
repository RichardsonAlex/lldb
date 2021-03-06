"""
Test SBType for ObjC classes.
"""

from __future__ import print_function

import lldb_shared

import os, time
import re
import lldb, lldbutil
from lldbtest import *

class ObjCSBTypeTestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    def setUp(self):
        # Call super's setUp().
        TestBase.setUp(self)
        self.line = line_number("main.m", '// Break at this line')

    @skipUnlessDarwin
    @add_test_categories(['pyapi'])
    def test(self):
        """Test SBType for ObjC classes."""
        self.build()
        exe = os.path.join(os.getcwd(), "a.out")

        # Create a target by the debugger.
        target = self.dbg.CreateTarget(exe)
        self.assertTrue(target, VALID_TARGET)

        # Create the breakpoint inside function 'main'.
        breakpoint = target.BreakpointCreateByLocation("main.m", self.line)
        self.assertTrue(breakpoint, VALID_BREAKPOINT)

        # Now launch the process, and do not stop at entry point.
        process = target.LaunchSimple (None, None, self.get_process_working_directory())
        self.assertTrue(process, PROCESS_IS_VALID)



        # Get Frame #0.
        self.assertTrue(process.GetState() == lldb.eStateStopped)
        thread = lldbutil.get_stopped_thread(process, lldb.eStopReasonBreakpoint)
        self.assertTrue(thread.IsValid(), "There should be a thread stopped due to breakpoint condition")

        aBar = self.frame().FindVariable("aBar")
        aBarType = aBar.GetType()
        self.assertTrue(aBarType.IsValid(), "Bar should be a valid data type")
        self.assertTrue(aBarType.GetName() == "Bar *", "Bar has the right name")

        self.assertTrue(aBarType.GetNumberOfDirectBaseClasses() == 1, "Bar has a superclass")
        aFooType = aBarType.GetDirectBaseClassAtIndex(0)

        self.assertTrue(aFooType.IsValid(), "Foo should be a valid data type")
        self.assertTrue(aFooType.GetName() == "Foo", "Foo has the right name")

        self.assertTrue(aBarType.GetNumberOfFields() == 1, "Bar has a field")
        aBarField = aBarType.GetFieldAtIndex(0)

        self.assertTrue(aBarField.GetName() == "_iVar", "The field has the right name")
