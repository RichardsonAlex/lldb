"""Test that we are able to evaluate expressions when the inferior is blocked in a syscall"""

from __future__ import print_function

import lldb_shared

import os
import lldb
from lldbtest import *
import lldbutil


class ExprSyscallTestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    @expectedFailureWindows("llvm.org/pr21765") # Also getpid() is not a function on Windows anyway
    def test_setpgid(self):
        self.build()
        self.expr_syscall()

    def expr_syscall(self):
        exe = os.path.join(os.getcwd(), 'a.out')

        # Create a target by the debugger.
        target = self.dbg.CreateTarget(exe)
        self.assertTrue(target, VALID_TARGET)

        listener = lldb.SBListener("my listener")

        # launch the inferior and don't wait for it to stop
        self.dbg.SetAsync(True)
        error = lldb.SBError()
        process = target.Launch (listener,
                None,      # argv
                None,      # envp
                None,      # stdin_path
                None,      # stdout_path
                None,      # stderr_path
                None,      # working directory
                0,         # launch flags
                False,     # Stop at entry
                error)     # error

        self.assertTrue(process and process.IsValid(), PROCESS_IS_VALID)

        event = lldb.SBEvent()

        # Give the child enough time to reach the syscall,
        # while clearing out all the pending events.
        # The last WaitForEvent call will time out after 2 seconds.
        while listener.WaitForEvent(2, event):
            pass

        # now the process should be running (blocked in the syscall)
        self.assertEqual(process.GetState(), lldb.eStateRunning, "Process is running")

        # send the process a signal
        process.SendAsyncInterrupt()
        while listener.WaitForEvent(2, event):
            pass

        # as a result the process should stop
        # in all likelihood we have stopped in the middle of the sleep() syscall
        self.assertEqual(process.GetState(), lldb.eStateStopped, PROCESS_STOPPED)
        thread = process.GetSelectedThread()

        # try evaluating a couple of expressions in this state
        self.expect("expr release_flag = 1", substrs = [" = 1"])
        self.expect("print (int)getpid()", substrs = [str(process.GetProcessID())])

        # and run the process to completion
        process.Continue()

        # process all events
        while listener.WaitForEvent(10, event):
            new_state = lldb.SBProcess.GetStateFromEvent(event)
            if new_state == lldb.eStateExited:
                break

        self.assertEqual(process.GetState(), lldb.eStateExited)
        self.assertEqual(process.GetExitStatus(), 0)
