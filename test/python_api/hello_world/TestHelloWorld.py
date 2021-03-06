"""Test Python APIs for target (launch and attach), breakpoint, and process."""

from __future__ import print_function

import lldb_shared

import os, sys, time
import lldb
import time
from lldbtest import *

class HelloWorldTestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)
    
    def setUp(self):
        # Call super's setUp().
        TestBase.setUp(self)
        # Get the full path to our executable to be attached/debugged.
        self.exe = os.path.join(os.getcwd(), self.testMethodName)
        self.d = {'EXE': self.testMethodName}
        # Find a couple of the line numbers within main.c.
        self.line1 = line_number('main.c', '// Set break point at this line.')
        self.line2 = line_number('main.c', '// Waiting to be attached...')

    def tearDown(self):
        # Destroy process before TestBase.tearDown()
        self.dbg.GetSelectedTarget().GetProcess().Destroy()
        # Call super's tearDown().
        TestBase.tearDown(self)

    @add_test_categories(['pyapi'])
    def test_with_process_launch_api(self):
        """Create target, breakpoint, launch a process, and then kill it."""
        self.build(dictionary=self.d)
        self.setTearDownCleanup(dictionary=self.d)
        target = self.dbg.CreateTarget(self.exe)

        breakpoint = target.BreakpointCreateByLocation("main.c", self.line1)

        # The default state after breakpoint creation should be enabled.
        self.assertTrue(breakpoint.IsEnabled(),
                        "Breakpoint should be enabled after creation")

        breakpoint.SetEnabled(False)
        self.assertTrue(not breakpoint.IsEnabled(),
                        "Breakpoint.SetEnabled(False) works")

        breakpoint.SetEnabled(True)
        self.assertTrue(breakpoint.IsEnabled(),
                        "Breakpoint.SetEnabled(True) works")

        # rdar://problem/8364687
        # SBTarget.Launch() issue (or is there some race condition)?

        process = target.LaunchSimple (None, None, self.get_process_working_directory())
        # The following isn't needed anymore, rdar://8364687 is fixed.
        #
        # Apply some dances after LaunchProcess() in order to break at "main".
        # It only works sometimes.
        #self.breakAfterLaunch(process, "main")

        process = target.GetProcess()
        self.assertTrue(process, PROCESS_IS_VALID)

        thread = process.GetThreadAtIndex(0)
        if thread.GetStopReason() != lldb.eStopReasonBreakpoint:
            from lldbutil import stop_reason_to_str
            self.fail(STOPPED_DUE_TO_BREAKPOINT_WITH_STOP_REASON_AS %
                      stop_reason_to_str(thread.GetStopReason()))

        # The breakpoint should have a hit count of 1.
        self.assertTrue(breakpoint.GetHitCount() == 1, BREAKPOINT_HIT_ONCE)

    @add_test_categories(['pyapi'])
    @expectedFailurei386 # llvm.org/pr17384: lldb needs to be aware of linux-vdso.so to unwind stacks properly
    @expectedFailureWindows("llvm.org/pr24600")
    def test_with_attach_to_process_with_id_api(self):
        """Create target, spawn a process, and attach to it with process id."""
        self.build(dictionary=self.d)
        self.setTearDownCleanup(dictionary=self.d)
        target = self.dbg.CreateTarget(self.exe)

        # Spawn a new process
        popen = self.spawnSubprocess(self.exe, ["abc", "xyz"])
        self.addTearDownHook(self.cleanupSubprocesses)

        # Give the subprocess time to start and wait for user input
        time.sleep(0.25)

        listener = lldb.SBListener("my.attach.listener")
        error = lldb.SBError()
        process = target.AttachToProcessWithID(listener, popen.pid, error)

        self.assertTrue(error.Success() and process, PROCESS_IS_VALID)

        # Let's check the stack traces of the attached process.
        import lldbutil
        stacktraces = lldbutil.print_stacktraces(process, string_buffer=True)
        self.expect(stacktraces, exe=False,
            substrs = ['main.c:%d' % self.line2,
                       '(int)argc=3'])

    @add_test_categories(['pyapi'])
    @expectedFailurei386 # llvm.org/pr17384: lldb needs to be aware of linux-vdso.so to unwind stacks properly
    @expectedFailureWindows("llvm.org/pr24600")
    def test_with_attach_to_process_with_name_api(self):
        """Create target, spawn a process, and attach to it with process name."""
        self.build(dictionary=self.d)
        self.setTearDownCleanup(dictionary=self.d)
        target = self.dbg.CreateTarget(self.exe)

        # Spawn a new process
        popen = self.spawnSubprocess(self.exe, ["abc", "xyz"])
        self.addTearDownHook(self.cleanupSubprocesses)

        # Give the subprocess time to start and wait for user input
        time.sleep(0.25)

        listener = lldb.SBListener("my.attach.listener")
        error = lldb.SBError()
        # Pass 'False' since we don't want to wait for new instance of "hello_world" to be launched.
        name = os.path.basename(self.exe)

        # While we're at it, make sure that passing a None as the process name
        # does not hang LLDB.
        target.AttachToProcessWithName(listener, None, False, error)
        # Also boundary condition test ConnectRemote(), too.
        target.ConnectRemote(listener, None, None, error)

        process = target.AttachToProcessWithName(listener, name, False, error)

        self.assertTrue(error.Success() and process, PROCESS_IS_VALID)

        # Verify that after attach, our selected target indeed matches name.
        self.expect(self.dbg.GetSelectedTarget().GetExecutable().GetFilename(), exe=False,
            startstr = name)

        # Let's check the stack traces of the attached process.
        import lldbutil
        stacktraces = lldbutil.print_stacktraces(process, string_buffer=True)
        self.expect(stacktraces, exe=False,
            substrs = ['main.c:%d' % self.line2,
                       '(int)argc=3'])
